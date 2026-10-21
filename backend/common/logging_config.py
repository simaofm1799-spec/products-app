import logging

from common.config import LOG_LEVEL


def setup_logging() -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    # httpx logs every request at INFO; our client already logs what matters
    logging.getLogger("httpx").setLevel(logging.WARNING)
