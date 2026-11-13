"""Central logging configuration file."""

import logging

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(module)s:%(lineno)d | "
        "%(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
)

def get_logger(name: str) -> logging.Logger:
    """Retrieve or create a configured logger instance with the specified name."""

    return logging.getLogger(name)