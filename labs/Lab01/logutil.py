import logging
import sys

def setup_logger(node_id: str, level=logging.INFO):
    logger = logging.getLogger(node_id)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)

    fmt = (
        "%(asctime)s "
        "[%(name)s] "
        "%(levelname)s "
        "%(message)s"
    )

    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)

    logger.propagate = False
    return logger