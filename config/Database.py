from config import CondexConfig


from peewee import *
from playhouse.pool import *

if CondexConfig.USE_DATABASE == 'MYSQL':
    # Mysql Database Setup
    internal_database = PooledMySQLDatabase(
    CondexConfig.MYSQL_DB_NAME,
    user= CondexConfig.MYSQL_DB_USER,
    passwd= CondexConfig.MYSQL_USER_PASSWORD,
    host=CondexConfig.MYSQL_HOST,
    max_connections=32,
    stale_timeout=300,
    )
elif CondexConfig.USE_DATABASE == 'POSTGRES':
    # Postgres Database Setup
    internal_database = PooledPostgresqlDatabase(
    CondexConfig.POSTGRES_DB_NAME,  # Required by Peewee.
    user=CondexConfig.POSTGRES_DB_USER,  # Will be passed directly to psycopg2.
    password=CondexConfig.POSTGRES_DB_PASSWORD,  # Ditto.
    host=CondexConfig.POSTGRES_HOST,  # Ditto.
    max_connections=32,
    stale_timeout=300,
    )
else:
    internal_database = PooledSqliteDatabase(CondexConfig.DATABASE)