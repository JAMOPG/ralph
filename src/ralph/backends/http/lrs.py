"""LRS HTTP backend for Ralph."""

import json
import logging
from itertools import chain
from typing import Iterator, List, Optional, Union
from urllib.parse import ParseResult, parse_qs, urljoin, urlparse

import httpx
from httpx import Client, HTTPError, HTTPStatusError
from more_itertools import chunked
from pydantic import AnyHttpUrl, BaseModel, parse_obj_as

from ralph.conf import LRSHeaders, settings
from ralph.exceptions import BackendException, BackendParameterException

from .base import (
    BaseHTTP,
    BaseQuery,
    HTTPBackendStatus,
    OperationType,
    enforce_query_checks,
)

lrs_settings = settings.BACKENDS.HTTP.LRS
logger = logging.getLogger(__name__)


class StatementResponse(BaseModel):
    """Pydantic model for `get` statements response."""

    statements: Union[List[dict], dict]
    more: Optional[str]


class LRSQuery(BaseQuery):
    """LRS body query model."""

    query_string: Optional[dict]


class LRSHTTP(BaseHTTP):
    """LRS HTTP backend."""

    name = "lrs"
    query_model = LRSQuery
    default_operation_type = OperationType.CREATE

    def __init__(  # pylint: disable=too-many-arguments
        self,
        url: str = lrs_settings.URL,
        basic_username: str = lrs_settings.BASIC_USERNAME,
        basic_password: str = lrs_settings.BASIC_PASSWORD,
        headers: LRSHeaders = lrs_settings.HEADERS,
        status_endpoint: str = lrs_settings.STATUS_ENDPOINT,
    ):
        """Instantiates the LRS client.

        Args:
            url (AnyHttpUrl): LRS server URL.
            basic_username (str): Basic auth username for LRS authentication.
            basic_password (str): Basic auth password for LRS authentication.
            headers (dict): Headers defined for the LRS server connection.
            status_endpoint (str): Endpoint used to check server status.
        """
        self.url = parse_obj_as(AnyHttpUrl, url)
        self.auth = (basic_username, basic_password)
        self.headers = headers
        self.status_endpoint = status_endpoint

    def status(self):
        """Implements HTTP backend check for server status."""
        status_url = urljoin(self.url, self.status_endpoint)

        try:
            response = httpx.get(status_url)
            response.raise_for_status()
        except HTTPStatusError:
            if response.status_code == 503:
                return HTTPBackendStatus.AWAY
            if response.status_code in (500, 404):
                return HTTPBackendStatus.ERROR

        return HTTPBackendStatus.OK

    def list(
        self, target: str = None, details: bool = False, new: bool = False
    ) -> Iterator[Union[str, dict]]:
        # noqa: D205, D415
        """LRS HTTP backend does not support `list` method,
        calling this method will raise an error.
        """
        msg = "LRS HTTP backend does not support `list` method, cannot list from %s"
        logger.error(msg, target)
        raise NotImplementedError(msg % target)

    @enforce_query_checks
    def read(  # pylint: disable=too-many-arguments
        self,
        query: Union[str, LRSQuery] = None,
        target: str = None,
        chunk_size: Union[None, int] = None,
        raw_output: bool = False,
        ignore_errors: bool = False,
    ) -> Iterator[Union[bytes, dict]]:
        """Get statements from LRS `target` endpoint.

        The `read` method defined in the LRS specification returns `statements` array
        and `more` IRL. The latter is required when the returned `statement` list has
        been limited.

        Args:
            query (str, LRSQuery):  The query to select records to read.
            target (str): Endpoint from which to read data (e.g. `/statements`).
                If target is `None`, `/xAPI/statements` default endpoint is used.
            chunk_size (int or None): The number of records or bytes to read in one
                batch, depending on whether the records are dictionaries or bytes.
            raw_output (bool): Controls whether to yield bytes or dictionaries.
                If the records are dictionaries and `raw_output` is set to `True`, they
                are encoded as JSON.
                If the records are bytes and `raw_output` is set to `False`, they are
                decoded as JSON by line.
            ignore_errors (bool): If `True`, errors during the read operation
                are be ignored and logged. If `False` (default), a `BackendException`
                is raised if an error occurs.
        """
        if not target:
            target = "/xAPI/statements"

        if query.query_string:
            query_params = query.query_string
        else:
            query_params = {}

        # Create request URL
        target = ParseResult(
            scheme=urlparse(self.url).scheme,
            netloc=urlparse(self.url).netloc,
            path=target,
            query="",
            params="",
            fragment="",
        ).geturl()

        def fetch_statements(url, query_params):
            with Client(auth=self.auth, headers=self.headers) as client:
                response = client.get(url=url, params=query_params)
                response.raise_for_status()

                statements_response = parse_obj_as(StatementResponse, response.json())
                statements = statements_response.statements
                statements = (
                    [statements] if not isinstance(statements, list) else statements
                )
                for statement in statements:
                    yield bytes(
                        json.dumps(statement), encoding="utf-8"
                    ) if raw_output else statement
                if statements_response.more:
                    query_params.update(
                        parse_qs(urlparse(statements_response.more).query)
                    )
                    yield from fetch_statements(url=target, query_params=query_params)

        try:
            yield from fetch_statements(url=target, query_params=query_params)
        except HTTPError as error:
            msg = "Failed to fetch statements."
            logger.error("%s. %s", msg, error)
            raise BackendException(msg, *error.args) from error

    def write(  # pylint: disable=too-many-arguments
        self,
        data: Union[List[bytes], List[dict]],
        target: Union[None, str] = None,
        chunk_size: Union[None, int] = 500,
        ignore_errors: bool = False,
        operation_type: Union[None, OperationType] = None,
    ) -> int:
        """Writes `data` records to the `target` endpoint and returns their count.

        Args:
            data: (Iterable or ): The data to write.
            target (str or None): Endpoint where to write data (e.g. `/statements`).
                If `target` is `None`, `/xAPI/statements` default endpoint is used.
            chunk_size (int or None): The number of records or bytes to write in one
                batch, depending on whether `data` contains dictionaries or bytes.
                If `chunk_size` is `None`, a default value is used instead.
            ignore_errors (bool): If `True`, errors during the write operation
                are ignored and logged. If `False` (default), a `BackendException`
                is raised if an error occurs.
            operation_type (OperationType or None): The mode of the write operation.
                If `operation_type` is `None`, the `default_operation_type` is used
                instead. See `OperationType`.
        """
        statements_count = 0

        data = iter(data)
        try:
            first_record = next(data)
        except StopIteration:
            logger.info("Data Iterator is empty; skipping write to target.")
            return statements_count

        if not operation_type:
            operation_type = self.default_operation_type

        if operation_type == OperationType.APPEND:
            msg = "Append operation_type is not supported."
            logger.error(msg)
            raise BackendParameterException(msg)

        if operation_type == OperationType.UPDATE:
            msg = "Update operation_type is not supported."
            logger.error(msg)
            raise BackendParameterException(msg)

        if operation_type == OperationType.DELETE:
            msg = "Delete operation_type is not supported."
            logger.error(msg)
            raise BackendParameterException(msg)

        if not target:
            target = "/xAPI/statements"

        target = ParseResult(
            scheme=urlparse(self.url).scheme,
            netloc=urlparse(self.url).netloc,
            path=target,
            query="",
            params="",
            fragment="",
        ).geturl()

        data = chain((first_record,), data)

        logger.debug(
            "Start writing to the %s endpoint (chunk size: %d)", target, chunk_size
        )

        if operation_type in [OperationType.INDEX, OperationType.CREATE]:
            with Client(auth=self.auth, headers=self.headers) as client:
                for chunk in chunked(data, chunk_size):
                    request = client.post(target, content=chunk)
                    try:
                        request.raise_for_status()
                    except HTTPError as error:
                        msg = "Failed to post statements"
                        logger.error("%s. %s", msg, error)
                        raise BackendException(msg, *error.args) from error
                    statements_count += len(chunk)
                    logger.debug("Posted %d statements", statements_count)

        return statements_count
