import os
import boto3
import botocore
from dotenv import load_dotenv

load_dotenv()

FORM_BUCKET = os.getenv("FORM_BUCKET_NAME")
FORM_FILE = os.getenv("FORM_FILE_NAME")

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

    if not all([bucket, file, name, country, purpose, email, source, start_date, end_date]):
    row = ",".join([name, country, purpose, email, source, start_date, end_date])
            data = "Name,Country,Purpose,Email,Source,Start Date,End Date\n"
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def append_form_row(name: str, country: str, purpose: str, email: str,
                     bucket: str = FORM_BUCKET, file: str = FORM_FILE) -> None:
    """Append a single form row to a CSV file stored in S3.

    If the CSV does not exist, it will be created with a header.
    Missing configuration or credentials will silently abort.
    """
    if not all([bucket, file, name, country, purpose, email]):
        return

    row = ",".join([name, country, purpose, email])

    try:
        obj = s3_client.get_object(Bucket=bucket, Key=file)
        data = obj["Body"].read().decode("utf-8")
    except botocore.exceptions.ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "NoSuchKey":
            data = "Name,Country,Purpose,Email\n"
        else:
            raise
    if data and not data.endswith("\n"):
        data += "\n"
    data += row + "\n"
    s3_client.put_object(Bucket=bucket, Key=file, Body=data.encode("utf-8"))
