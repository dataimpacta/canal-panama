import os
from io import StringIO

import boto3
import pandas as pd
from botocore.exceptions import ClientError

# Bucket and file name for the form submissions
FORM_BUCKET = os.getenv("FORM_BUCKET_NAME") or os.getenv("form_bucket_name")
FORM_FILE = os.getenv("FORM_FILE_NAME") or os.getenv("form_file_name")

# Initialize S3 client using environment credentials/role
s3_client = boto3.client("s3")


def append_submission(name: str, country: str, purpose: str, email: str) -> None:
    """Append a submission record to the S3 CSV file.

    If the object does not exist it will be created with the proper headers.
    If required environment variables are missing, the function does nothing.
    """
    if not FORM_BUCKET or not FORM_FILE:
        # Missing configuration, do nothing
        return

    try:
        obj = s3_client.get_object(Bucket=FORM_BUCKET, Key=FORM_FILE)
        existing = obj["Body"].read().decode("utf-8")
        df = pd.read_csv(StringIO(existing))
    except ClientError as exc:  # File may not exist yet
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "NoSuchKey":
            df = pd.DataFrame(columns=["Name", "Country", "Purpose", "Email"])
        else:
            raise

    new_row = {
        "Name": name or "",
        "Country": country or "",
        "Purpose": purpose or "",
        "Email": email or "",
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_client.put_object(Bucket=FORM_BUCKET, Key=FORM_FILE, Body=csv_buffer.getvalue())
