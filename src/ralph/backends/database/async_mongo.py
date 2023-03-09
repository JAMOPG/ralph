"""Async MongoDB database backend for Ralph."""

import logging
from typing import List, TextIO, Union

from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import BulkWriteError, ConnectionFailure, PyMongoError

from ralph.conf import MongoClientOptions
from ralph.exceptions import BackendException

from .base import (
    BaseAsyncDatabase,
    DatabaseStatus,
    StatementParameters,
    StatementQueryResult,
    enforce_query_checks,
)
from .mongo import MongoDatabase, MongoQuery, mongo_settings

logger = logging.getLogger(__name__)


class AsyncMongoDatabase(BaseAsyncDatabase):
    """Async MongoDB database backend."""

    name = "async_mongo"
    query_model = MongoQuery
    to_documents = staticmethod(MongoDatabase.to_documents)

    def __init__(
        self,
        connection_uri: str = mongo_settings.CONNECTION_URI,
        database: str = mongo_settings.DATABASE,
        collection: str = mongo_settings.COLLECTION,
        client_options: MongoClientOptions = mongo_settings.CLIENT_OPTIONS,
    ):
        """Instantiates the async Mongo client.

        Args:
            connection_uri (str): MongoDB connection URI.
            database (str): MongoDB database to connect to.
            collection (str): MongoDB database collection to get objects from.
            client_options (MongoClientOptions): A dictionary of valid options
                for the AsyncIOMotorClient class initialization.
        """
        self.client = AsyncIOMotorClient(connection_uri, **client_options.dict())
        self.database = getattr(self.client, database)
        self.collection = getattr(self.database, collection)

    async def status(self) -> DatabaseStatus:
        """Checks MongoDB cluster connection status."""
        # Check Mongo cluster connection
        try:
            await self.client.admin.command("ping")
        except ConnectionFailure:
            return DatabaseStatus.AWAY

        # Check cluster status
        if (await self.client.admin.command("serverStatus")).get("ok", 0.0) < 1.0:
            return DatabaseStatus.ERROR

        return DatabaseStatus.OK

    @enforce_query_checks
    async def get(self, query: MongoQuery = None, chunk_size: int = 500):
        """Gets collection documents and yields them.

        The `query` dictionary should only contain kwargs compatible with the
        pymongo.collection.Collection.find method signature (API reference
        documentation: https://pymongo.readthedocs.io/en/stable/api/pymongo/).
        """
        async for document in self.collection.find(
            batch_size=chunk_size, **query.dict()
        ):
            # Make the document json-serializable
            document.update({"_id": str(document.get("_id"))})
            yield document

    async def bulk_import(self, batch: list, ignore_errors: bool = False):
        """Inserts a batch of documents into the selected database collection."""
        try:
            new_documents = await self.collection.insert_many(batch)
        except BulkWriteError as error:
            if not ignore_errors:
                raise BackendException(
                    *error.args, f"{error.details['nInserted']} succeeded writes"
                ) from error
            logger.warning(
                "Bulk importation failed for current documents chunk but you choose "
                "to ignore it.",
            )
            return error.details["nInserted"]

        inserted_count = len(new_documents.inserted_ids)
        logger.debug("Inserted %d documents chunk with success", inserted_count)

        return inserted_count

    async def put(
        self,
        stream: Union[TextIO, list],
        chunk_size: int = 500,
        ignore_errors: bool = False,
    ) -> int:
        """Writes documents from the `stream` to the instance collection."""
        logger.debug(
            "Start writing to the %s collection of the %s database (chunk size: %d)",
            self.collection,
            self.database,
            chunk_size,
        )

        success = 0
        batch = []
        for document in self.to_documents(stream, ignore_errors=ignore_errors):
            batch.append(document)
            if len(batch) < chunk_size:
                continue

            success += await self.bulk_import(batch, ignore_errors=ignore_errors)
            batch = []

        # Edge case: if the total number of documents is lower than the chunk size
        if len(batch) > 0:
            success += await self.bulk_import(batch, ignore_errors=ignore_errors)

        logger.debug("Inserted a total of %d documents with success", success)

        return success

    async def query_statements(
        self, params: StatementParameters
    ) -> StatementQueryResult:
        """Returns the results of a statements query using xAPI parameters."""
        mongo_query_filters = {}

        if params.statementId:
            mongo_query_filters.update({"_source.id": params.statementId})

        if params.agent:
            mongo_query_filters.update({"_source.actor.account.name": params.agent})

        if params.verb:
            mongo_query_filters.update({"_source.verb.id": params.verb})

        if params.activity:
            mongo_query_filters.update(
                {
                    "_source.object.objectType": "Activity",
                    "_source.object.id": params.activity,
                },
            )

        if params.since:
            mongo_query_filters.update({"_source.timestamp": {"$gt": params.since}})

        if params.until:
            mongo_query_filters.update({"_source.timestamp": {"$lte": params.until}})

        if params.search_after:
            search_order = "$gt" if params.ascending else "$lt"
            mongo_query_filters.update(
                {"_id": {search_order: ObjectId(params.search_after)}}
            )

        mongo_sort_order = ASCENDING if params.ascending else DESCENDING
        mongo_query_sort = [
            ("_source.timestamp", mongo_sort_order),
            ("_id", mongo_sort_order),
        ]

        mongo_response = await self._find(
            filter=mongo_query_filters, limit=params.limit, sort=mongo_query_sort
        )
        search_after = None
        if mongo_response:
            search_after = mongo_response[-1]["_id"]

        return StatementQueryResult(
            statements=[document["_source"] for document in mongo_response],
            pit_id=None,
            search_after=search_after,
        )

    async def query_statements_by_ids(self, ids: List[str]) -> List:
        """Returns the list of matching statement IDs from the database."""
        return await self._find(filter={"_source.id": {"$in": ids}})

    async def _find(self, **kwargs):
        """Wraps the MongoClient.collection.find method.

        Raises:
            BackendException: raised for any failure.
        """
        try:
            return [i async for i in self.collection.find(**kwargs)]
        except (PyMongoError, IndexError, TypeError, ValueError) as error:
            msg = "Failed to execute MongoDB query"
            logger.error("%s. %s", msg, error)
            raise BackendException(msg, *error.args) from error
