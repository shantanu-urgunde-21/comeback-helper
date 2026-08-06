import sys
from pathlib import Path
from loguru import logger

from src.config import get_settings

def setup_logger():
    """
    Configures Loguru logger for Comeback Helper.
    Outputs colorized logs to stdout and appends logs to .storage/logs/app.log.
    """
    settings = get_settings()
    log_dir = settings.storage_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    # Remove default handler to avoid duplicate logs
    logger.remove()

    # Add stdout handler with colorized formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )

    # Add rotating file handler
    logger.add(
        str(log_file),
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

    return logger

# Singleton logger instance
log = setup_logger()
