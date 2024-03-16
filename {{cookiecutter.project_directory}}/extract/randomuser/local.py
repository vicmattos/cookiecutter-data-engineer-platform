import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

from main import main
from main import Args


if __name__ == "__main__":
    load_dotenv()

    if os.getenv("ENDPOINT_URL"):
        client = boto3.client('s3',
            endpoint_url=os.getenv("ENDPOINT_URL"),
            aws_access_key_id=os.getenv("ACCESS_KEY"),
            aws_secret_access_key=os.getenv("SECRET_KEY"),
        )
    else:
        client = boto3.client('s3',
            aws_access_key_id=os.getenv("ACCESS_KEY"),
            aws_secret_access_key=os.getenv("SECRET_KEY"),
        )

    args = Args(
        user_qtd = int(os.getenv("APP_USERS_QTD", 10)),
        bucket_name = os.getenv("APP_BUCKET_NAME"),
        obj_prefix = Path(os.getenv("APP_OBJ_PREFIX")),
    )

    print(main(client, args))
