from config import CondexConfig

from peewee import *
from playhouse.pool import *

internal_database = PooledSqliteDatabase(CondexConfig.DATABASE)

# Mysql Database Setup
#internal_database = PooledMySQLDatabase(
#    'database_name',
#    user='database_user',
#    passwd='database_password',
#    host='database_host',
#    max_connections=12,
#    stale_timeout=300,
#)

# Postgres Database Setup
#internal_database = PooledPostgresqlDatabase(
#    'database_name',  # Required by Peewee.
#    user='database_user',  # Will be passed directly to psycopg2.
#    password='database_password',  # Ditto.
#    host='database_host',  # Ditto.
#    max_connections=12,
#    stale_timeout=300,
#)