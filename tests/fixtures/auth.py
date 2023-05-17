"""Test fixtures related to authentication on the API."""
import base64
import json

import bcrypt
import pytest

from ralph.api.auth import get_stored_credentials
from ralph.conf import settings


def create_user(fs_, user, pwd, scopes):
    """Create a user in the (fake) file system"""
    credential_bytes = base64.b64encode(f"{user}:{pwd}".encode("utf-8"))
    credentials = str(credential_bytes, "utf-8")
    auth_file_path = settings.AUTH_FILE  # settings.APP_DIR / "auth.json"

    # Clear lru_cache to allow for auth testing within same function
    get_stored_credentials.cache_clear()

    fs_.create_file(
        auth_file_path,
        contents=json.dumps(
            [
                {
                    "username": user,
                    "hash": bcrypt.hashpw(
                        bytes(pwd.encode("utf-8")), bcrypt.gensalt()
                    ).decode("UTF-8"),
                    "scopes": scopes,
                }
            ]
        ),
    )
    return credentials


# pylint: disable=invalid-name
@pytest.fixture
def auth_credentials(fs, user_scopes=None):
    """Sets up the credentials file for request authentication.

    Args:
        fs: fixture provided by pyfakefs (not called in the code)
        user_scopes (List[str]): list of scopes to associate to the user

    Returns:
        credentials (str): auth parameters that need to be passed
            through headers to authenticate the request.
    """

    user = "ralph"
    pwd = "admin"
    # scopes = ["statements/read", "statements/write"]
    if user_scopes is None:
        user_scopes = ["all"]

    credentials = create_user(fs, user, pwd, user_scopes)

    return credentials