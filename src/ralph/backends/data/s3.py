"""S3 data backend for Ralph."""

import json
import logging
from itertools import chain
from typing import Iterable, Iterator, Union
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError, ParamValidationError
from botocore.response import StreamingBody

from ralph.backends.data.base import (
    BaseDataBackend,
    BaseDataBackendSettings,
    BaseOperationType,
    BaseQuery,
    DataBackendStatus,
    enforce_query_checks,
)
from ralph.backends.mixins import HistoryMixin
from ralph.conf import BaseSettingsConfig
from ralph.exceptions import BackendException, BackendParameterException
from ralph.utils import now

logger = logging.getLogger(__name__)


class S3DataBackendSettings(BaseDataBackendSettings):
    """Represents the S3 data backend default configuration."""

    class Config(BaseSettingsConfig):
        """Pydantic Configuration."""

        env_prefix = "RALPH_BACKENDS__DATA__S3__"

    ACCESS_KEY_ID: str = None
    SECRET_ACCESS_KEY: str = None
    SESSION_TOKEN: str = None
    DEFAULT_REGION: str = None
    DEFAULT_BUCKET_NAME: str = None
    DEFAULT_CHUNK_SIZE: int = 4096
    LOCALE_ENCODING: str = "utf8"


class S3DataBackend(HistoryMixin, BaseDataBackend):
    """S3 data backend."""

    # pylint: disable=too-many-instance-attributes
    name = "s3"
    default_operation_type = BaseOperationType.CREATE
    settings_class = S3DataBackendSettings

    def __init__(self, settings: settings_class = None):
        """Instantiates the AWS S3 client."""
        settings = settings if settings else self.settings_class()
        self.access_key_id = settings.ACCESS_KEY_ID
        self.secret_access_key = settings.SECRET_ACCESS_KEY
        self.session_token = settings.SESSION_TOKEN
        self.default_region = settings.DEFAULT_REGION
        self.default_bucket_name = settings.DEFAULT_BUCKET_NAME
        self.default_chunk_size = settings.DEFAULT_CHUNK_SIZE
        self.locale_encoding = settings.LOCALE_ENCODING

        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            aws_session_token=self.session_token,
            region_name=self.default_region,
        )

    def status(self) -> DataBackendStatus:
        """Checks whether bucket exists and is accessible."""
        try:
            self.client.head_bucket(Bucket=self.default_bucket_name)
        except ClientError:
            return DataBackendStatus.ERROR

        return DataBackendStatus.OK

    def list(
        self, target: str = None, details: bool = False, new: bool = False
    ) -> Iterator[Union[str, dict]]:
        """Lists objects contained in the S3 bucket.

        Args:
            target (str or None): The bucket where to list the objects.
                If target is `None`, the `default_bucket_name` is used instead.
            details (bool): Get detailed object information instead of just object name.
            new (bool): Given the history, list only unread files.

        Yields:
            str: The next object name. (If details is False).
            dict: The next object details. (If details is True).
        """
        if target is None:
            target = self.default_bucket_name

        objects_to_skip = set()
        if new:
            objects_to_skip = set(self.get_command_history(self.name, "read"))

        try:
            paginator = self.client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=target)
            for objects in page_iterator:
                if "Contents" not in objects:
                    continue
                for obj in objects["Contents"]:
                    if new and obj["Key"] in objects_to_skip:
                        continue
                    if details:
                        obj["LastModified"] = obj["LastModified"].strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        yield obj
                    else:
                        yield obj["Key"]
        except ClientError as err:
            error_msg = err.response["Error"]["Message"]
            msg = "Failed to list the bucket %s: %s"
            logger.error(msg, target, error_msg)
            raise BackendException(msg % (target, error_msg)) from err

    @enforce_query_checks
    def read(
        self,
        *,
        query: Union[str, BaseQuery] = None,
        target: str = None,
        chunk_size: Union[None, int] = None,
        raw_output: bool = False,
        ignore_errors: bool = False,
    ) -> Iterator[Union[bytes, dict]]:
        """Reads objects matching the query in the target bucket and yields them.

        Args:
            query: (str or BaseQuery): The pattern for the objects to read.
            target (str or None): The target bucket containing the objects.
                If target is `None`, the `default_bucket` is used instead.
            chunk_size (int or None): The chunk size for reading objects.
            raw_output (bool): Controls whether to yield bytes or dictionaries.
            ignore_errors (bool): If `True`, errors during the read operation
                will be ignored and logged. If `False` (default), a `BackendException`
                will be raised if an error occurs.

        Yields:
            dict: If `raw_output` is False.
            bytes: If `raw_output` is True.

        Raises:
            BackendException: If a failure during the read operation occurs and
                `ignore_errors` is set to `False`.
        """
        if not query.query_string:
            msg = "`query` argument is required to read."
            logger.error(msg)
            raise BackendParameterException(msg)

        if not chunk_size:
            chunk_size = self.default_chunk_size

        if target is None:
            target = self.default_bucket_name

        try:
            response = self.client.get_object(Bucket=target, Key=query.query_string)
        except ClientError as err:
            error_msg = err.response["Error"]["Message"]
            msg = "Failed to download %s: %s"
            logger.error(msg, query.query_string, error_msg)
            if not ignore_errors:
                raise BackendException(msg % (query.query_string, error_msg)) from err

        reader = self._read_raw if raw_output else self._read_dict
        for chunk in reader(response["Body"], chunk_size, ignore_errors):
            yield chunk

        # Archive fetched, add a new entry to the history
        self.append_to_history(
            {
                "backend": self.name,
                "action": "read",
                "id": target + "/" + query.query_string,
                "size": response["ContentLength"],
                "timestamp": now(),
            }
        )

    def write(  # pylint: disable=too-many-arguments
        self,
        data: Iterable[Union[bytes, dict]],
        target: Union[None, str] = None,
        chunk_size: Union[None, int] = None,
        ignore_errors: bool = False,
        operation_type: Union[None, BaseOperationType] = None,
    ) -> int:
        """Writes data records to the target and returns their count.

        Args:
            data: (Iterable): The data to write.
            target (str or None): The target bucket and the target object
                separated by a `/`.
                If target is `None`, the default bucket is used and a random
                (uuid4) object is created.
                If target does not contain a `/`, it is assumed to be the
                target object and the default bucket is used.
            target_container (str or None): The target bucket to create the
                target object into.
                If container is `None`, `default_bucket_name` is used as the
                 container instead.
            chunk_size (int or None): Ignored.
            ignore_errors (bool): If `True`, errors during the read operation
                will be ignored and logged. If `False` (default), a `BackendException`
                will be raised if an error occurs.
            operation_type (BaseOperationType or None): The mode of the write
                operation.
                If operation_type is `CREATE` or `INDEX`, the target object is
                expected to be absent. If the target object exists a
                `FileExistsError` is raised.
                If operation_type is `UPDATE`, the target object is overwritten.

        Returns:
            int: The number of written objects.

        Raises:
            BackendException: If the `operation_type` is `CREATE` or `INDEX` and the
                target object already exists.
            BackendParameterException: If the `operation_type` is `APPEND` or `DELETE`
                as it is not supported.
        """
        data = iter(data)
        try:
            first_record = next(data)
        except StopIteration:
            logger.info("Data Iterator is empty; skipping write to target.")
            return 0

        if not operation_type:
            operation_type = self.default_operation_type

        if not target:
            target = f"{self.default_bucket_name}/{now()}-{uuid4()}"
            logger.info(
                "Target not specified; using default bucket with random file name: %s",
                target,
            )

        if "/" not in target:
            target = f"{self.default_bucket_name}/{target}"
            logger.info(
                "Bucket not specified; using default bucket: %s",
                target,
            )

        target_bucket, target_object = target.split("/", 1)

        if operation_type in [BaseOperationType.APPEND, BaseOperationType.DELETE]:
            msg = "%s operation_type is not allowed."
            logger.error(msg, operation_type.name)
            raise BackendParameterException(msg % operation_type.name)

        if operation_type in [BaseOperationType.CREATE, BaseOperationType.INDEX]:
            if target_object in list(self.list(target=target_bucket)):
                msg = "%s already exists and overwrite is not allowed for operation %s"
                logger.error(msg, target_object, operation_type)
                if not ignore_errors:
                    raise BackendException(msg % (target_object, operation_type))

            logger.debug("Creating archive: %s", target_object)

            is_dict = isinstance(first_record, dict)
            writer = self._write_dict if is_dict else self._write_raw
            try:
                for chunk in chain((first_record,), data):
                    writer(target_bucket, target_object, chunk)
                response = self.client.head_object(
                    Bucket=target_bucket, Key=target_object
                )
            except (ClientError, ParamValidationError) as exc:
                msg = "Failed to upload %s"
                logger.error(msg, target)
                if not ignore_errors:
                    raise BackendException(msg % target) from exc

            # Archive written, add a new entry to the history
            self.append_to_history(
                {
                    "backend": self.name,
                    "action": "write",
                    "operation_type": operation_type.value,
                    "id": target,
                    "size": response["ContentLength"],
                    "timestamp": now(),
                }
            )

        return 1

    @staticmethod
    def _read_raw(
        obj: StreamingBody, chunk_size: int, _ignore_errors: bool
    ) -> Iterator[bytes]:
        """Reads the `object` in chunks of size `chunk_size` and yield them."""
        for chunk in obj.iter_chunks(chunk_size):
            yield chunk

    @staticmethod
    def _read_dict(
        obj: StreamingBody, chunk_size: int, ignore_errors: bool
    ) -> Iterator[dict]:
        """Reads the `object` by line and yield JSON parsed dictionaries."""
        for line in obj.iter_lines(chunk_size):
            try:
                yield json.loads(line)
            except (TypeError, json.JSONDecodeError) as err:
                msg = "Raised error: %s"
                logger.error(msg, err)
                if not ignore_errors:
                    raise BackendException(msg % err) from err

    def _write_raw(self, bucket: str, obj: str, data: bytes):
        """Writes the `chunk` bytes to the file."""
        self.client.put_object(Body=data, Bucket=bucket, Key=obj)

    def _write_dict(self, bucket: str, obj: str, data: dict):
        """Writes the `chunk` dictionary to the file."""
        self.client.put_object(
            Body=bytes(f"{json.dumps(data)}\n", encoding=self.locale_encoding),
            Bucket=bucket,
            Key=obj,
        )
