from peewee import *

from models.BaseModel import BaseModel

class RebalanceTickModel(BaseModel):

    TickCount = IntegerField()
