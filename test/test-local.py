import os
import boto3
from botocore.exceptions import ClientError

# Load credentials from environment variables or use dummy defaults
access_key = os.getenv("AWS_ACCESS_KEY_ID", "dummy_access_key")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "dummy_secret_key")
region = os.getenv("AWS_REGION", "us-east-1")
bucket = os.getenv("S3_BUCKET_NAME", "dummy_bucket")
key = "Generated_Emission_Data_Monthly.csv"

s3 = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region,
)

try:
    s3.head_object(Bucket=bucket, Key=key)
    print("✅ File exists and credentials are valid.")

    obj = s3.get_object(Bucket=bucket, Key=key)
    print("✅ Able to read object.")
    print("📦 Size:", obj['ContentLength'])

except ClientError as e:
    print("❌ Error:", e.response['Error']['Message'])
