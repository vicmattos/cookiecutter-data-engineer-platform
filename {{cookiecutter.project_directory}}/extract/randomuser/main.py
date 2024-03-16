from dataclasses import dataclass
import os
from pathlib import Path
import tempfile
import time

import boto3
from dotenv import load_dotenv
import jsonlines
from randomuser import RandomUser


@dataclass
class Args:
    user_qty: int
    bucket_name: str
    obj_prefix: Path

def main(s3_client, args: Args) -> str:
    # Clean args
    args.obj_prefix = _clean_obj_prefix(args.obj_prefix)
    # Create Constants
    FILE_NAME: str = f'{int(time.time())}_users.jsonl'
    TEMP_FILE: Path = Path(tempfile.mkdtemp(), FILE_NAME)
    S3_OBJ_KEY: Path = Path(args.obj_prefix, FILE_NAME)
    # Create local file with random users
    users = generate_users(args.user_qty)
    create_file(TEMP_FILE, users)
    # Upload file to object store
    s3_client.upload_file(
        Filename=TEMP_FILE,
        Bucket=args.bucket_name,
        Key=str(S3_OBJ_KEY),
    )
    # Return object S3 URI
    obj_uri = Path(args.bucket_name, S3_OBJ_KEY)
    return 's3://' + str(obj_uri)


def generate_users(qty: int) -> list[dict[str,str]]:
    users = []
    for ru in RandomUser.generate_users(qty):
        users.append({
            "full_name": ru.get_full_name(),
            "date_of_birth": ru.get_dob(),
            "email": ru.get_email(),
        })
    return users


def _clean_obj_prefix(obj_prefix: Path) -> Path:
    if '/' in obj_prefix.parts:
        return Path(*obj_prefix.parts[1:])
    return obj_prefix


def create_file(file_path: Path, users: list[dict[str,str]]) -> None:
    with jsonlines.open(file_path, mode='w') as writer:
        writer.write_all(users)


if __name__ == "__main__":
    load_dotenv()

    ENDPOINT_URL = os.getenv("ENDPOINT_URL")
    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    APP_USERS_QTY = int(os.getenv("APP_USERS_QTY", 10))
    APP_BUCKET_NAME = os.getenv("APP_BUCKET_NAME")
    APP_OBJ_PREFIX = Path(os.getenv("APP_OBJ_PREFIX"))

    if ENDPOINT_URL:
        client = boto3.client('s3',
            endpoint_url=ENDPOINT_URL,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )
    elif ACCESS_KEY and SECRET_KEY:
        client = boto3.client('s3',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )
    else:
        client = boto3.client('s3')

    args = Args(
        user_qty = APP_USERS_QTY,
        bucket_name = APP_BUCKET_NAME,
        obj_prefix = APP_OBJ_PREFIX,
    )

    print(main(client, args))
