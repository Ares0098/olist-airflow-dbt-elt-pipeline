import os
import requests
import zipfile

from dotenv import load_dotenv  
from io import BytesIO
from minio import Minio

load_dotenv()

# ----------------------
# Validate environment
# ----------------------
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = os.getenv("MINIO_BUCKET")
PREFIX = os.getenv("MINIO_PREFIX")
DATA_URL = os.getenv("DATA_URL")

assert MINIO_ENDPOINT, "Missing MINIO_ENDPOINT"
assert MINIO_ACCESS_KEY, "Missing MINIO_ACCESS_KEY"
assert MINIO_SECRET_KEY, "Missing MINIO_SECRET_KEY"
assert BUCKET_NAME, "Missing MINIO_BUCKET"
assert PREFIX, "Missing MINIO_PREFIX"

print("Config loaded:")
print(f"Endpoint: {MINIO_ENDPOINT}")
print(f"Bucket: {BUCKET_NAME}")
print(f"Prefix: {PREFIX}")

# ----------------------
# Initialize client
# ----------------------
client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# ----------------------
# Test connection
# ----------------------
try:
    buckets = client.list_buckets()
    print("Connected to MinIO. Existing buckets:", [b.name for b in buckets])
except Exception as e:
    raise Exception(f"MinIO connection failed: {e}")

# ----------------------
# Create bucket
# ----------------------
def create_bucket():
    try:
        if not client.bucket_exists(BUCKET_NAME):
            client.make_bucket(BUCKET_NAME)
            print(f"Bucket created: {BUCKET_NAME}")
        else:
            print(f"Bucket already exists: {BUCKET_NAME}")
    except Exception as e:
        raise Exception(f"Bucket creation failed: {e}")
    
# ----------------------
# Download files
# ----------------------
def download_dataset() : 

    url = DATA_URL

    print(f"Downloading dataset to in memory...")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Download failed: {e}")
        raise
    
    response_zip = response.content

    return response_zip


# ----------------------
# Upload files
# ----------------------
def extract_and_upload_files(response_zip):

    try : 
        print("Extracting dataset...")

        with zipfile.ZipFile(BytesIO(response_zip)) as z:
            for file_name in z.namelist():
                # Only CSV files
                if file_name.endswith(".csv"):
                    data = z.read(file_name)
                    print(f"Uploading dataset : {os.path.basename(file_name)}")
                    object_name = f"{PREFIX}/{os.path.basename(file_name)}"
                    client.put_object(
                        BUCKET_NAME,
                        object_name,
                        BytesIO(data),
                        length=len(data)
                    )
                    print(f"Uploaded {object_name} → bucket {BUCKET_NAME}")
    except Exception as e:
        print(f"Extraction failed: {e}")
        raise

# ----------------------
# Main
# ----------------------
if __name__ == "__main__":
    create_bucket()
    downloaded_dataset = download_dataset()
    extract_and_upload_files(response_zip = downloaded_dataset)
    print("Download and Upload process completed")