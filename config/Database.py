from config import CondexConfig

from peewee import *

internal_database = SqliteDatabase(CondexConfig.DATABASE)
