import logging
import time

import certifi
from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError

from config import get_settings

logger = logging.getLogger(__name__)

_client: MongoClient | None = None
_indexes_ensured: bool = False

INDEX_CONFLICT_CODES = {85, 86}  # IndexOptionsConflict, IndexKeySpecsConflict


def get_client() -> MongoClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = MongoClient(
            settings.MONGODB_URI,
            tlsCAFile=certifi.where(),
            tlsDisableOCSPEndpointCheck=True,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            retryWrites=True,
        )
    return _client


def get_database() -> Database:
    settings = get_settings()
    db = get_client()[settings.DATABASE_NAME]
    ensure_indexes()
    return db


def _normalize_index_key(key_spec) -> tuple:
    if isinstance(key_spec, dict):
        items = key_spec.items()
    else:
        items = key_spec
    return tuple((field, int(direction)) for field, direction in items)


def _create_index_safe(collection, keys: list, **kwargs) -> None:
    index_name = kwargs.get("name", "_".join(field for field, _ in keys))
    target_key = _normalize_index_key(keys)
    existing = collection.index_information()

    if index_name in existing:
        logger.debug("Index '%s' already exists on %s", index_name, collection.name)
        return

    for name, info in existing.items():
        if _normalize_index_key(info.get("key", {})) == target_key:
            logger.debug("Equivalent index '%s' already exists on %s", name, collection.name)
            return

    try:
        collection.create_index(keys, **kwargs)
        logger.info("Created index '%s' on %s", index_name, collection.name)
    except OperationFailure as exc:
        if exc.code in INDEX_CONFLICT_CODES:
            logger.warning(
                "Index conflict on %s (%s) — skipping: %s",
                collection.name,
                index_name,
                exc.details,
            )
            return
        if exc.code == 11000:
            logger.error(
                "Cannot create unique index '%s' on %s: duplicate values exist in collection",
                index_name,
                collection.name,
            )
            return
        raise


def ensure_indexes(max_retries: int = 3, retry_delay: float = 2.0) -> None:
    global _indexes_ensured

    if _indexes_ensured:
        return

    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            db = get_client()[get_settings().DATABASE_NAME]
            db.command("ping")

            _create_index_safe(
                db.users,
                [("email", ASCENDING)],
                unique=True,
                name="email_unique",
            )
            _create_index_safe(
                db.chats,
                [("user_id", ASCENDING)],
                name="user_id_index",
            )

            _indexes_ensured = True
            logger.info("Database indexes ensured")
            return

        except (ServerSelectionTimeoutError, ConnectionFailure) as exc:
            last_error = exc
            logger.warning(
                "MongoDB connection attempt %d/%d failed: %s",
                attempt,
                max_retries,
                exc,
            )
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)

    if last_error:
        raise last_error
