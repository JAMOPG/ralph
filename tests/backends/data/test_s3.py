"""Tests for Ralph S3 data backend."""

import datetime
import json
import logging

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_s3

from ralph.backends.data.base import BaseOperationType, DataBackendStatus
from ralph.conf import settings
from ralph.exceptions import BackendException, BackendParameterException


@mock_s3
def test_backends_data_s3_backend_instantiation(
    s3_backend,
):  # pylint:disable=invalid-name
    """S3 backend instantiation test.

    Checks that S3 backend doesn't raise exceptions when the connection is
    successful.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket in Moto's 'virtual' AWS account
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    try:
        s3_backend()
    except Exception:  # pylint:disable=broad-except
        pytest.fail("S3 backend should not raise exception on successful connection")


@mock_s3
def test_backends_data_s3_data_backend_status_method(
    s3_backend,
):  # pylint:disable=unused-argument, invalid-name
    """Test the `FSDataBackend.status` method."""

    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket
    bucket_name = "wrong_bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    assert s3_backend().status() == DataBackendStatus.ERROR

    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    assert s3_backend().status() == DataBackendStatus.OK


@mock_s3
def test_backends_data_s3_list_should_yield_archive_names(
    moto_fs, s3_backend, fs, settings_fs
):  # pylint:disable=unused-argument, invalid-name
    """S3 backend list test.

    Tests that given `S3DataBackend.list` method successfully connects to the S3
    data, the S3 backend list method should yield the archives.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    s3_client.put_object(
        Bucket=bucket_name,
        Key="2022-04-29.gz",
        Body=json.dumps({"id": "1", "foo": "bar"}),
    )

    s3_client.put_object(
        Bucket=bucket_name,
        Key="2022-04-30.gz",
        Body=json.dumps({"id": "2", "some": "data"}),
    )

    s3_client.put_object(
        Bucket=bucket_name,
        Key="2022-10-01.gz",
        Body=json.dumps({"id": "3", "other": "info"}),
    )

    listing = [
        {"name": "2022-04-29.gz"},
        {"name": "2022-04-30.gz"},
        {"name": "2022-10-01.gz"},
    ]

    history = [
        {"id": "2022-04-29.gz", "backend": "s3", "command": "read"},
        {"id": "2022-04-30.gz", "backend": "s3", "command": "read"},
    ]

    s3 = s3_backend()
    try:
        response_list = s3.list()
        response_list_new = s3.list(new=True)
        response_list_details = s3.list(details=True)
    except Exception:  # pylint:disable=broad-except
        pytest.fail("S3 backend should not raise exception on successful list")

    fs.create_file(settings.HISTORY_FILE, contents=json.dumps(history))

    assert list(response_list) == [x["name"] for x in listing]
    assert list(response_list_new) == ["2022-10-01.gz"]
    assert [x["Key"] for x in response_list_details] == [x["name"] for x in listing]


@mock_s3
def test_backends_data_s3_list_on_empty_bucket_should_do_nothing(
    moto_fs, s3_backend, fs
):  # pylint:disable=unused-argument, invalid-name
    """S3 backend list test.

    Tests that given `S3DataBackend.list` method successfully connects to the S3
    data, the S3 backend list method on an empty bucket should do nothing.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    listing = []

    history = []

    s3 = s3_backend()
    try:
        response_list = s3.list()
    except Exception:  # pylint:disable=broad-except
        pytest.fail("S3 backend should not raise exception on successful list")

    fs.create_file(settings.HISTORY_FILE, contents=json.dumps(history))

    assert list(response_list) == [x["name"] for x in listing]


@mock_s3
def test_backends_data_s3_list_with_failed_connection_should_log_the_error(
    moto_fs, s3_backend, fs, caplog, settings_fs
):  # pylint:disable=unused-argument, invalid-name
    """S3 backend list test.

    Tests that given `S3DataBackend.list` method fails to retrieve the list of archives,
    the S3 backend list method should log the error and raise a BackendException.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket in Moto's 'virtual' AWS account
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    s3_client.put_object(
        Bucket=bucket_name,
        Key="2022-04-29.gz",
        Body=json.dumps({"id": "1", "foo": "bar"}),
    )

    s3 = s3_backend()

    fs.create_file(settings.HISTORY_FILE, contents=json.dumps([]))
    caplog.set_level(logging.ERROR)
    error = "The specified bucket does not exist"
    msg = f"Failed to list the bucket wrong_name: {error}"

    with pytest.raises(BackendException, match=msg):
        next(s3.list(target="wrong_name"))
    with pytest.raises(BackendException, match=msg):
        next(s3.list(target="wrong_name", new=True))
    with pytest.raises(BackendException, match=msg):
        next(s3.list(target="wrong_name", details=True))
    logger_name = "ralph.backends.data.s3"
    assert caplog.record_tuples == [(logger_name, logging.ERROR, msg)] * 3


@mock_s3
def test_backends_data_s3_read_with_valid_name_should_write_to_history(
    moto_fs, s3_backend, monkeypatch, fs, settings_fs
):  # pylint:disable=unused-argument, invalid-name
    """S3 backend read test.

    Tests that given `S3DataBackend.list` method successfully retrieves from the
    S3 data the object with the provided name (the object exists),
    the S3 backend read method should write the entry to the history.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket in Moto's 'virtual' AWS account
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    raw_body = b"some contents in the body"
    json_body = '{"id":"foo"}'

    s3_client.put_object(
        Bucket=bucket_name,
        Key="2022-09-29.gz",
        Body=raw_body,
    )

    s3_client.put_object(
        Bucket=bucket_name,
        Key="2022-09-30.gz",
        Body=json_body,
    )

    freezed_now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    monkeypatch.setattr("ralph.backends.data.s3.now", lambda: freezed_now)
    fs.create_file(settings.HISTORY_FILE, contents=json.dumps([]))

    s3 = s3_backend()
    list(
        s3.read(
            query="2022-09-29.gz",
            target=bucket_name,
            chunk_size=1000,
            raw_output=True,
        )
    )

    assert {
        "backend": "s3",
        "action": "read",
        "id": f"{bucket_name}/2022-09-29.gz",
        "size": len(raw_body),
        "timestamp": freezed_now,
    } in s3.history

    list(
        s3.read(
            query="2022-09-30.gz",
            raw_output=False,
        )
    )

    assert {
        "backend": "s3",
        "action": "read",
        "id": f"{bucket_name}/2022-09-30.gz",
        "size": len(json_body),
        "timestamp": freezed_now,
    } in s3.history


@mock_s3
def test_backends_data_s3_read_with_invalid_output_should_log_the_error(
    moto_fs, s3_backend, fs, caplog, settings_fs
):  # pylint:disable=unused-argument, invalid-name
    """S3 backend read test.

    Tests that given `S3DataBackend.read` method fails to serialize the object, the
    S3 backend read method should log the error, not write to history and raise a
    BackendException.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket in Moto's 'virtual' AWS account
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    body = b"some contents in the body"

    s3_client.put_object(
        Bucket=bucket_name,
        Key="2022-09-29.gz",
        Body=body,
    )

    fs.create_file(settings.HISTORY_FILE, contents=json.dumps([]))
    caplog.set_level(logging.ERROR)

    with pytest.raises(BackendException):
        s3 = s3_backend()
        list(s3.read(query="2022-09-29.gz", raw_output=False))

    logger_name = "ralph.backends.data.s3"
    msg = "Raised error: Expecting value: line 1 column 1 (char 0)"
    assert caplog.record_tuples == [(logger_name, logging.ERROR, msg)]
    assert s3.history == []


@mock_s3
def test_backends_data_s3_read_with_invalid_name_should_log_the_error(
    moto_fs, s3_backend, fs, caplog, settings_fs
):  # pylint:disable=unused-argument, invalid-name
    """S3 backend read test.

    Tests that given `S3DataBackend.read` method fails to retrieve from the S3
    data the object with the provided name (the object does not exists on S3),
    the S3 backend read method should log the error, not write to history and raise a
    BackendException.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket in Moto's 'virtual' AWS account
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    body = b"some contents in the body"

    s3_client.put_object(
        Bucket=bucket_name,
        Key="2022-09-29.gz",
        Body=body,
    )

    fs.create_file(settings.HISTORY_FILE, contents=json.dumps([]))
    caplog.set_level(logging.ERROR)

    with pytest.raises(BackendParameterException):
        s3 = s3_backend()
        list(s3.read(query=None, target=bucket_name))

    logger_name = "ralph.backends.data.s3"
    msg = "`query` argument is required to read."
    assert caplog.record_tuples == [(logger_name, logging.ERROR, msg)]
    assert s3.history == []


@mock_s3
def test_backends_data_s3_read_with_wrong_name_should_log_the_error(
    moto_fs, s3_backend, fs, caplog, settings_fs
):  # pylint:disable=unused-argument, invalid-name
    """S3 backend read test.

    Tests that given `S3DataBackend.read` method fails to retrieve from the S3
    data the object with the provided name (the object does not exists on S3),
    the S3 backend read method should log the error, not write to history and raise a
    BackendException.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket in Moto's 'virtual' AWS account
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    body = b"some contents in the body"

    s3_client.put_object(
        Bucket=bucket_name,
        Key="2022-09-29.gz",
        Body=body,
    )

    fs.create_file(settings.HISTORY_FILE, contents=json.dumps([]))
    caplog.set_level(logging.ERROR)
    error = "The specified key does not exist."

    with pytest.raises(BackendException):
        s3 = s3_backend()
        list(s3.read(query="invalid_name.gz", target=bucket_name))
    logger_name = "ralph.backends.data.s3"
    msg = f"Failed to download invalid_name.gz: {error}"
    assert caplog.record_tuples == [(logger_name, logging.ERROR, msg)]
    assert s3.history == []


# pylint: disable=line-too-long
@pytest.mark.parametrize(
    "operation_type",
    [None, BaseOperationType.CREATE, BaseOperationType.INDEX],
)
@mock_s3
def test_backends_data_s3_write_method_with_parameter_error(  # noqa
    moto_fs, operation_type, s3_backend, monkeypatch, fs, caplog, settings_fs
):  # pylint:disable=unused-argument, invalid-name, too-many-arguments, too-many-locals
    """Test the `S3DataBackend.write` method, given a target matching an
    existing object and a `CREATE` or `INDEX` `operation_type`, should raise a
    `FileExistsError`.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket in Moto's 'virtual' AWS account
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    body = b"some contents in the body"

    s3_client.put_object(
        Bucket=bucket_name,
        Key="2022-09-29.gz",
        Body=body,
    )

    object_name = "2022-09-29.gz"
    some_content = b"some contents in the stream file to upload"

    fs.create_file(settings.HISTORY_FILE, contents=json.dumps([]))
    caplog.set_level(logging.ERROR)

    with pytest.raises(BackendException):
        s3 = s3_backend()
        s3.write(data=some_content, target=object_name, operation_type=operation_type)
    logger_name = "ralph.backends.data.s3"
    msg = (
        f"{object_name} already exists and overwrite is not allowed for operation"
        f" {operation_type if operation_type is not None else BaseOperationType.CREATE}"
    )
    assert caplog.record_tuples == [(logger_name, logging.ERROR, msg)]
    assert s3.history == []


# pylint: disable=line-too-long
@pytest.mark.parametrize(
    "operation_type",
    [BaseOperationType.APPEND, BaseOperationType.DELETE],
)
def test_backends_data_s3_data_backend_write_method_with_append_or_delete_operation(
    s3_backend, operation_type
):
    """Test the `S3DataBackend.write` method, given an `APPEND`
    `operation_type`, should raise a `BackendParameterException`.
    """
    # pylint: disable=invalid-name
    backend = s3_backend()
    with pytest.raises(
        BackendParameterException,
        match=f"{operation_type.name} operation_type is not allowed.",
    ):
        backend.write(data=[b"foo"], operation_type=operation_type)


# pylint: disable=line-too-long
@pytest.mark.parametrize(
    "operation_type",
    [BaseOperationType.CREATE, BaseOperationType.INDEX],
)
@mock_s3
def test_backends_data_s3_write_method_with_create_index_operation(  # noqa
    moto_fs, operation_type, s3_backend, monkeypatch, fs, settings_fs
):  # pylint:disable=unused-argument, invalid-name, too-many-arguments, too-many-locals
    """Test the `S3DataBackend.write` method, given a target matching an
    existing object and a `CREATE` or `INDEX` `operation_type`, should add
    an entry to the History.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket in Moto's 'virtual' AWS account
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    freezed_now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    monkeypatch.setattr("ralph.backends.data.s3.now", lambda: freezed_now)
    fs.create_file(settings.HISTORY_FILE, contents=json.dumps([]))

    object_name = "new-archive.gz"
    some_content = b"some contents in the stream file to upload"

    s3 = s3_backend()
    response = s3.write(
        data=[some_content],
        target=object_name,
        operation_type=operation_type,
    )

    assert response == 1
    assert {
        "backend": "s3",
        "action": "write",
        "operation_type": operation_type.value,
        "id": f"{bucket_name}/{object_name}",
        "size": len(some_content),
        "timestamp": freezed_now,
    } in s3.history

    object_name = "new-archive2.gz"
    other_content = {"some": "content"}

    response = s3.write(
        data=[other_content],
        target=object_name,
        operation_type=operation_type,
    )

    assert response == 1
    assert {
        "backend": "s3",
        "action": "write",
        "operation_type": operation_type.value,
        "id": f"{bucket_name}/{object_name}",
        "size": len(bytes(f"{json.dumps(other_content)}\n", encoding="utf8")),
        "timestamp": freezed_now,
    } in s3.history


@mock_s3
def test_backends_data_s3_write_method_with_no_data_should_skip(  # noqa
    s3_backend,
):  # pylint:disable=unused-argument, invalid-name, too-many-arguments, too-many-locals
    """Test the `S3DataBackend.write` method, given no data to write,
    should skip and return 0.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket in Moto's 'virtual' AWS account
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    object_name = "new-archive.gz"

    s3 = s3_backend()
    response = s3.write(
        data=[],
        target=object_name,
        operation_type=BaseOperationType.CREATE,
    )
    assert response == 0


@mock_s3
def test_backends_data_s3_write_method_with_failure_should_log_the_error(
    moto_fs, s3_backend, fs, caplog, settings_fs
):  # pylint:disable=unused-argument, invalid-name,too-many-arguments
    """Test the `S3DataBackend.write` method, given a connection failure,
    should raise a `BackendException`.
    """
    # Regions outside of us-east-1 require the appropriate LocationConstraint
    s3_client = boto3.client("s3", region_name="us-east-1")
    # Create a valid bucket in Moto's 'virtual' AWS account
    bucket_name = "bucket_name"
    s3_client.create_bucket(Bucket=bucket_name)

    object_name = "new-archive.gz"
    body = b"some contents in the body"
    error = "Failed to upload"

    def raise_client_error(*args, **kwargs):
        raise ClientError({"Error": {}}, "error")

    s3 = s3_backend()
    s3.client.put_object = raise_client_error

    with pytest.raises(BackendException, match=error):
        s3.write(
            data=[body],
            target=object_name,
            operation_type=BaseOperationType.CREATE,
        )
