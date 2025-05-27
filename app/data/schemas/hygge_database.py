# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

"""
Module for managing the Hygge Power Trading Simulator database connection.

This module provides a centralized class `HyggeDatabase` for configuring
and accessing the PostgresSQL database instance using Peewee ORM with
connection pooling.
"""

from typing import Any, Optional

from peewee import OperationalError
from playhouse.postgres_ext import PostgresqlExtDatabase # type: ignore[import]
from playhouse.pool import PooledPostgresqlDatabase  # type: ignore[import]

from app.config.i_configuration import DbConfig
from app.data.schemas.schema_base import BaseModel


class HyggeDatabase:
    """
    Manages the database connection for the Hygge application.

    This class uses a singleton-like pattern to provide a single,
    pooled database connection instance. It handles configuration,
    connection testing, and recreation if the connection is lost.
    """

    _config: Optional[DbConfig] = None
    _instance: Optional[PooledPostgresqlDatabase] = None

    @classmethod
    def set_config(cls, config: DbConfig):
        """
        Sets the database configuration.

        This method should be called once at application startup
        before any database instance is requested.

        Args:
            config: An object implementing IConfiguration containing
                    database connection parameters.
        """
        cls._config = config

    @classmethod
    def get_instance(cls) -> PooledPostgresqlDatabase:
        """
        Gets the database instance, creating a new one if necessary.

        If an instance doesn't exist or the connection test fails,
        a new database instance is created and returned.

        Returns:
            PooledPostgresqlDatabase: The active database instance.
        """
        if cls._instance is None or not cls._test_connection():
            cls._instance = cls._create_db_instance()
        assert (
            cls._instance is not None
        ), "_instance should be initialized by this point"
        return cls._instance

    @classmethod
    def _test_connection(cls) -> bool:
        """
        Tests the current database connection.

        Executes a simple query to ensure the connection is active.
        If the connection fails, it closes the current instance and
        sets it to None, forcing a new connection on the next
        `get_instance` call.

        Returns:
            bool: True if the connection is active, False otherwise.
        """
        if not cls._instance:
            return False
        try:
            cls._instance.execute_sql("SELECT 1;")  # type: ignore
            return True
        except OperationalError:
            if cls._instance:
                cls._instance.close()
            cls._instance = None
            return False

    @classmethod
    def _create_db_instance(cls) -> PooledPostgresqlDatabase:
        """
        Creates a new database instance with pooled connections.

        Initializes a `PooledPostgresqlDatabase` using the provided
        configuration. It also sets the timezone to UTC for the
        connection and associates the BaseModel with this database.

        Returns:
            PooledPostgresqlDatabase: The newly created database instance.

        Raises:
            AttributeError: If `_config` or `_config.db` is None
                            (i.e., `set_config` was not called or
                            config is malformed).
        """
        if not cls._config:
            raise AttributeError(
                "Database configuration not set or is invalid. "
                "Call HyggeDatabase.set_config() with valid IConfiguration."
            )
        db_conf = cls._config
        db_instance = PooledPostgresqlDatabase(
            db_conf.database,
            user=db_conf.user,
            password=db_conf.password,
            host=db_conf.host,
            port=db_conf.port,
            max_connections=db_conf.max_connections,
            stale_timeout=db_conf.stale_timeout,
            autorollback=True,
        )
        cls._set_utc_timezone(db_instance)
        BaseModel.set_database(db_instance)
        return db_instance

    @staticmethod
    def _set_utc_timezone(db_instance: PooledPostgresqlDatabase):
        """
        Sets the timezone of the database connection to UTC.

        This ensures consistency in timestamp handling across the application.

        Args:
            db_instance (PooledPostgresqlDatabase): The database instance
                for which to set the timezone.
        """
        cursor: Any
        # "partially unknown type" errors for Peewee methods.
        with db_instance.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SET TIME ZONE 'UTC';")
