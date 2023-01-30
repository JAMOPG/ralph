"""Tests for basic authentication for the Ralph API."""

import base64
import json

import bcrypt
import pytest

from ralph.api.auth.basic import ServerUsersCredentials, UserCredentials
from ralph.conf import settings

STORED_CREDENTIALS = json.dumps(
    [
        {
            "username": "ralph",
            "hash": bcrypt.hashpw(b"admin", bcrypt.gensalt()).decode("UTF-8"),
            "scopes": ["ralph_test_scope"],
        }
    ]
)


def test_api_auth_basic_model_serveruserscredentials():
    """Test api.auth ServerUsersCredentials model."""

    users = ServerUsersCredentials(
        __root__=[
            UserCredentials(
                username="johndoe", hash="notrealhash", scopes=["johndoe_scope"]
            ),
            UserCredentials(username="foo", hash="notsorealhash", scopes=["foo_scope"]),
        ]
    )
    other_users = ServerUsersCredentials.parse_obj(
        [
            UserCredentials(
                username="janedoe", hash="notreallyrealhash", scopes=["janedoe_scope"]
            ),
        ]
    )

    # Test addition operator
    users += other_users

    # Test len
    assert len(users) == 3

    # Test getitem
    assert users[0].username == "johndoe"
    assert users[1].username == "foo"
    assert users[2].username == "janedoe"

    # Test iterator
    usernames = [user.username for user in users]
    assert len(usernames) == 3
    assert usernames == ["johndoe", "foo", "janedoe"]

    # Test username uniqueness validator
    with pytest.raises(
        ValueError,
        match="You cannot create multiple credentials with the same username",
    ):
        users += ServerUsersCredentials.parse_obj(
            [
                UserCredentials(
                    username="foo", hash="notsorealhash", scopes=["foo_scope"]
                ),
            ]
        )


@pytest.mark.parametrize("auth_mode", ["basic"])
def test_get_whoami_no_credentials(auth_test_client):
    """Whoami route returns a 401 error when no credentials are sent."""
    response = auth_test_client.get("/whoami")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.parametrize("auth_mode", ["basic"])
def test_get_whoami_credentials_wrong_scheme(auth_test_client):
    """Whoami route returns a 401 error when wrong scheme is used for authorization."""
    response = auth_test_client.get(
        "/whoami", headers={"Authorization": "Bearer sometoken"}
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.parametrize("auth_mode", ["basic"])
def test_get_whoami_credentials_encoding_error(auth_test_client):
    """Whoami route returns a 401 error when the credentials encoding is broken."""
    response = auth_test_client.get(
        "/whoami", headers={"Authorization": "Basic not-base64"}
    )
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"
    assert response.json() == {"detail": "Invalid authentication credentials"}


@pytest.mark.parametrize("auth_mode", ["basic"])
# pylint: disable=invalid-name
def test_get_whoami_username_not_found(auth_test_client, fs):
    """Whoami route returns a 401 error when the username cannot be found."""
    credential_bytes = base64.b64encode("john:admin".encode("utf-8"))
    credentials = str(credential_bytes, "utf-8")

    auth_file_path = settings.APP_DIR / "auth.json"
    fs.create_file(auth_file_path, contents=STORED_CREDENTIALS)

    response = auth_test_client.get(
        "/whoami", headers={"Authorization": f"Basic {credentials}"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"
    assert response.json() == {"detail": "Invalid authentication credentials"}


@pytest.mark.parametrize("auth_mode", ["basic"])
# pylint: disable=invalid-name
def test_get_whoami_wrong_password(auth_test_client, fs):
    """Whoami route returns a 401 error when the password is wrong."""
    credential_bytes = base64.b64encode("john:not-admin".encode("utf-8"))
    credentials = str(credential_bytes, "utf-8")

    auth_file_path = settings.APP_DIR / "auth.json"
    fs.create_file(auth_file_path, contents=STORED_CREDENTIALS)

    response = auth_test_client.get(
        "/whoami", headers={"Authorization": f"Basic {credentials}"}
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"
    assert response.json() == {"detail": "Invalid authentication credentials"}


@pytest.mark.parametrize("auth_mode", ["basic"])
# pylint: disable=invalid-name
def test_get_whoami_correct_credentials(auth_test_client, fs):
    """Whoami returns a 200 response when the credentials are correct.

    Returns the username and associated scopes.
    """
    credential_bytes = base64.b64encode("ralph:admin".encode("utf-8"))
    credentials = str(credential_bytes, "utf-8")

    auth_file_path = settings.APP_DIR / "auth.json"
    fs.create_file(auth_file_path, contents=STORED_CREDENTIALS)

    response = auth_test_client.get(
        "/whoami", headers={"Authorization": f"Basic {credentials}"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "username": "ralph",
        "scopes": ["ralph_test_scope"],
    }
