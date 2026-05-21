import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config.settings import SCHEDULE_INTERVAL_HOURS
from src.pipeline import run_pipeline

logger = logging.getLogger(__name__)


def start_scheduler():
    scheduler = BlockingScheduler()
    trigger = IntervalTrigger(hours=SCHEDULE_INTERVAL_HOURS)
    scheduler.add_job(run_pipeline, trigger, id="etl_pipeline", replace_existing=True)

    logger.info("Scheduler starting: pipeline will run every %d hour(s)", SCHEDULE_INTERVAL_HOURS)
    logger.info("Running pipeline immediately on startup...")
    run_pipeline()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
