from managers.DatabaseManager import *

from peewee import *

class BaseModel(Model):
    class Meta:
        database = internal_database
