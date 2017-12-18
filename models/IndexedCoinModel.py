from peewee import *

from BaseModel import BaseModel

class IndexedCoinModel(BaseModel):
    Ticker = CharField(unique=True)
    DesiredPercentage = DoubleField()
    CurrentPercentage = DoubleField()
    UnrealizedGain = DoubleField()
    Locked = BooleanField()
