"""
Configures the TouchMap root logger (level, format, stdout handler).
"""
import logging
import sys

from app.core.config import settings


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("touchmap")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s.%(module)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()
