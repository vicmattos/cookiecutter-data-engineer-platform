import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar
from urllib.parse import urlparse

import psycopg
import s3fs
from dotenv import load_dotenv

S3Client = TypeVar("S3Client", bound=s3fs.core.S3FileSystem)


@dataclass
class DwConnArgs:
    host: str
    port: str
    user: str
    password: str
    dbname: str


@dataclass
class MainArgs:
    s3_client: S3Client
    dw_conn_args: DwConnArgs
    s3_obj_uri: str
    s3_obj_enconde: str
    dw_table: str

    def __post_init__(self):
        self.bucket_name = self.s3_obj_uri.split("://")[1].split("/")[0]
        self.s3_obj_key = Path(*Path(urlparse(self.s3_obj_uri).path).parts[1:])


def main(args: MainArgs) -> None:
    # Read users from S3
    OBJ_FULL_KEY = Path(args.bucket_name, args.s3_obj_key)
    with args.s3_client.open(OBJ_FULL_KEY, "rb") as f:
        users_str = f.read().decode(args.s3_obj_enconde)

    # Parse data
    # users = [json.loads(u) for u in users_str.splitlines()]
    users_json = "[" + users_str.replace("\n", ",") + "]"

    # Insert into DW
    with psycopg.connect(
        host=args.dw_conn_args.host,
        port=args.dw_conn_args.port,
        user=args.dw_conn_args.user,
        password=args.dw_conn_args.password,
        dbname=args.dw_conn_args.dbname,
    ) as conn:
        with conn.cursor() as cur:
            query_sql = f"""
                INSERT INTO {args.dw_table}
                SELECT * FROM json_populate_recordset(NULL::{args.dw_table}, %s)
            """
            # cur.execute(query_sql, (json.dumps(users),))
            cur.execute(query_sql, (users_json,))


if __name__ == "__main__":
    load_dotenv()

    APP_OBJ_URI = os.getenv("APP_OBJ_URI")
    APP_DW_TABLE = os.getenv("APP_DW_TABLE")
    APP_OBJ_ENCODE = os.getenv("APP_OBJ_ENCODE")

    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")

    DW_HOST = os.getenv("DW_HOST")
    DW_PORT = os.getenv("DW_PORT")
    DW_USER = os.getenv("DW_USER")
    DW_PASSWORD = os.getenv("DW_PASSWORD")
    DW_DATABASE = os.getenv("DW_DATABASE")

    # Local development exclusive
    ENDPOINT_URL = os.getenv("ENDPOINT_URL")

    # Create object store client
    if ENDPOINT_URL:
        client = s3fs.S3FileSystem(
            key=ACCESS_KEY,
            secret=SECRET_KEY,
            endpoint_url=ENDPOINT_URL,
        )
    elif ACCESS_KEY and SECRET_KEY:
        client = s3fs.S3FileSystem(
            key=ACCESS_KEY,
            secret=SECRET_KEY,
        )
    else:
        s3fs.S3FileSystem(anon=False)

    # Compose data warehouse connection args
    args = MainArgs(
        s3_client=client,
        dw_conn_args=DwConnArgs(
            host=DW_HOST,
            port=DW_PORT,
            user=DW_USER,
            password=DW_PASSWORD,
            dbname=DW_DATABASE,
        ),
        s3_obj_uri=APP_OBJ_URI,
        s3_obj_enconde=APP_OBJ_ENCODE,
        dw_table=APP_DW_TABLE,
    )

    main(args)
