import sys
from pathlib import Path
from loguru import logger

from shared.config import get_settings

CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Handler id of the console sink, so it can be moved to stderr later.
_console_handler_id: int | None = None


def setup_logger():
    """
    Configures Loguru logger for Comeback Helper.
    Outputs colorized logs to stdout and appends logs to .storage/logs/app.log.
    """
    global _console_handler_id
    settings = get_settings()
    log_dir = settings.storage_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    # Remove default handler to avoid duplicate logs
    logger.remove()

    # Add stdout handler with colorized formatting
    _console_handler_id = logger.add(
        sys.stdout,
        format=CONSOLE_FORMAT,
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


def use_stderr_console():
    """Moves the console log sink from stdout to stderr.

    Callers that print machine-readable output (the CLI's --json mode) need
    stdout to carry exactly one JSON object and nothing else. Loguru's console
    sink defaults to stdout, which would interleave log lines into that output
    and make it unparseable. The rotating file sink is left alone, so a JSON
    invocation still produces a full log in .storage/logs/app.log.
    """
    global _console_handler_id
    if _console_handler_id is not None:
        try:
            logger.remove(_console_handler_id)
        except ValueError:
            pass  # already removed
    _console_handler_id = logger.add(sys.stderr, format=CONSOLE_FORMAT, level="INFO")


# Singleton logger instance
log = setup_logger()
