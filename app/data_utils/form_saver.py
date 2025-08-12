import os
import boto3
import botocore
from dotenv import load_dotenv
from datetime import datetime
from ipaddress import ip_address, ip_network

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

def anonymize_ip(ip: str) -> str:
    try:
        ip_obj = ip_address(ip)
        if ip_obj.version == 4:
            network = ip_network(f"{ip}/24", strict=False)
        else:
            network = ip_network(f"{ip}/48", strict=False)
        return str(network.network_address)
    except ValueError:
        return ""


def append_form_row(
    anonymized_ip: str,
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
        anonymized_ip,
        country,
        purpose,
        source,
        start_date,
        end_date,
    ]):
        return

    submission_date = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    row = ",".join(
        [submission_date, anonymized_ip, country, purpose, source, start_date, end_date]
    )
    
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=file)
        data = obj["Body"].read().decode("utf-8")
    except botocore.exceptions.ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "NoSuchKey":
            data = "submission_date,anonymized_ip,country,purpose,source,start_date,end_date\n"
        else:
            raise
    if data and not data.endswith("\n"):
        data += "\n"
    data += row + "\n"
    s3_client.put_object(Bucket=bucket, Key=file, Body=data.encode("utf-8"))
