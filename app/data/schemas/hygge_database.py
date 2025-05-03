from peewee import OperationalError
from playhouse.pool import PooledPostgresqlDatabase

from app.data.schemas.schema_base import BaseModel


class HyggeDatabase:
    _config = None
    _instance = None

    @classmethod
    def set_config(cls, config):
        cls._config = config

    @classmethod
    def get_instance(cls):
        """Gets the database instance, creating a new one if necessary."""
        if cls._instance is None or not cls._test_connection():
            cls._instance = cls._create_db_instance()
        return cls._instance

    @classmethod
    def _test_connection(cls):
        """Tests the current database connection."""
        try:
            cls._instance.execute_sql('SELECT 1;')
            return True
        except OperationalError:
            cls._instance.close()
            cls._instance = None
            return False

    @classmethod
    def _create_db_instance(cls):
        """Creates a new database instance with pooled connections."""
        db_instance = PooledPostgresqlDatabase(
            cls._config.database,
            user=cls._config.user,
            password=cls._config.password,
            host=cls._config.host,
            port=cls._config.port,
            max_connections=cls._config.max_connections,
            stale_timeout=cls._config.stale_timeout,
            autorollback=True
        )
        cls._set_utc_timezone(db_instance)
        BaseModel.set_database(db_instance)
        return db_instance

    @staticmethod
    def _set_utc_timezone(db_instance):
        """Sets the timezone of the database connection to UTC."""
        with db_instance.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SET TIME ZONE 'UTC';")
