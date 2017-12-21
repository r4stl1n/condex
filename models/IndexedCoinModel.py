from peewee import *

from models.BaseModel import BaseModel

class IndexedCoinModel(BaseModel):
    Ticker = CharField(unique=True)
    DesiredPercentage = DoubleField()
    DistanceFromTarget = DoubleField()
    Locked = BooleanField()

