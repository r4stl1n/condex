from config import CondexConfig

from peewee import *

internal_database = SqliteDatabase(CondexConfig.DATABASE, autocommit=False))

# Mysql Database Setup
#internal_database = MySQLDatabase(
#    'database_name',
#    user='database_user',
#    passwd='database_password',
#    host='database_host',
#    autocommit=False)
#)

# Postgres Database Setup
#internal_database = PostgresqlDatabase(
#    'database_name',  # Required by Peewee.
#    user='database_user',  # Will be passed directly to psycopg2.
#    password='database_password',  # Ditto.
#    host='database_host',  # Ditto.
#    autocommit=False)
#)