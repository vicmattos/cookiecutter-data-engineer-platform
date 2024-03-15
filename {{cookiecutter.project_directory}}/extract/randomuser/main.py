import os
from pathlib import Path
import tempfile
import time

from dotenv import load_dotenv
import boto3
import jsonlines
from randomuser import RandomUser


# Args
load_dotenv()
APP_USERS_QTD: int = int(os.getenv("APP_USERS_QTD", 10))
APP_BUCKET_NAME: str = os.getenv("APP_BUCKET_NAME")
APP_OBJ_PREFIX: Path = Path(os.getenv("APP_OBJ_PREFIX"))
ACCESS_KEY: str = os.getenv("ACCESS_KEY")
SECRET_KEY: str = os.getenv("SECRET_KEY")
ENDPOINT_URL: str = os.getenv("ENDPOINT_URL")

FILE_NAME: str = f'{int(time.time())}_users.jsonl'
TEMP_FILE: Path = Path(tempfile.mkdtemp(), FILE_NAME)
APP_OBJ_KEY: Path = Path(APP_OBJ_PREFIX, FILE_NAME)


# Generate Data
with jsonlines.open(TEMP_FILE, mode='w') as writer:
    for u in RandomUser.generate_users(APP_USERS_QTD):
        writer.write({
            "full_name": u.get_full_name(),
            "date_of_birth": u.get_dob(),
            "email": u.get_email(),
        })


# Upload to S3
client = boto3.client('s3',
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

client.upload_file(
    Filename=TEMP_FILE,
    Bucket=APP_BUCKET_NAME,
    Key=str(APP_OBJ_KEY),
)
