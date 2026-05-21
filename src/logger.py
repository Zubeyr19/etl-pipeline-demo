import logging
import sys
from config.settings import LOG_LEVEL, LOG_FILE


def setup_logging():
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handlers = [logging.StreamHandler(sys.stdout)]
    if LOG_FILE:
        handlers.append(logging.FileHandler(LOG_FILE, encoding="utf-8"))

    logging.basicConfig(level=level, handlers=handlers, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)
