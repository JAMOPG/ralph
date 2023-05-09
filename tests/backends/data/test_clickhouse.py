"""Tests for Ralph clickhouse database backend."""

import json
import logging
import uuid
from datetime import datetime, timedelta

import pytest
import pytz
from clickhouse_connect.driver.exceptions import ClickHouseError
from clickhouse_connect.driver.httpclient import HttpClient

from ralph.backends.data.base import BaseOperationType, DataBackendStatus
from ralph.backends.data.clickhouse import (
    ClickHouseDataBackend,
    ClickHouseLRSBackend,
    ClickHouseQuery,
)
from ralph.backends.lrs.base import StatementParameters
from ralph.exceptions import (
    BackendException,
    BackendParameterException,
    BadFormatException,
)

from tests.fixtures.backends import (
    CLICKHOUSE_TEST_DATABASE,
    CLICKHOUSE_TEST_HOST,
    CLICKHOUSE_TEST_PORT,
    CLICKHOUSE_TEST_TABLE_NAME,
)


def test_backends_data_clickhouse_data_backend_instantiation_with_settings():
    """Test the ClickHouse backend instantiation."""
    assert ClickHouseDataBackend.name == "clickhouse"

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)

    assert isinstance(backend.client, HttpClient)
    assert backend.database == CLICKHOUSE_TEST_DATABASE


# pylint: disable=unused-argument
def test_backends_db_clickhouse_get_method(clickhouse):
    """Test the clickhouse backend get method."""
    # Create records
    date_1 = (datetime.now() - timedelta(seconds=3)).isoformat()
    date_2 = (datetime.now() - timedelta(seconds=2)).isoformat()
    date_3 = (datetime.now() - timedelta(seconds=1)).isoformat()

    statements = [
        {"id": str(uuid.uuid4()), "bool": 1, "timestamp": date_1},
        {"id": str(uuid.uuid4()), "bool": 0, "timestamp": date_2},
        {"id": str(uuid.uuid4()), "bool": 1, "timestamp": date_3},
    ]
    documents = list(ClickHouseDataBackend.to_documents(statements))

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)
    backend.bulk_import(documents)

    results = list(backend.read())
    assert len(results) == 3
    assert results[0]["event"] == statements[0]
    assert results[1]["event"] == statements[1]
    assert results[2]["event"] == statements[2]

    results = list(backend.read(chunk_size=1))
    assert len(results) == 1
    results = list(backend.read(chunk_size=3))
    assert len(results) == 3
    assert results[0]["event"] == statements[0]
    assert results[1]["event"] == statements[1]
    assert results[2]["event"] == statements[2]

    results = list(backend.read(chunk_size=1000))
    assert len(results) == 3
    assert results[0]["event"] == statements[0]
    assert results[1]["event"] == statements[1]
    assert results[2]["event"] == statements[2]

    results = list(backend.read(raw_output=True))
    assert len(results) == 3
    assert isinstance(results[0], bytes)
    assert json.loads(results[0])["event"] == statements[0]


# pylint: disable=unused-argument
def test_backends_db_clickhouse_get_method_on_timestamp_boundary(clickhouse):
    """Make sure no rows are lost on pagination if they have the same timestamp."""
    # Create records
    date_1 = "2023-02-17T16:55:17.721627"
    date_2 = "2023-02-17T16:55:14.721633"

    # Using fixed UUIDs here to make sure they always come back in the same order
    statements = [
        {"id": "9e1310cb-875f-4b14-9410-6443399be63c", "timestamp": date_1},
        {"id": "f93b5796-e0b1-4221-a867-7c2c820f9b68", "timestamp": date_2},
        {"id": "af8effc0-26eb-42b6-8f64-3a0d6b26c16c", "timestamp": date_2},
    ]
    documents = list(ClickHouseDataBackend.to_documents(statements))

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseLRSBackend(settings)
    backend.bulk_import(documents)

    # First get all 3 rows with default settings
    results = backend.query_statements(StatementParameters())
    result_statements = results.statements
    assert len(result_statements) == 3
    assert result_statements[0] == statements[0]
    assert result_statements[1] == statements[1]
    assert result_statements[2] == statements[2]

    # Next get them one at a time, starting with the first
    params = StatementParameters(limit=1)
    results = backend.query_statements(params)
    result_statements = results.statements
    assert len(result_statements) == 1
    assert result_statements[0] == statements[0]

    # Next get the second row with an appropriate search after
    params = StatementParameters(
        limit=1, search_after=results.search_after, pit_id=results.pit_id
    )
    results = backend.query_statements(params)
    result_statements = results.statements
    assert len(result_statements) == 1
    assert result_statements[0] == statements[1]

    # And finally the third
    params = StatementParameters(
        limit=1, search_after=results.search_after, pit_id=results.pit_id
    )
    results = backend.query_statements(params)
    result_statements = results.statements
    assert len(result_statements) == 1
    assert result_statements[0] == statements[2]


# pylint: disable=unused-argument
def test_backends_db_clickhouse_get_method_with_a_custom_query(clickhouse):
    """Test the clickhouse backend get method with a custom query."""
    date_1 = (datetime.now() - timedelta(seconds=3)).isoformat()
    date_2 = (datetime.now() - timedelta(seconds=2)).isoformat()
    date_3 = (datetime.now() - timedelta(seconds=1)).isoformat()

    statements = [
        {"id": str(uuid.uuid4()), "bool": 1, "timestamp": date_1},
        {"id": str(uuid.uuid4()), "bool": 0, "timestamp": date_2},
        {"id": str(uuid.uuid4()), "bool": 1, "timestamp": date_3},
    ]
    documents = list(ClickHouseDataBackend.to_documents(statements))

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)
    backend.bulk_import(documents)

    # Test filtering
    query = ClickHouseQuery(where_clause="event.bool = 1")
    results = list(backend.read(query=query))
    assert len(results) == 2
    assert results[0]["event"] == statements[0]
    assert results[1]["event"] == statements[2]

    # Test fields
    query = ClickHouseQuery(return_fields=["event_id", "event.bool"])
    results = list(backend.read(query=query))
    assert len(results) == 3
    assert len(results[0]) == 2
    assert results[0]["event_id"] == documents[0][0]
    assert results[0]["event.bool"] == statements[0]["bool"]
    assert results[1]["event_id"] == documents[1][0]
    assert results[1]["event.bool"] == statements[1]["bool"]
    assert results[2]["event_id"] == documents[2][0]
    assert results[2]["event.bool"] == statements[2]["bool"]

    # Test filtering and projection
    query = ClickHouseQuery(
        where_clause="event.bool = 0", return_fields=["event_id", "event.bool"]
    )
    results = list(backend.read(query=query))
    assert len(results) == 1
    assert len(results[0]) == 2
    assert results[0]["event_id"] == documents[1][0]
    assert results[0]["event.bool"] == statements[1]["bool"]


def test_backends_db_clickhouse_data_backend_list_method(clickhouse):
    """Test the clickhouse backend list method."""

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)

    assert list(backend.list(details=True)) == [{"name": CLICKHOUSE_TEST_TABLE_NAME}]
    assert list(backend.list(details=False)) == [CLICKHOUSE_TEST_TABLE_NAME]


def test_backends_db_clickhouse_data_backend_to_documents_method_with_invalid_timestamp(
    clickhouse,
):
    """Test the clickhouse backend to_documents method with an invalid timestamp."""
    valid_timestamp = (datetime.now() - timedelta(seconds=3)).isoformat()
    invalid_timestamp = "This is not a valid timestamp!"
    invalid_statement = {
        "id": str(uuid.uuid4()),
        "bool": 0,
        "timestamp": invalid_timestamp,
    }

    statements = [
        {"id": str(uuid.uuid4()), "bool": 1, "timestamp": valid_timestamp},
        invalid_statement,
    ]
    documents = ClickHouseDataBackend.to_documents(statements, ignore_errors=False)

    assert str(next(documents)[0]) == statements[0]["id"]

    with pytest.raises(
        BadFormatException,
        match=f"Statement has an invalid or missing id or "
        f"timestamp field: {invalid_statement}",
    ):
        next(documents)


def test_backends_db_clickhouse_to_documents_method():
    """Test the clickhouse backend to_documents method."""
    native_statements = [
        {
            "id": uuid.uuid4(),
            "timestamp": datetime.now(pytz.utc) - timedelta(seconds=1),
        },
        {"id": uuid.uuid4(), "timestamp": datetime.now(pytz.utc)},
    ]
    # Add a duplicate row to ensure statement transformation is idempotent
    native_statements.append(native_statements[1])

    statements = [
        {"id": str(x["id"]), "timestamp": x["timestamp"].isoformat()}
        for x in native_statements
    ]
    documents = ClickHouseDataBackend.to_documents(statements)

    doc = next(documents)
    assert doc[0] == native_statements[0]["id"]
    assert doc[1] == native_statements[0]["timestamp"].replace(tzinfo=pytz.UTC)
    assert doc[2] == statements[0]

    doc = next(documents)
    assert doc[0] == native_statements[1]["id"]
    assert doc[1] == native_statements[1]["timestamp"].replace(tzinfo=pytz.UTC)
    assert doc[2] == statements[1]

    # Identical statement ID produces the same Object
    doc = next(documents)
    assert doc[0] == native_statements[1]["id"]
    assert doc[1] == native_statements[1]["timestamp"].replace(tzinfo=pytz.UTC)
    assert doc[2] == statements[1]


def test_backends_db_clickhouse_to_documents_method_when_statement_has_no_id(
    caplog,
):
    """Test the clickhouse to_documents method when a statement has no id field."""
    timestamp = {"timestamp": "2022-06-27T15:36:50"}
    statements = [
        {"id": str(uuid.uuid4()), **timestamp},
        {**timestamp},
        {"id": str(uuid.uuid4()), **timestamp},
    ]

    documents = ClickHouseDataBackend.to_documents(statements, ignore_errors=False)
    assert next(documents)[0] == uuid.UUID(statements[0]["id"], version=4)

    with pytest.raises(
        BadFormatException,
        match="Statement has an invalid or missing id or " "timestamp field",
    ):
        next(documents)

    documents = ClickHouseDataBackend.to_documents(statements, ignore_errors=True)
    assert next(documents)[0] == uuid.UUID(statements[0]["id"], version=4)
    assert next(documents)[0] == uuid.UUID(statements[2]["id"], version=4)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert (
        "Statement has an invalid or missing id or timestamp field"
        in caplog.records[0].message
    )


def test_backends_db_clickhouse_to_documents_method_when_statement_has_no_timestamp(
    caplog,
):
    """Tests the clickhouse to_documents method when a statement has no timestamp."""
    timestamp = {"timestamp": "2022-06-27T15:36:50"}
    statements = [
        {"id": str(uuid.uuid4()), **timestamp},
        {"id": str(uuid.uuid4())},
        {"id": str(uuid.uuid4()), **timestamp},
    ]

    documents = ClickHouseDataBackend.to_documents(statements, ignore_errors=False)
    assert next(documents)[0] == uuid.UUID(statements[0]["id"], version=4)

    with pytest.raises(
        BadFormatException,
        match="Statement has an invalid or missing id or " "timestamp field",
    ):
        next(documents)

    documents = ClickHouseDataBackend.to_documents(statements, ignore_errors=True)
    assert next(documents)[0] == uuid.UUID(statements[0]["id"], version=4)
    assert next(documents)[0] == uuid.UUID(statements[2]["id"], version=4)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert (
        "Statement has an invalid or missing id or timestamp field"
        in caplog.records[0].message
    )


def test_backends_db_clickhouse_to_documents_method_with_invalid_timestamp(
    caplog,
):
    """Tests the clickhouse to_documents method with an invalid timestamp."""
    valid_timestamp = {"timestamp": "2022-06-27T15:36:50"}
    valid_timestamp_2 = {"timestamp": "2022-06-27T15:36:51"}
    invalid_timestamp = {"timestamp": "This is not a valid timestamp!"}
    invalid_statement = {"id": str(uuid.uuid4()), **invalid_timestamp}
    statements = [
        {"id": str(uuid.uuid4()), **valid_timestamp},
        invalid_statement,
        {"id": str(uuid.uuid4()), **valid_timestamp_2},
    ]

    with pytest.raises(
        BadFormatException,
        match="Statement has an invalid or missing id or timestamp field",
    ):
        # Since this is a generator the error won't happen until the failing
        # statement is processed.
        list(ClickHouseDataBackend.to_documents(statements, ignore_errors=False))

    documents = ClickHouseDataBackend.to_documents(statements, ignore_errors=True)
    assert next(documents)[0] == uuid.UUID(statements[0]["id"], version=4)
    assert next(documents)[0] == uuid.UUID(statements[2]["id"], version=4)
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert (
        "Statement has an invalid or missing id or timestamp field"
        in caplog.records[0].message
    )


def test_backends_db_clickhouse_bulk_import_method(clickhouse):
    """Test the clickhouse backend bulk_import method."""
    # pylint: disable=unused-argument

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)

    native_statements = [
        {"id": uuid.uuid4(), "timestamp": datetime.utcnow() - timedelta(seconds=1)},
        {"id": uuid.uuid4(), "timestamp": datetime.utcnow()},
    ]
    statements = [
        {"id": str(x["id"]), "timestamp": x["timestamp"].isoformat()}
        for x in native_statements
    ]

    docs = list(ClickHouseDataBackend.to_documents(statements))
    backend.bulk_import(docs)

    res = backend.client.query(f"SELECT * FROM {CLICKHOUSE_TEST_TABLE_NAME}")
    result = res.named_results()

    db_statement = next(result)
    assert db_statement["event_id"] == native_statements[0]["id"]
    assert db_statement["emission_time"] == native_statements[0]["timestamp"]
    assert db_statement["event"] == statements[0]

    db_statement = next(result)
    assert db_statement["event_id"] == native_statements[1]["id"]
    assert db_statement["emission_time"] == native_statements[1]["timestamp"]
    assert db_statement["event"] == statements[1]


def test_backends_db_clickhouse_bulk_import_method_with_duplicated_key(
    clickhouse,
):
    """Test the clickhouse backend bulk_import method with a duplicated key conflict."""
    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)

    timestamp = {"timestamp": "2022-06-27T15:36:50"}
    dupe_id = str(uuid.uuid4())
    statements = [
        {"id": str(uuid.uuid4()), **timestamp},
        {"id": dupe_id, **timestamp},
        {"id": dupe_id, **timestamp},
    ]
    documents = list(ClickHouseDataBackend.to_documents(statements))
    with pytest.raises(BackendException, match="Duplicate IDs found in batch"):
        backend.bulk_import(documents)

    success = backend.bulk_import(documents, ignore_errors=True)
    assert success == 0


def test_backends_db_clickhouse_bulk_import_method_import_partial_chunks_on_error(
    clickhouse,
):
    """Test the clickhouse bulk_import method imports partial chunks while raising a
    BulkWriteError and ignoring errors.
    """
    # pylint: disable=unused-argument

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)

    # Identical statement ID produces the same ObjectId, leading to a
    # duplicated key write error while trying to bulk import this batch
    timestamp = {"timestamp": "2022-06-27T15:36:50"}
    dupe_id = str(uuid.uuid4())
    statements = [
        {"id": str(uuid.uuid4()), **timestamp},
        {"id": dupe_id, **timestamp},
        {"id": str(uuid.uuid4()), **timestamp},
        {"id": str(uuid.uuid4()), **timestamp},
        {"id": dupe_id, **timestamp},
    ]
    documents = list(ClickHouseDataBackend.to_documents(statements))
    assert backend.bulk_import(documents, ignore_errors=True) == 0


def test_backends_db_clickhouse_put_method(clickhouse):
    """Test the clickhouse backend put method."""
    sql = f"""SELECT count(*) FROM {CLICKHOUSE_TEST_TABLE_NAME}"""
    result = clickhouse.query(sql).result_set
    assert result[0][0] == 0

    native_statements = [
        {"id": uuid.uuid4(), "timestamp": datetime.utcnow() - timedelta(seconds=1)},
        {"id": uuid.uuid4(), "timestamp": datetime.utcnow()},
    ]
    statements = [
        {"id": str(x["id"]), "timestamp": x["timestamp"].isoformat()}
        for x in native_statements
    ]
    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)
    success = backend.write(statements, target=CLICKHOUSE_TEST_TABLE_NAME)

    assert success == 2

    result = clickhouse.query(sql).result_set
    assert result[0][0] == 2

    sql = f"""SELECT * FROM {CLICKHOUSE_TEST_TABLE_NAME} ORDER BY event.timestamp"""
    result = list(clickhouse.query(sql).named_results())

    assert result[0]["event_id"] == native_statements[0]["id"]
    assert result[0]["emission_time"] == native_statements[0]["timestamp"]
    assert result[0]["event"] == statements[0]

    assert result[1]["event_id"] == native_statements[1]["id"]
    assert result[1]["emission_time"] == native_statements[1]["timestamp"]
    assert result[1]["event"] == statements[1]


def test_backends_db_clickhouse_put_method_bytes(clickhouse):
    """Test the clickhouse backend put method."""
    sql = f"""SELECT count(*) FROM {CLICKHOUSE_TEST_TABLE_NAME}"""
    result = clickhouse.query(sql).result_set
    assert result[0][0] == 0

    native_statements = [
        {"id": uuid.uuid4(), "timestamp": datetime.utcnow() - timedelta(seconds=1)},
        {"id": uuid.uuid4(), "timestamp": datetime.utcnow()},
    ]
    statements = [
        {"id": str(x["id"]), "timestamp": x["timestamp"].isoformat()}
        for x in native_statements
    ]
    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)
    byte_data = []
    for item in statements:
        json_str = json.dumps(item, separators=(",", ":"), ensure_ascii=False)
        byte_data.append(json_str.encode("utf-8"))
    success = backend.write(byte_data, target=CLICKHOUSE_TEST_TABLE_NAME)

    assert success == 2

    result = clickhouse.query(sql).result_set
    assert result[0][0] == 2

    sql = f"""SELECT * FROM {CLICKHOUSE_TEST_TABLE_NAME} ORDER BY event.timestamp"""
    result = list(clickhouse.query(sql).named_results())

    assert result[0]["event_id"] == native_statements[0]["id"]
    assert result[0]["emission_time"] == native_statements[0]["timestamp"]
    assert result[0]["event"] == statements[0]

    assert result[1]["event_id"] == native_statements[1]["id"]
    assert result[1]["emission_time"] == native_statements[1]["timestamp"]
    assert result[1]["event"] == statements[1]


def test_backends_db_clickhouse_put_method_bytes_failed(clickhouse):
    """Test the clickhouse backend put method."""
    sql = f"""SELECT count(*) FROM {CLICKHOUSE_TEST_TABLE_NAME}"""
    result = clickhouse.query(sql).result_set
    assert result[0][0] == 0

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)
    byte_data = []
    json_str = "failed_json_str"
    byte_data.append(json_str.encode("utf-8"))

    success = 0
    with pytest.raises(json.JSONDecodeError):
        success = backend.write(byte_data)

    assert success == 0

    result = clickhouse.query(sql).result_set
    assert result[0][0] == 0

    success = backend.write(byte_data, ignore_errors=True)
    assert success == 0

    result = clickhouse.query(sql).result_set
    assert result[0][0] == 0


def test_backends_db_clickhouse_put_method_empty(clickhouse):
    """Test the clickhouse backend put method."""
    sql = f"""SELECT count(*) FROM {CLICKHOUSE_TEST_TABLE_NAME}"""
    result = clickhouse.query(sql).result_set
    assert result[0][0] == 0

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)
    success = backend.write([], target=CLICKHOUSE_TEST_TABLE_NAME)

    assert success == 0

    result = clickhouse.query(sql).result_set
    assert result[0][0] == 0


def test_backends_db_clickhouse_put_method_wrong_operation_type(clickhouse):
    """Test the clickhouse backend put method."""
    sql = f"""SELECT count(*) FROM {CLICKHOUSE_TEST_TABLE_NAME}"""
    result = clickhouse.query(sql).result_set
    assert result[0][0] == 0

    native_statements = [
        {"id": uuid.uuid4(), "timestamp": datetime.utcnow() - timedelta(seconds=1)},
        {"id": uuid.uuid4(), "timestamp": datetime.utcnow()},
    ]
    statements = [
        {"id": str(x["id"]), "timestamp": x["timestamp"].isoformat()}
        for x in native_statements
    ]

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)
    with pytest.raises(
        BackendParameterException,
        match=f"{BaseOperationType.APPEND.name} operation_type is not allowed.",
    ):
        backend.write(data=statements, operation_type=BaseOperationType.APPEND)


def test_backends_db_clickhouse_put_method_with_custom_chunk_size(clickhouse):
    """Test the clickhouse backend put method with a custom chunk_size."""
    sql = f"""SELECT count(*) FROM {CLICKHOUSE_TEST_TABLE_NAME}"""
    result = clickhouse.query(sql).result_set
    assert result[0][0] == 0

    native_statements = [
        {"id": uuid.uuid4(), "timestamp": datetime.utcnow() - timedelta(seconds=1)},
        {"id": uuid.uuid4(), "timestamp": datetime.utcnow()},
    ]
    statements = [
        {"id": str(x["id"]), "timestamp": x["timestamp"].isoformat()}
        for x in native_statements
    ]

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)
    success = backend.write(statements, chunk_size=1)
    assert success == 2

    result = clickhouse.query(sql).result_set
    assert result[0][0] == 2

    sql = f"""SELECT * FROM {CLICKHOUSE_TEST_TABLE_NAME} ORDER BY event.timestamp"""
    result = list(clickhouse.query(sql).named_results())

    assert result[0]["event_id"] == native_statements[0]["id"]
    assert result[0]["emission_time"] == native_statements[0]["timestamp"]
    assert result[0]["event"] == statements[0]

    assert result[1]["event_id"] == native_statements[1]["id"]
    assert result[1]["emission_time"] == native_statements[1]["timestamp"]
    assert result[1]["event"] == statements[1]


def test_backends_database_clickhouse_query_statements(monkeypatch, caplog, clickhouse):
    """Tests the ClickHouse backend query_statements method,
    given a search query failure,
    should raise a BackendException and log the error.
    """
    # pylint: disable=unused-argument,use-implicit-booleaness-not-comparison

    # Instantiate ClickHouse Databases

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseLRSBackend(settings)

    # Insert documents
    meta = {
        "actor": {"account": {"name": "test_name"}},
        "verb": {"id": "verb_id"},
        "object": {"id": "http://example.com", "objectType": "Activity"},
    }
    date_str = "09-19-2022"
    datetime_object = datetime.strptime(date_str, "%m-%d-%Y").utcnow()
    native_statements = [
        {"id": uuid.uuid4(), "timestamp": datetime_object - timedelta(seconds=1)},
        {"id": uuid.uuid4(), "timestamp": datetime_object},
    ]
    statements = [
        {"id": str(x["id"]), "timestamp": x["timestamp"].isoformat(), **meta}
        for x in native_statements
    ]
    success = backend.write(statements, chunk_size=1)
    assert success == 2

    statement_parameters = StatementParameters()
    statement_parameters.activity = "http://example.com"
    statement_parameters.since = "2022-01-01T15:36:50"
    statement_parameters.until = "2025-12-01T15:36:50"
    statement_parameters.search_after = "2022-01-01T15:36:50"
    statement_parameters.limit = 25
    statement_parameters.ascending = True
    statement_parameters.agent = "test_name"
    statement_parameters.verb = "verb_id"
    statement_parameters.statementId = statements[0]["id"]
    statement_parameters.pit_id = statements[0]["id"]
    statement_query_result = backend.query_statements(statement_parameters)

    assert len(statement_query_result.statements) > 0


def test_backends_db_clickhouse_query_statements_with_search_query_failure(
    monkeypatch, caplog, clickhouse
):
    """Tests the clickhouse query_statements method, given a search query failure,
    should raise a BackendException and log the error.
    """
    # pylint: disable=unused-argument

    def mock_query(*_, **__):
        """Mocks the ClickHouseClient.collection.find method."""
        raise ClickHouseError("Something is wrong")

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseLRSBackend(settings)
    monkeypatch.setattr(backend.client, "query", mock_query)

    caplog.set_level(logging.ERROR)

    msg = "'Failed to execute ClickHouse query', 'Something is wrong'"
    with pytest.raises(BackendException, match=msg):
        backend.query_statements(StatementParameters())

    logger_name = "ralph.backends.data.clickhouse"
    msg = "Failed to execute ClickHouse query. Something is wrong"
    assert caplog.record_tuples == [(logger_name, logging.ERROR, msg)]


def test_backends_db_clickhouse_query_statements_by_ids_with_search_query_failure(
    monkeypatch, caplog, clickhouse
):
    """Tests the clickhouse backend query_statements_by_ids method, given a search query
    failure, should raise a BackendException and log the error.
    """
    # pylint: disable=unused-argument

    def mock_find(**_):
        """Mocks the ClickHouseClient.collection.find method."""
        raise ClickHouseError("Something is wrong")

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseLRSBackend(settings)
    monkeypatch.setattr(backend.client, "query", mock_find)
    caplog.set_level(logging.ERROR)

    msg = "'Failed to execute ClickHouse query', 'Something is wrong'"
    with pytest.raises(BackendException, match=msg):
        backend.query_statements_by_ids(
            [
                "abcdefg",
            ]
        )

    logger_name = "ralph.backends.data.clickhouse"
    msg = "Failed to execute ClickHouse query. Something is wrong"
    assert caplog.record_tuples == [(logger_name, logging.ERROR, msg)]


def test_backends_db_clickhouse_query_statements_by_ids_with_search_query(
    monkeypatch, caplog, clickhouse
):
    """Tests the ClickHouse backend query_statements_by_ids method, given a valid search
    query, should execute the query uniquely on the specified collection and return the
    expected results.
    """
    # pylint: disable=unused-argument,use-implicit-booleaness-not-comparison

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseLRSBackend(settings)

    date_str = "09-19-2022"
    datetime_object = datetime.strptime(date_str, "%m-%d-%Y").utcnow()
    native_statements = [
        {"id": uuid.uuid4(), "timestamp": datetime_object - timedelta(seconds=1)},
        {"id": uuid.uuid4(), "timestamp": datetime_object},
    ]
    statements = [
        {"id": str(x["id"]), "timestamp": x["timestamp"].isoformat()}
        for x in native_statements
    ]
    success = backend.write(statements, chunk_size=1)
    assert success == 2

    statement_query_result = backend.query_statements_by_ids([statements[0]["id"]])
    assert len(statement_query_result) == 1
    assert statement_query_result[0]["event_id"] == native_statements[0]["id"]


def test_backends_db_clickhouse_status(clickhouse, monkeypatch):
    """Test the ClickHouse status method.

    As pyclickhouse is monkeypatching the ClickHouse client to add admin object, it's
    barely untestable. 😢
    """
    # pylint: disable=unused-argument

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)
    assert backend.status() == DataBackendStatus.OK

    def mock_query(*_, **__):
        """Mocks the ClickHouseClient.query method."""
        raise ClickHouseError("Something is wrong")

    settings = ClickHouseDataBackend.settings_class(
        HOST=CLICKHOUSE_TEST_HOST,
        PORT=CLICKHOUSE_TEST_PORT,
        DATABASE=CLICKHOUSE_TEST_DATABASE,
        EVENT_TABLE_NAME=CLICKHOUSE_TEST_TABLE_NAME,
    )
    backend = ClickHouseDataBackend(settings)
    monkeypatch.setattr(backend.client, "query", mock_query)
    assert backend.status() == DataBackendStatus.AWAY
