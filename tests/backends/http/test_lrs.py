"""Tests for Ralph LRS HTTP backend."""

import json
from urllib.parse import ParseResult, parse_qs, urlencode, urljoin, urlparse
from uuid import uuid4

import pytest
from pydantic import AnyHttpUrl
from pytest_httpx import HTTPXMock

from ralph.backends.http.base import HTTPBackendStatus
from ralph.backends.http.lrs import LRSHTTP, LRSQuery, OperationType
from ralph.conf import LRSHeaders
from ralph.exceptions import BackendException, BackendParameterException


def test_backends_http_lrs_http_instantiation():
    """Test the LRS backend instantiation."""
    assert LRSHTTP.name == "lrs"
    assert LRSHTTP.query_model == LRSQuery

    headers = LRSHeaders(
        X_EXPERIENCE_API_VERSION="1.0.3", CONTENT_TYPE="application/json"
    )
    status_endpoint = "/fake-status-endpoint"
    backend = LRSHTTP(
        url="http://fake-lrs.com",
        basic_username="user",
        basic_password="pass",
        headers=headers,
        status_endpoint=status_endpoint,
    )

    assert isinstance(backend.url, AnyHttpUrl)
    assert backend.auth == ("user", "pass")
    assert backend.headers.CONTENT_TYPE == "application/json"
    assert backend.headers.X_EXPERIENCE_API_VERSION == "1.0.3"
    assert backend.status_endpoint == "/fake-status-endpoint"


def test_backends_http_lrs_status_method_with_status_ok(httpx_mock: HTTPXMock):
    """Tests the LRS backend status method returns `ok` when all server checks are
    successful.
    """
    url = "http://fake-lrs.com"
    status_endpoint = "/__heartbeat__"

    backend = LRSHTTP(
        url=url,
        basic_username="user",
        basic_password="pass",
        status_endpoint=status_endpoint,
    )

    # Mock GET response of HTTPX
    httpx_mock.add_response(
        url=urljoin(url, status_endpoint), method="GET", status_code=200
    )

    status = backend.status()
    assert status == HTTPBackendStatus.OK


def test_backends_http_lrs_status_method_with_status_away(httpx_mock: HTTPXMock):
    """Tests the LRS backend status method returns `away` when the server is
    down.
    """

    url = "http://fake-lrs.com"
    status_endpoint = "/__heartbeat__"

    backend = LRSHTTP(
        url=url,
        basic_username="user",
        basic_password="pass",
        status_endpoint=status_endpoint,
    )

    # Mock GET response of HTTPX
    httpx_mock.add_response(
        url=urljoin(url, status_endpoint), method="GET", status_code=503
    )
    status = backend.status()
    assert status == HTTPBackendStatus.AWAY


def test_backends_http_lrs_status_method_with_status_error(httpx_mock: HTTPXMock):
    """Tests the LRS backend status method returns `error` when not all server
    checks are successful.
    """

    url = "http://fake-lrs.com"
    status_endpoint = "/__heartbeat__"

    backend = LRSHTTP(
        url=url,
        basic_username="user",
        basic_password="pass",
        status_endpoint=status_endpoint,
    )

    # Mock GET response of HTTPX with status code 500
    httpx_mock.add_response(
        url=urljoin(url, status_endpoint), method="GET", status_code=500
    )
    status = backend.status()
    assert status == HTTPBackendStatus.ERROR

    # Mock GET response of HTTPX with status code 404
    httpx_mock.add_response(
        url=urljoin(url, status_endpoint), method="GET", status_code=404
    )

    status = backend.status()
    assert status == HTTPBackendStatus.ERROR


def test_backends_http_lrs_list_method():
    "Test the LRS backend `list` method raises a `NotImplementedError`."

    url = "http://fake-lrs.com"
    target = "/xAPI/statements/"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    msg = (
        "LRS HTTP backend does not support `list` method, "
        "cannot list from /xAPI/statements/"
    )
    with pytest.raises(NotImplementedError, match=msg):
        backend.list(target=target)


def test_backends_http_lrs_read_method_without_target(httpx_mock: HTTPXMock):
    """Tests the LRS backend `read` method without target parameter value fetches
    statements from '/xAPI/statements' default endpoint.
    """

    url = "http://fake-lrs.com"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    statements = {
        "statements": [
            {"id": str(uuid4()), "timestamp": "2022-06-22T08:31:38"},
            {"id": str(uuid4()), "timestamp": "2022-07-22T08:31:38"},
            {"id": str(uuid4()), "timestamp": "2022-08-22T08:31:38"},
        ]
    }

    # Mock HTTPX POST
    httpx_mock.add_response(
        url=urljoin(url, "/xAPI/statements"), method="GET", json=statements
    )

    result = backend.read()
    assert list(result) == statements["statements"]


def test_backends_http_lrs_read_method_without_statements(httpx_mock: HTTPXMock):
    """Test the LRS backend `read` method without statements in the target endpoint
    raises a `BackendException`.
    """

    url = "http://fake-lrs.com"
    target = "/xAPI/statements/"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    # Mock GET response of HTTPX
    httpx_mock.add_response(url=urljoin(url, target), method="GET", status_code=500)

    with pytest.raises(BackendException, match="Failed to fetch statements."):
        list(backend.read(target=target))


def test_backends_http_lrs_read_method_without_pagination(httpx_mock: HTTPXMock):
    """Test the LRS backend `read` method when the request on the target endpoint
    returns statements without pagination."""

    url = "http://fake-lrs.com"
    target = "/xAPI/statements/"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    statements = {
        "statements": [
            {
                "id": str(uuid4()),
                "verb": {"id": "https://w3id.org/xapi/video/verbs/played"},
                "timestamp": "2022-06-22T08:31:38",
            },
            {
                "id": str(uuid4()),
                "verb": {"id": "https://w3id.org/xapi/video/verbs/played"},
                "timestamp": "2022-07-22T08:31:38",
            },
            {
                "id": str(uuid4()),
                "verb": {"id": "https://w3id.org/xapi/video/verbs/paused"},
                "timestamp": "2022-08-22T08:31:38",
            },
        ]
    }

    # Mock GET response of HTTPX without query parameter
    httpx_mock.add_response(url=urljoin(url, target), method="GET", json=statements)

    # Return an iterable of dict
    result = backend.read(target=target, raw_output=False)
    assert list(result) == statements["statements"]

    # Return an iterable of bytes
    result = backend.read(target=target, raw_output=True)
    assert list(result) == [
        bytes(json.dumps(statement), encoding="utf-8")
        for statement in statements["statements"]
    ]

    # Mock GET response of HTTPX with query parameter
    params = LRSQuery(query_string={"verb": "https://w3id.org/xapi/video/verbs/played"})

    statements_with_query_played_verb = {
        "statements": [
            raw for raw in statements["statements"] if "played" in raw["verb"]
        ]
    }
    httpx_mock.add_response(
        url=ParseResult(
            scheme=urlparse(url).scheme,
            netloc=urlparse(url).netloc,
            path=target,
            query=urlencode(params.query_string),
            params="",
            fragment="",
        ).geturl(),
        method="GET",
        json=statements_with_query_played_verb,
    )
    # Return an iterable of dict
    result = backend.read(query=params, target=target, raw_output=False)
    assert list(result) == statements_with_query_played_verb["statements"]

    # Return an iterable of bytes
    result = backend.read(query=params, target=target, raw_output=True)
    assert list(result) == [
        bytes(json.dumps(statement), encoding="utf-8")
        for statement in statements_with_query_played_verb["statements"]
    ]


def test_backends_http_lrs_read_method_with_pagination(httpx_mock: HTTPXMock):
    """Test the LRS backend `read` method when the request on the target endpoint
    returns statements with pagination."""

    url = "http://fake-lrs.com"
    target = "/xAPI/statements/"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    more_target = "/xAPI/statements/?pit_id=fake-pit-id"
    statements = {
        "statements": [
            {
                "id": str(uuid4()),
                "verb": {"id": "https://w3id.org/xapi/video/verbs/played"},
                "timestamp": "2022-06-22T08:31:38",
            },
            {
                "id": str(uuid4()),
                "verb": {"id": "https://w3id.org/xapi/video/verbs/played"},
                "timestamp": "2022-07-22T08:31:38",
            },
            {
                "id": str(uuid4()),
                "verb": {"id": "https://w3id.org/xapi/video/verbs/paused"},
                "timestamp": "2022-08-22T08:31:38",
            },
        ],
        "more": more_target,
    }
    more_statements = {
        "statements": [
            {
                "id": str(uuid4()),
                "verb": {"id": "https://w3id.org/xapi/video/verbs/seeked"},
                "timestamp": "2022-09-22T08:31:38",
            },
            {
                "id": str(uuid4()),
                "verb": {"id": "https://w3id.org/xapi/video/verbs/played"},
                "timestamp": "2022-10-22T08:31:38",
            },
            {
                "id": str(uuid4()),
                "verb": {"id": "https://w3id.org/xapi/video/verbs/paused"},
                "timestamp": "2022-11-22T08:31:38",
            },
        ]
    }

    # Mock GET response of HTTPX for target and "more" target without query parameter
    httpx_mock.add_response(
        url=urljoin(url, target),
        method="GET",
        json=statements,
    )
    httpx_mock.add_response(
        url=urljoin(url, more_target),
        method="GET",
        json=more_statements,
    )

    # Return an iterable of dict
    result = backend.read(target=target, raw_output=False)
    assert list(result) == statements["statements"] + more_statements["statements"]

    # Return an iterable of bytes
    result = backend.read(target=target, raw_output=True)
    assert list(result) == [
        bytes(json.dumps(statement), encoding="utf-8")
        for statement in statements["statements"] + more_statements["statements"]
    ]

    # Mock GET response of HTTPX with query parameter
    query_params = LRSQuery(
        query_string={"verb": "https://w3id.org/xapi/video/verbs/played"}
    )

    statements_with_query_played_verb = {
        "statements": [
            raw for raw in statements["statements"] if "played" in raw["verb"]["id"]
        ],
        "more": more_target,
    }
    more_statements_with_query_played_verb = {
        "statements": [
            raw
            for raw in more_statements["statements"]
            if "played" in raw["verb"]["id"]
        ]
    }

    httpx_mock.add_response(
        url=ParseResult(
            scheme=urlparse(url).scheme,
            netloc=urlparse(url).netloc,
            path=target,
            query=urlencode(query_params.query_string),
            params="",
            fragment="",
        ).geturl(),
        method="GET",
        json=statements_with_query_played_verb,
    )

    more_query_params = query_params.query_string
    more_query_params.update(parse_qs(urlparse(more_target).query))
    httpx_mock.add_response(
        url=ParseResult(
            scheme=urlparse(url).scheme,
            netloc=urlparse(url).netloc,
            path=urlparse(more_target).path,
            query=urlencode(more_query_params),
            params="",
            fragment="",
        ).geturl(),
        method="GET",
        json=more_statements_with_query_played_verb,
    )

    # Return an iterable of dict
    result = backend.read(query=query_params, target=target, raw_output=False)
    assert (
        list(result)
        == statements_with_query_played_verb["statements"]
        + more_statements_with_query_played_verb["statements"]
    )

    # Return an iterable of bytes
    result = backend.read(query=query_params, target=target, raw_output=True)
    assert list(result) == [
        bytes(json.dumps(statement), encoding="utf-8")
        for statement in statements_with_query_played_verb["statements"]
        + more_statements_with_query_played_verb["statements"]
    ]


def test_backends_http_lrs_write_method_without_operation(httpx_mock: HTTPXMock):
    """Tests the LRS backend `write` method, given no operation_type should POST to
    the LRS server.
    """

    url = "http://fake-lrs.com"
    target = "/xAPI/statements/"

    data = [
        {"id": str(uuid4()), "timestamp": "2022-06-22T08:31:38"},
        {"id": str(uuid4()), "timestamp": "2022-07-22T08:31:38"},
        {"id": str(uuid4()), "timestamp": "2022-08-22T08:31:38"},
    ]

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    # Mock HTTPX POST
    httpx_mock.add_response(url=urljoin(url, target), method="POST", json=data)

    result = backend.write(target=target, data=data)
    assert result == len(data)


def test_backends_http_lrs_write_method_without_data():
    """Tests the LRS backend `write` method returns null when no data to write
    in the target endpoint are given.
    """

    url = "http://fake-lrs.com"
    target = "/xAPI/statements/"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    result = backend.write(target=target, data=[])
    assert result == 0


def test_backends_http_lrs_write_method_with_append_operation():
    """Tests the LRS backend `write` method, given an `APPEND` `operation_type`, should
    raise a `BackendParameterException`.
    """

    url = "http://fake-lrs.com"
    target = "/xAPI/statements/"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    msg = "Append operation_type is not supported."
    with pytest.raises(BackendParameterException, match=msg):
        backend.write(target=target, data=[b"foo"], operation_type=OperationType.APPEND)


def test_backends_http_lrs_write_method_with_update_operation():
    """Tests the LRS backend `write` method, given an `UPDATE` `operation_type`, should
    raise a `BackendParameterException`.
    """

    url = "http://fake-lrs.com"
    target = "/xAPI/statements"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    msg = "Update operation_type is not supported."
    with pytest.raises(BackendParameterException, match=msg):
        backend.write(target=target, data=[b"foo"], operation_type=OperationType.UPDATE)


def test_backends_http_lrs_write_method_with_delete_operation():
    """Tests the LRS backend `write` method, given a `DELETE` `operation_type`, should
    raise a `BackendParameterException`.
    """

    url = "http://fake-lrs.com"
    target = "/xAPI/statements"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    msg = "Delete operation_type is not supported."
    with pytest.raises(BackendParameterException, match=msg):
        backend.write(target=target, data=[b"foo"], operation_type=OperationType.DELETE)


def test_backends_http_lrs_write_method_without_target(httpx_mock: HTTPXMock):
    """Tests the LRS backend `write` method without target parameter value writes
    statements to '/xAPI/statements' default endpoint."""

    url = "http://fake-lrs.com"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    data = [
        {"id": str(uuid4()), "timestamp": "2022-06-22T08:31:38"},
        {"id": str(uuid4()), "timestamp": "2022-07-22T08:31:38"},
        {"id": str(uuid4()), "timestamp": "2022-08-22T08:31:38"},
    ]

    # Mock HTTPX POST
    httpx_mock.add_response(
        url=urljoin(url, "/xAPI/statements"), method="POST", json=data
    )

    result = backend.write(data=data, operation_type=OperationType.CREATE)
    assert result == len(data)


def test_backends_http_lrs_write_method_with_create_or_index_operation(
    httpx_mock: HTTPXMock,
):
    """Tests the `LRSHTTP.write` method with `CREATE` or `INDEX` operation_type writes
    statements to the given target endpoint.
    """

    url = "http://fake-lrs.com"
    target = "/xAPI/statements"

    backend = LRSHTTP(url=url, basic_username="user", basic_password="pass")

    data = [
        {"id": str(uuid4()), "timestamp": "2022-06-22T08:31:38"},
        {"id": str(uuid4()), "timestamp": "2022-07-22T08:31:38"},
        {"id": str(uuid4()), "timestamp": "2022-08-22T08:31:38"},
    ]

    # Mock HTTPX POST
    httpx_mock.add_response(url=urljoin(url, target), method="POST", json=data)

    result = backend.write(
        target=target, data=data, operation_type=OperationType.CREATE
    )
    assert result == len(data)

    result = backend.write(target=target, data=data, operation_type=OperationType.INDEX)
    assert result == len(data)
