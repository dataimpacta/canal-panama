import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
import pandas as pd
import io

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")  # Or "secrets/.env" if stored in a subfolder

# Get credentials from environment
#access_key = os.getenv("VICTOR_AWS_ACCESS_KEY_ID")
#secret_key = os.getenv("VICTOR_AWS_SECRET_ACCESS_KEY")
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

print(access_key)
print(secret_key)

bucket_name = os.getenv("victor_bucket_name")
bucket_name = os.getenv("bucket_name")


key = "dash/emissions_local_panama/emissions_local_panama_in.parquet"

# Set up S3 client with credentials
s3_client = boto3.client(
    "s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name="us-east-1"  # 👈 Optional but good to match the bucket's region
)

# Try to load and preview the Parquet file
try:
    # Check access first
    s3_client.head_object(Bucket=bucket_name, Key=key)
    print("✅ Credentials are valid and file is accessible.\n")

    # Read object
    response = s3_client.get_object(Bucket=bucket_name, Key=key)
    body = response['Body'].read()

    # Convert to DataFrame
    df = pd.read_parquet(io.BytesIO(body))

    # Show DataFrame head
    print("📄 Preview of Parquet File:")
    print(df.head())

except ClientError as e:
    print("❌ AWS Error:", e.response['Error']['Message'])
except Exception as e:
    print("❌ General Error:", str(e))