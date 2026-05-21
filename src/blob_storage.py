import json
import logging
from datetime import datetime, timezone
from typing import Optional
from config.settings import AZURE_STORAGE_CONNECTION_STRING, AZURE_CONTAINER_NAME

logger = logging.getLogger(__name__)

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False
    logger.warning("azure-storage-blob not installed; blob staging will be skipped")


def _get_client() -> Optional[object]:
    if not AZURE_SDK_AVAILABLE:
        return None
    if not AZURE_STORAGE_CONNECTION_STRING:
        logger.warning("AZURE_STORAGE_CONNECTION_STRING not set; skipping blob upload")
        return None
    return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


def upload_staging(raw_data: list[dict], run_id: str = "") -> Optional[str]:
    client = _get_client()
    if client is None:
        return None

    if not run_id:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    blob_name = f"weather/{run_id}/raw.json"
    payload = json.dumps(raw_data, default=str)

    try:
        container_client = client.get_container_client(AZURE_CONTAINER_NAME)
        try:
            container_client.create_container()
        except Exception:
            pass  # container already exists

        container_client.upload_blob(name=blob_name, data=payload, overwrite=True)
        logger.info("Staged raw data to blob: %s/%s", AZURE_CONTAINER_NAME, blob_name)
        return blob_name
    except Exception as e:
        logger.error("Blob upload failed: %s", e)
        return None


def download_staging(blob_name: str) -> Optional[list[dict]]:
    client = _get_client()
    if client is None:
        return None

    try:
        blob_client = client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=blob_name)
        data = blob_client.download_blob().readall()
        logger.info("Downloaded staging blob: %s", blob_name)
        return json.loads(data)
    except Exception as e:
        logger.error("Blob download failed: %s", e)
        return None
