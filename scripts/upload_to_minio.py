import os
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

# ----------------------
# Validate environment
# ----------------------
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
BUCKET_NAME = os.getenv("MINIO_BUCKET")
PREFIX = os.getenv("MINIO_PREFIX")
DATA_PATH = "data/raw"

assert MINIO_ENDPOINT, "Missing MINIO_ENDPOINT"
assert MINIO_ACCESS_KEY, "Missing MINIO_ACCESS_KEY"
assert MINIO_SECRET_KEY, "Missing MINIO_SECRET_KEY"
assert BUCKET_NAME, "Missing MINIO_BUCKET"
assert PREFIX, "Missing MINIO_PREFIX"

print("Config loaded:")
print(f"Endpoint: {MINIO_ENDPOINT}")
print(f"Bucket: {BUCKET_NAME}")
print(f"Prefix: {PREFIX}")
print(f"Data path exists: {os.path.exists(DATA_PATH)}")

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
# Upload files
# ----------------------
def upload_files():
    try:
        files = os.listdir(DATA_PATH)
        print("Files found:", files)
    except Exception as e:
        raise Exception(f"Failed to read data directory: {e}")

    for file_name in files:
        file_path = os.path.join(DATA_PATH, file_name)

        if os.path.isfile(file_path):
            object_name = f"{PREFIX}/{file_name}"

            try:
                client.fput_object(
                    BUCKET_NAME,
                    object_name,
                    file_path
                )
                print(f"Uploaded: {object_name}")
            except Exception as e:
                print(f"Failed to upload {file_name}: {e}")

# ----------------------
# Main
# ----------------------
if __name__ == "__main__":
    create_bucket()
    upload_files()
    print("Upload process completed")