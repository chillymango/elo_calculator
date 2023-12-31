import os


def getenv(key: str, default: str | None = None, required: bool = True):
    val = os.getenv(key, default=default)
    if val is None and required:
        raise OSError(f"Required OS env var {key} but could not find it")
    return val


TESTING = getenv("TESTING", default=False)

SECRET_KEY = getenv("ELO_CALCULATOR_SECRET_KEY")
ALGORITHM = getenv("ELO_CALCULATOR_ALGORITHM", default="HS256")
TOKEN_EXPIRY_MINUTES = getenv("ELO_CALCULATOR_EXPIRY_MINUTES", default=24 * 60)
AUTH_USERNAME = getenv("ELO_CALCULATOR_ADMIN_USERNAME", default="admin")
AUTH_PASSWORD = getenv("ELO_CALCULATOR_ADMIN_PASSWORD")
STARTING_ELO = getenv("ELO_CALCULATOR_STARTING_ELO", default=1200)
ELO_K_VALUE_CEILING = getenv("ELO_CALCULATOR_K_PARAMETER_CEILING", default=512)
ELO_K_VALUE_FLOOR = getenv("ELO_CALCULATOR_K_PARAMETER_FLOOR", default=16)
ELO_K_VALUE_DECAY = getenv("ELO_CALCULATOR_K_VALUE_DECAY", default=2)
