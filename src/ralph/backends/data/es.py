"""Elasticsearch data backend for Ralph."""

import json
import logging
from itertools import chain
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

from elasticsearch import ApiError
from elasticsearch import ConnectionError as ESConnectionError
from elasticsearch import Elasticsearch
from elasticsearch.helpers import BulkIndexError, scan, streaming_bulk
from pydantic import BaseModel

from ralph.backends.data.base import (
    BaseDataBackend,
    BaseDataBackendSettings,
    BaseOperationType,
    BaseQuery,
    DataBackendStatus,
    enforce_query_checks,
)
from ralph.conf import BaseSettingsConfig
from ralph.exceptions import BackendException, BackendParameterException

logger = logging.getLogger(__name__)


class CommaSeparatedTuple(str):
    """Pydantic field type validating comma separated strings or lists/tuples."""

    @classmethod
    def __get_validators__(cls):  # noqa: D105
        def validate(value: Union[str, Tuple[str], List[str]]) -> Tuple[str]:
            """Checks whether the value is a comma separated string or a list/tuple."""
            if isinstance(value, (tuple, list)):
                return tuple(value)

            if isinstance(value, str):
                return tuple(value.split(","))

            raise TypeError("Invalid comma separated list")

        yield validate


class ESClientOptions(BaseModel):
    """Pydantic model for Elasticsearch additional client options."""

    class Config:
        """Base query model configuration."""

        extra = "forbid"

    ca_certs: Path = None
    verify_certs: bool = None


class ESDataBackendSettings(BaseDataBackendSettings):
    """Represents the Elasticsearch data backend default configuration.

    Attributes:
        HOSTS (str or tuple): The list of Elasticsearch nodes to connect to.
        INDEX (str): The default Elasticsearch index name.
        CLIENT_OPTIONS (dict): A dictionary of valid options for the Elasticsearch class
            initialization.
        LOCALE_ENCODING (str): The encoding used for reading/writing documents.
    """

    class Config(BaseSettingsConfig):
        """Pydantic Configuration."""

        env_prefix = "RALPH_BACKENDS__DATA__ES__"

    CLIENT_OPTIONS: ESClientOptions = ESClientOptions()
    DEFAULT_INDEX: str = "statements"
    HOSTS: CommaSeparatedTuple = ("http://localhost:9200",)
    LOCALE_ENCODING: str = "utf8"


class ESQuery(BaseQuery):
    """Elasticsearch query model."""

    query: Optional[dict]


class ESDataBackend(BaseDataBackend):
    """Elasticsearch data backend."""

    name = "es"
    query_model = ESQuery
    settings_class = ESDataBackendSettings

    def __init__(self, settings: settings_class = None):
        """Instantiates the Elasticsearch client."""
        settings = settings if settings else self.settings_class()
        self.default_index = settings.DEFAULT_INDEX
        self.locale_encoding = settings.LOCALE_ENCODING
        self.client = Elasticsearch(settings.HOSTS, **settings.CLIENT_OPTIONS.dict())

    def status(self) -> DataBackendStatus:
        """Checks Elasticsearch cluster connection and status."""
        try:
            self.client.info()
        except ESConnectionError as error:
            logger.error("Failed to connect to Elasticsearch: %s", error)
            return DataBackendStatus.AWAY

        cluster_status = self.client.cat.health()
        if "green" not in cluster_status:
            logger.error("Cluster status is not green: %s", cluster_status)
            return DataBackendStatus.ERROR

        return DataBackendStatus.OK

    def list(
        self, target: str = None, details: bool = False, new: bool = False
    ) -> Iterator[Union[str, dict]]:
        """Lists available Elasticsearch indices, data streams and aliases.

        Args:
            target (str or None): The comma-separated list of data streams, indices,
                and aliases to limit the request. Supports wildcards (*).
                If target is `None`, lists all available indices, data streams and
                    aliases. Equivalent to (`target` = "*").
            details (bool): Get detailed informations instead of just names.
            new (bool): Ignored.

        Yields:
            str: The next index, data stream or alias name. (If `details` is False).
            dict: The next index, data stream or alias details. (If `details` is True).

        Raises:
            BackendException: If a failure during indices retrieval occurs.
        """
        target = target if target else "*"
        try:
            indices = self.client.indices.get(index=target)
        except (ApiError, ESConnectionError) as error:
            msg = "Failed to read indices: %s"
            logger.error(msg, error)
            raise BackendException(msg % error) from error

        if details:
            for index in indices:
                yield {index: indices[index]}

            return

        for index in indices:
            yield index

    @enforce_query_checks
    def read(
        self,
        *,
        query: Union[str, ESQuery] = None,
        target: str = None,
        chunk_size: Union[None, int] = 500,
        raw_output: bool = False,
        ignore_errors: bool = True,
    ) -> Iterator[Union[bytes, dict]]:
        """Reads documents matching the query in the target index and yields them.

        Args:
            query: (str or ESQuery): A query in the Lucene query
                string syntax or a dictionary defining a search definition using the
                Elasticsearch Query DSL.
                The Lucene query overrides the query DSL if present.
                See Elasticsearch search reference for Lucene query syntax:
                https://www.elastic.co/guide/en/elasticsearch/reference/8.6/search-search.html#search-api-query-params-q
                See Elasticsearch search reference for query DSL syntax:
                https://www.elastic.co/guide/en/elasticsearch/reference/8.6/search-search.html#request-body-search-query
            target (str or None): The target index name to query.
                If target is `None`, the `default_index` is used instead.
            chunk_size (int or None): The chunk size for reading batches of documents.
            raw_output (bool): Controls whether to yield dictionaries or bytes.
            ignore_errors (bool): Ignored. Always set to `True`.

        Yields:
            bytes: The next chunk of documents if `raw_output` is True.
            dict: The next JSON parsed document if `raw_output` is False.
        """  # pylint: disable=line-too-long
        target = target if target else self.default_index
        reader = self._read_raw if raw_output else self._read_dict
        scan_kwargs = {
            "index": target,
            "size": chunk_size,
            "query": query.query,
            "q": query.query_string,
        }
        for document in reader(scan(self.client, **scan_kwargs)):
            yield document

    def write(  # pylint: disable=too-many-arguments
        self,
        data: Iterable[Union[bytes, dict]],
        target: Union[None, str] = None,
        chunk_size: Union[None, int] = 500,
        ignore_errors: bool = False,
        operation_type: Union[None, BaseOperationType] = None,
    ) -> int:
        """Writes data documents to the target index and returns their count."""
        count = 0
        data = iter(data)
        try:
            first_record = next(data)
        except StopIteration:
            logger.info("Data Iterator is empty; skipping write to target.")
            return count
        if not operation_type:
            operation_type = self.default_operation_type
        target = target if target else self.default_index
        if operation_type == BaseOperationType.APPEND:
            msg = "Append operation_type is not supported."
            logger.error(msg)
            raise BackendParameterException(msg)

        data = chain((first_record,), data)
        if isinstance(first_record, bytes):
            data = self._parse_bytes_to_dict(data, ignore_errors)

        logger.debug(
            "Start writing to the %s index (chunk size: %d)", target, chunk_size
        )
        try:
            for success, action in streaming_bulk(
                client=self.client,
                actions=self.to_documents(data, target, operation_type),
                chunk_size=chunk_size,
                raise_on_error=(not ignore_errors),
            ):
                count += success
                logger.debug(
                    "Wrote %d documents [action: %s ok: %d]", count, action, success
                )
        except BulkIndexError as error:
            raise BackendException(*error.args, f"{count} succeeded writes") from error
        return count

    @staticmethod
    def to_documents(
        data: Iterable[dict],
        target: str,
        operation_type: BaseOperationType,
    ) -> Iterator[dict]:
        """Converts `stream` lines to ES documents."""
        if operation_type == BaseOperationType.UPDATE:
            for item in data:
                yield {
                    "_index": target,
                    "_id": item.get("id", None),
                    "_op_type": operation_type.value,
                    "doc": item,
                }
        elif operation_type in (BaseOperationType.CREATE, BaseOperationType.INDEX):
            for item in data:
                yield {
                    "_index": target,
                    "_id": item.get("id", None),
                    "_op_type": operation_type.value,
                    "_source": item,
                }
        else:
            for item in data:
                yield {
                    "_index": target,
                    "_id": item.get("id", None),
                    "_op_type": operation_type.value,
                }

    def _read_raw(self, documents: Iterable[Dict[str, Any]]) -> Iterator[bytes]:
        """Reads the `documents` Iterable and yields bytes."""
        for document in documents:
            yield json.dumps(document).encode(self.locale_encoding)

    @staticmethod
    def _read_dict(documents: Iterable[Dict[str, Any]]) -> Iterator[dict]:
        """Reads the `documents` Iterable and yields dictionaries."""
        for document in documents:
            yield document

    @staticmethod
    def _parse_bytes_to_dict(
        raw_documents: Iterable[bytes], ignore_errors: bool
    ) -> Iterator[dict]:
        """Reads the `raw_documents` Iterable and yields dictionaries."""
        for raw_document in raw_documents:
            try:
                yield json.loads(raw_document)
            except (TypeError, json.JSONDecodeError) as error:
                msg = "Failed to decode JSON: %s, for document %s"
                logger.error(msg, error, raw_document)
                if ignore_errors:
                    continue
                raise BackendException(msg % (error, raw_document)) from error
