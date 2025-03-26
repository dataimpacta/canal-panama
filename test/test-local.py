import boto3
from botocore.exceptions import ClientError

# Load from .env or set directly
access_key = "AKIAUSJEUTGR5SDNBLPT"
secret_key = "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"
region = "us-east-1"
bucket = "buckect-canalpanama"
key = "Generated_Emission_Data_Monthly.csv"

s3 = boto3.client(
    "s3"
)

try:
    s3.head_object(Bucket=bucket, Key=key)
    print("✅ File exists and credentials are valid.")
    
    obj = s3.get_object(Bucket=bucket, Key=key)
    print("✅ Able to read object.")
    print("📦 Size:", obj['ContentLength'])

except ClientError as e:
    print("❌ Error:", e.response['Error']['Message'])