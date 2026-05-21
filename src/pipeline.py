import logging
from datetime import datetime, timezone
from src.extract import extract_all
from src.transform import transform_all
from src.load import load_records, init_db, get_engine
from src.blob_storage import upload_staging

logger = logging.getLogger(__name__)


def run_pipeline() -> dict:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    logger.info("=== ETL pipeline run started: %s ===", run_id)
    result = {
        "run_id": run_id,
        "extracted": 0,
        "transformed": 0,
        "loaded": 0,
        "blob_path": None,
        "status": "failed",
    }

    try:
        raw = extract_all()
        result["extracted"] = len(raw)

        if not raw:
            logger.warning("No raw data extracted, aborting run")
            return result

        blob_path = upload_staging(raw, run_id)
        result["blob_path"] = blob_path

        records = transform_all(raw)
        result["transformed"] = len(records)

        engine = get_engine()
        init_db(engine)
        loaded = load_records(records, engine)
        result["loaded"] = loaded

        result["status"] = "success"
        logger.info("=== Pipeline run complete: %s | loaded %d records ===", run_id, loaded)

    except Exception as e:
        logger.exception("Unhandled error during pipeline run: %s", e)

    return result
