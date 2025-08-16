import os
import boto3
import botocore
import hashlib
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


def hash_email(email: str) -> str:
    """
    Hash email address for use as unique identifier.
    Returns empty string if email is None or empty.
    """
    if not email or not email.strip():
        return ""
    
    # Normalize email (lowercase, trim whitespace)
    normalized_email = email.strip().lower()
    
    # Create SHA-256 hash and return first 16 characters
    # This provides uniqueness while keeping the hash manageable
    return hashlib.sha256(normalized_email.encode('utf-8')).hexdigest()[:16]


def append_form_row(
    email: str,
    country: str,
    purpose: str,
    source: str,
    start_date: str,
    end_date: str,
    bucket: str = FORM_BUCKET,
    file: str = FORM_FILE,
) -> None:

    if not all([
        bucket,
        file,
        country,
        purpose,
        source,
        start_date,
        end_date,
    ]):
        return

    # Hash the email immediately - we never store the original
    email_hash = hash_email(email)

    submission_date = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    row = ",".join(
        [submission_date, email_hash, country, purpose, source, start_date, end_date]
    )

    try:
        obj = s3_client.get_object(Bucket=bucket, Key=file)
        data = obj["Body"].read().decode("utf-8")
    except botocore.exceptions.ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "NoSuchKey":
            data = "submission_date,email_hash,country,purpose,source,start_date,end_date\n"
        else:
            raise
    if data and not data.endswith("\n"):
        data += "\n"
    data += row + "\n"
    s3_client.put_object(Bucket=bucket, Key=file, Body=data.encode("utf-8"))
