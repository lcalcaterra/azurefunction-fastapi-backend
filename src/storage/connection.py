import os
from azure.storage.blob import BlobServiceClient


AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER")

if not AZURE_STORAGE_CONNECTION_STRING:
    raise RuntimeError("Missing AZURE_STORAGE_CONNECTION_STRING env var")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER)

# Create container if not exists
try:
    container_client.create_container()
except Exception:
    pass