import os
import boto3
import botocore
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

FORM_BUCKET = os.getenv("FORM_BUCKET_NAME")
FORM_FILE = os.getenv("FORM_FILE_NAME")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID_DATA_IMPACTA")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY_DATA_IMPACTA")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

def append_form_row(
    name: str,
    country: str,
    purpose: str,
    email: str,
    source: str,
    start_date: str,
    end_date: str,
    bucket: str = FORM_BUCKET,
    file: str = FORM_FILE,
) -> None:

    if not all([
        bucket,
        file,
        name,
        country,
        purpose,
        email,
        source,
        start_date,
        end_date,
    ]):
        return

    submitted_at = datetime.utcnow().strftime("%Y-%m-%d")
    row = ",".join(
        [submitted_at, name, country, purpose, email, source, start_date, end_date]
    )
    
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=file)
        data = obj["Body"].read().decode("utf-8")
    except botocore.exceptions.ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "NoSuchKey":
            data = "Submitted At,Name,Country,Purpose,Email,Source,Start Date,End Date\n"
        else:
            raise
    if data and not data.endswith("\n"):
        data += "\n"
    data += row + "\n"
    s3_client.put_object(Bucket=bucket, Key=file, Body=data.encode("utf-8"))
