"""ClickhouseDB data backend for Ralph."""

import json
import logging
from datetime import datetime
from io import IOBase
from itertools import chain
from typing import (
    Any,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Union,
)
from uuid import UUID, uuid4

import clickhouse_connect
from clickhouse_connect.driver.exceptions import ClickHouseError
from pydantic import BaseModel, ValidationError

from ralph.backends.data.base import (
    BaseDataBackend,
    BaseDataBackendSettings,
    BaseOperationType,
    BaseQuery,
    DataBackendStatus,
    enforce_query_checks,
)
from ralph.backends.lrs.base import (
    BaseLRSBackend,
    StatementParameters,
    StatementQueryResult,
)
from ralph.conf import BaseSettingsConfig, ClientOptions
from ralph.exceptions import (
    BackendException,
    BackendParameterException,
    BadFormatException,
)

logger = logging.getLogger(__name__)


class ClickHouseInsert(BaseModel):
    """Model to validate required fields for ClickHouse insertion."""

    event_id: UUID
    emission_time: datetime


class ClickhouseClientOptions(ClientOptions):
    """Pydantic model for `clickhouse` client options."""

    date_time_input_format: str = "best_effort"
    allow_experimental_object_type: Literal[0, 1] = 1


class ClickHouseDataBackendSettings(BaseDataBackendSettings):
    """Represents the ClickHouse data backend default configuration.

    Attributes:
        HOST (str): ClickHouse server host to connect to.
        PORT (int): ClickHouse server port to connect to.
        DATABASE (str): ClickHouse database to connect to.
        EVENT_TABLE_NAME (str): Table where events live.
        USERNAME (str): ClickHouse username to connect as (optional).
        PASSWORD (str): Password for the given ClickHouse username (optional).
        CLIENT_OPTIONS (dict): A dictionary of valid options for the ClickHouse
            client connection.
        LOCALE_ENCODING (str): The locale encoding to use when none is provided.
    """

    class Config(BaseSettingsConfig):
        """Pydantic Configuration."""

        env_prefix = "RALPH_BACKENDS__DATA__CLICKHOUSE__"

    HOST: str = "localhost"
    PORT: int = 8123
    DATABASE: str = "xapi"
    EVENT_TABLE_NAME: str = "xapi_events_all"
    USERNAME: str = None
    PASSWORD: str = None
    CLIENT_OPTIONS: ClickhouseClientOptions = ClickhouseClientOptions()
    LOCALE_ENCODING: str = "utf8"


class ClickHouseQuery(BaseQuery):
    """ClickHouse query model."""

    where_clause: Optional[str]
    return_fields: Optional[List[str]]


class ClickHouseDataBackend(
    BaseDataBackend
):  # pylint: disable=too-many-instance-attributes
    """ClickHouse database backend."""

    name = "clickhouse"
    query_model = ClickHouseQuery
    default_operation_type = BaseOperationType.CREATE
    default_chunk_size = 500
    settings_class = ClickHouseDataBackendSettings

    def __init__(self, settings: settings_class = None):
        """Instantiates the ClickHouse configuration.

        Args:
            settings (ClickHouseDataBackendSettings): The ClickHouse data backend
                settings.
            host (str): ClickHouse server host to connect to.
            port (int): ClickHouse server port to connect to.
            database (str): ClickHouse database to connect to.
            event_table_name (str): Table where events live.
            username (str): ClickHouse username to connect as (optional).
            password (str): Password for the given ClickHouse username (optional).
            client_options (dict): A dictionary of valid options for the ClickHouse
                client connection.
            locale_encoding (str): The locale encoding to use when none is provided.
            _client (clickhouse_driver.Client): The ClickHouse client instance.

        If username and password are None, we will try to connect as the ClickHouse
        user "default".
        """
        settings = settings if settings else self.settings_class()
        self.host = settings.HOST
        self.port = settings.PORT
        self.database = settings.DATABASE
        self.event_table_name = settings.EVENT_TABLE_NAME
        self.username = settings.USERNAME
        self.password = settings.PASSWORD
        self.client_options = settings.CLIENT_OPTIONS.dict()
        self.locale_encoding = settings.LOCALE_ENCODING
        self._client = None

    @property
    def client(self):
        """Creates a ClickHouse client if it doesn't exist.

        We do this here so that we don't interrupt initialization in the case
        where ClickHouse is not running when Ralph starts up, which will cause
        Ralph to hang. This client is HTTP, so not actually stateful. Ralph
        should be able to gracefully deal with ClickHouse outages at all other
        times.
        """
        if not self._client:
            self._client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                database=self.database,
                username=self.username,
                password=self.password,
                settings=self.client_options,
            )
        return self._client

    def status(self) -> DataBackendStatus:
        """Checks ClickHouse connection status."""
        try:
            self.client.query("SELECT 1")
        except ClickHouseError:
            return DataBackendStatus.AWAY

        return DataBackendStatus.OK

    def list(
        self, target: str = None, details: bool = False, new: bool = False
    ) -> Iterator[Union[str, dict]]:
        """Lists documents for a given table.

        Args:
            target (str): The table to list documents from.
            details (bool): Get detailed archive information instead of just ids.
            new (bool): Given the history, list only not already fetched archives.
        """
        sql = "SHOW TABLES"
        self.client.database = target if target else self.database
        for document in self.client.query(sql).named_results():
            if details:
                yield document
            else:
                yield str(document.get("name"))

    @enforce_query_checks
    def read(
        self,
        *,
        query: Union[str, ClickHouseQuery] = None,
        target: str = None,
        chunk_size: Union[None, int] = None,
        raw_output: bool = False,
        ignore_errors: bool = False,
    ) -> Iterator[Union[bytes, dict]]:
        """Reads documents from the database."""
        reader = self._read_raw if raw_output else self._read_dict
        fields = ",".join(query.return_fields) if query.return_fields else "event"

        if target is None:
            target = self.event_table_name
        sql = f"SELECT {fields} FROM {target}"  # nosec

        if query.where_clause:
            sql += f"  WHERE {query.where_clause}"

        if chunk_size is None:
            chunk_size = self.default_chunk_size

        sql += f" LIMIT {chunk_size}"

        result = self.client.query(sql).named_results()
        for statement in result:
            yield reader(statement)

    @staticmethod
    def to_documents(
        data: Iterable[dict],
        ignore_errors: bool = False,
        operation_type: Union[None, BaseOperationType] = default_operation_type,
    ) -> Generator[dict, None, None]:
        """Converts `stream` lines (one statement per line) to insert tuples."""
        for statement in data:
            if "timestamp" not in statement or (
                operation_type == BaseOperationType.CREATE
                and not statement.get("id", "")
            ):
                err = (
                    "Statement has an invalid or missing id or "
                    f"timestamp field: {statement}"
                )
                if ignore_errors:
                    logger.warning(err)
                    continue
                raise BadFormatException(err)
            try:
                insert = ClickHouseInsert(
                    event_id=statement.get("id", str(uuid4())),
                    emission_time=statement["timestamp"],
                )
            except (KeyError, ValidationError) as exc:
                err = (
                    "Statement has an invalid or missing id or "
                    f"timestamp field: {statement}"
                )
                if ignore_errors:
                    logger.warning(err)
                    continue
                raise BadFormatException(err) from exc

            document = (
                insert.event_id,
                insert.emission_time,
                statement,
                json.dumps(statement),
            )

            yield document

    def bulk_import(
        self, batch: list, ignore_errors: bool = False, event_table_name=None
    ):
        """Inserts a batch of documents into the selected database table."""
        try:
            if event_table_name is None:
                event_table_name = self.event_table_name
            found_ids = {x[0] for x in batch}

            if len(found_ids) != len(batch):
                raise BackendException("Duplicate IDs found in batch")

            self.client.insert(
                event_table_name,
                batch,
                column_names=[
                    "event_id",
                    "emission_time",
                    "event",
                    "event_str",
                ],
                # Allow ClickHouse to buffer the insert, and wait for the
                # buffer to flush. Should be configurable, but I think these are
                # reasonable defaults.
                settings={"async_insert": 1, "wait_for_async_insert": 1},
            )
        except (ClickHouseError, BackendException) as error:
            if not ignore_errors:
                raise BackendException(*error.args) from error
            logger.warning(
                "Bulk import failed for current chunk but you choose to ignore it.",
            )
            # There is no current way of knowing how many rows from the batch
            # succeeded, we assume 0 here.
            return 0
        inserted_count = len(batch)
        logger.debug("Inserted %d documents chunk with success", inserted_count)

        return inserted_count

    def write(  # pylint: disable=too-many-arguments disable=too-many-branches
        self,
        data: Union[IOBase, Iterable[bytes], Iterable[dict]],
        target: Union[None, str] = None,
        chunk_size: Union[None, int] = None,
        ignore_errors: bool = False,
        operation_type: Union[None, BaseOperationType] = None,
    ) -> int:
        """Method to insert multiple rows/data to our target table in our database.

        Args:
            data: The data to write to the database.
            target: The target table to write to.
            chunk_size: The number of documents to write at once.
            ignore_errors: Whether to ignore errors or not.
            operation_type: The operation type to use for the write operation.
        """
        target = target if target else self.event_table_name
        if not operation_type:
            operation_type = self.default_operation_type
        if not chunk_size:
            chunk_size = self.default_chunk_size
        logger.debug(
            "Start writing to the %s table of the %s database (chunk size: %d)",
            target,
            self.database,
            chunk_size,
        )

        data = iter(data)
        try:
            first_record = next(data)
        except StopIteration:
            logger.info("Data Iterator is empty; skipping write to target.")
            return 0

        data = chain([first_record], data)
        if isinstance(first_record, bytes):
            data = self._parse_bytes_to_dict(data, ignore_errors)

        success = 0
        batch = []
        if operation_type == BaseOperationType.CREATE:
            for document in self.to_documents(
                data, ignore_errors=ignore_errors, operation_type=operation_type
            ):
                batch.append(document)
                if len(batch) < chunk_size:
                    continue

                success += self.bulk_import(
                    batch,
                    ignore_errors=ignore_errors,
                    event_table_name=target,
                )
                batch = []

            # Edge case: if the total number of documents is lower than the chunk size
            if len(batch) > 0:
                success += self.bulk_import(
                    batch,
                    ignore_errors=ignore_errors,
                    event_table_name=target,
                )

            logger.debug("Inserted a total of %d documents with success", success)
        else:
            msg = "%s operation_type is not allowed."
            logger.error(msg, operation_type.name)
            raise BackendParameterException(msg % operation_type.name)
        return success

    def _find(
        self, parameters: dict, where: List = None, limit: int = None, sort: str = None
    ):
        """Wraps the ClickHouse query method.

        Raises:
            BackendException: raised for any failure.
        """
        sql = """
        SELECT event_id, emission_time, event
        FROM {event_table_name:Identifier}
        """
        if where:
            filter_str = "WHERE 1=1 AND "
            filter_str += """
            AND
            """.join(
                where
            )
            sql += filter_str
        if sort:
            sql += f"\nORDER BY {sort}"

        if limit:
            sql += f"\nLIMIT {limit}"

        parameters["event_table_name"] = self.event_table_name

        try:
            return self.client.query(sql, parameters=parameters).named_results()
        except (ClickHouseError, IndexError, TypeError, ValueError) as error:
            msg = "Failed to execute ClickHouse query"
            logger.error("%s. %s", msg, error)
            raise BackendException(msg, *error.args) from error

    @staticmethod
    def _parse_bytes_to_dict(
        raw_documents: Iterable[bytes], ignore_errors: bool
    ) -> Iterator[dict]:
        """Reads the `raw_documents` Iterable and yields dictionaries."""
        for raw_document in raw_documents:
            try:
                yield json.loads(raw_document)
            except (TypeError, json.JSONDecodeError) as err:
                logger.error("Raised error: %s, for document %s", err, raw_document)
                if ignore_errors:
                    continue
                raise err

    def _read_raw(self, document: Dict[str, Any]) -> bytes:
        """Reads the `documents` Iterable and yields bytes."""
        return json.dumps(document).encode(self.locale_encoding)

    @staticmethod
    def _read_dict(document: Dict[str, Any]) -> dict:
        """Reads the `documents` Iterable and yields dictionaries."""
        return document


class ClickHouseLRSBackend(BaseLRSBackend, ClickHouseDataBackend):
    """ClickhouseDB LRS backend implementation."""

    def query_statements(self, params: StatementParameters) -> StatementQueryResult:
        """Returns the results of a statements query using xAPI parameters."""
        where_clauses = []

        if params.statementId:
            where_clauses.append("event_id = {statementId:UUID}")

        if params.agent:
            where_clauses.append("event.actor.account.name = {agent:String}")

        if params.verb:
            where_clauses.append("event.verb.id = {verb:String}")

        if params.activity:
            where_clauses.append("event.object.objectType = 'Activity'")
            where_clauses.append("event.object.id = {activity:String}")

        if params.since:
            where_clauses.append("emission_time > {since:DateTime64(6)}")

        if params.until:
            where_clauses.append("emission_time <= {until:DateTime64(6)}")

        if params.search_after:
            search_order = ">" if params.ascending else "<"

            where_clauses.append(
                f"(emission_time {search_order} "
                "{search_after:DateTime64(6)}"
                " OR "
                "(emission_time = {search_after:DateTime64(6)}"
                " AND "
                f"event_id {search_order} "
                "{pit_id:UUID}"
                "))"
            )

        sort_order = "ASCENDING" if params.ascending else "DESCENDING"
        order_by = f"emission_time {sort_order}, event_id {sort_order}"

        response = self._find(
            where=where_clauses,
            parameters=params.dict(),
            limit=params.limit,
            sort=order_by,
        )
        response = list(response)
        new_search_after = None
        new_pit_id = None

        if response:
            # Our search after string is a combination of event timestamp and
            # event id, so that we can avoid losing events when they have the
            # same timestamp, and also avoid sending the same event twice.
            new_search_after = response[-1]["emission_time"].isoformat()
            new_pit_id = str(response[-1]["event_id"])

        return StatementQueryResult(
            statements=[document["event"] for document in response],
            search_after=new_search_after,
            pit_id=new_pit_id,
        )

    def query_statements_by_ids(self, ids: List[str]) -> List:
        """Returns the list of matching statement IDs from the database."""

        def chunk_id_list(chunk_size=10000):
            for i in range(0, len(ids), chunk_size):
                yield ids[i : i + chunk_size]

        sql = """
                SELECT event_id
                FROM {table_name:Identifier}
                WHERE event_id IN ({ids:Array(String)})
        """
        query_context = self.client.create_query_context(
            query=sql,
            parameters={"ids": ["1"], "table_name": self.event_table_name},
            column_oriented=True,
        )
        found_ids = []
        try:
            for chunk_ids in chunk_id_list():
                query_context.set_parameter("ids", chunk_ids)
                result = self.client.query(context=query_context).named_results()
                found_ids.extend(result)
            return found_ids
        except (ClickHouseError, IndexError, TypeError, ValueError) as error:
            msg = "Failed to execute ClickHouse query"
            logger.error("%s. %s", msg, error)
            raise BackendException(msg, *error.args) from error
