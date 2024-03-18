import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from typing import TypeVar

import s3fs
from dotenv import load_dotenv
from randomuser import RandomUser

UserGen = TypeVar("UserGen", bound=Iterator[dict[str, str]])
S3File = TypeVar("S3File", bound=s3fs.core.S3FileSystem)


@dataclass
class MainArgs:
    s3: S3File
    user_qty: int
    bucket_name: str
    obj_prefix: Path

    def __post_init__(self):
        if "/" in self.obj_prefix.parts:
            self.obj_prefix = Path(*self.obj_prefix.parts[1:])


def main(args: MainArgs) -> str:
    # Create Constants
    FILE_NAME: str = f"{int(time.time())}_users.jsonl"
    S3_OBJ_URI: Path = Path(args.bucket_name, args.obj_prefix, FILE_NAME)
    # Create random users generator
    user_generator = generate_users(args.user_qty)
    # Upload data to object store
    upload_users(args.s3, S3_OBJ_URI, user_generator)
    # Return object S3 URI
    return "s3://" + str(S3_OBJ_URI)


def generate_users(qty: int) -> UserGen:
    for ru in RandomUser.generate_users(qty):
        yield {
            "full_name": ru.get_full_name(),
            "date_of_birth": ru.get_dob(),
            "email": ru.get_email(),
        }


def upload_users(s3: S3File, key: str, users: UserGen, encode: str = "utf-8") -> None:
    ld_user_bytes = lambda u: bytes(json.dumps(u), encode)
    with s3.open(key, "wb") as f:
        f.write(b"\n".join([ld_user_bytes(u) for u in users]))


if __name__ == "__main__":
    load_dotenv()

    ENDPOINT_URL = os.getenv("ENDPOINT_URL")
    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    APP_USERS_QTY = int(os.getenv("APP_USERS_QTY", 10))
    APP_BUCKET_NAME = os.getenv("APP_BUCKET_NAME")
    APP_OBJ_PREFIX = Path(os.getenv("APP_OBJ_PREFIX"))

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

    args = MainArgs(
        s3=client,
        user_qty=APP_USERS_QTY,
        bucket_name=APP_BUCKET_NAME,
        obj_prefix=APP_OBJ_PREFIX,
    )

    print(main(args))
