import random
import re
import string
import logging

logger = logging.getLogger(__name__)


def generate_username(prefix: str = "auto_user") -> str:
    """Generate a unique username with a random numeric suffix."""
    suffix = "".join(random.choices(string.digits, k=6))
    return f"{prefix}_{suffix}"


def parse_record_count(text: str) -> int:
    """Extract record count from OrangeHRM text like '(5) Records Found'."""
    match = re.search(r"\((\d+)\)", text)
    if match:
        return int(match.group(1))
    raise ValueError(f"Could not parse record count from: '{text}'")


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
