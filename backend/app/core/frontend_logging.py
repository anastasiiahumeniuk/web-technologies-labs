import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

FRONTEND_LOG_FILE = LOG_DIR / "frontend.log"

frontend_logger = logging.getLogger("frontend")
frontend_logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    FRONTEND_LOG_FILE,
    maxBytes=5_000_000,
    backupCount=3,
    encoding="utf-8"
)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

handler.setFormatter(formatter)

frontend_logger.addHandler(handler)
frontend_logger.propagate = False
