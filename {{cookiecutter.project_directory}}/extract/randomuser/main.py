from dataclasses import dataclass
from pathlib import Path
import tempfile
import time

import jsonlines
from randomuser import RandomUser


@dataclass
class Args:
    user_qtd: int
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
    users = generate_users(args.user_qtd)
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


def generate_users(qtd: int) -> list[dict[str,str]]:
    users = []
    for ru in RandomUser.generate_users(qtd):
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
