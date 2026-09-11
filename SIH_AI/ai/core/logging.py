import logging
import sys

def setup_logger(name: str = "ai_service") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logger()

def log_event(event: str, **kwargs):
    """
    Structured logging helper.
    """
    msg_parts = [f"event={event}"]
    for k, v in kwargs.items():
        msg_parts.append(f"{k}={v}")
    logger.info(" ".join(msg_parts))
