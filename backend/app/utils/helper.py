import secrets
import string


def generate_unique_id(length: int = 16) -> str:
    """
    Generate a secure unique ID using secrets module
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))