import random
import string


def generate_username(prefix: str = "auto_user") -> str:
    """Generate a unique username with a random numeric suffix."""
    suffix = "".join(random.choices(string.digits, k=6))
    return f"{prefix}_{suffix}"
