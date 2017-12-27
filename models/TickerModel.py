from peewee import *

from models.BaseModel import BaseModel

class TickerModel(BaseModel):

    Ticker = CharField(unique=True,max_length=64)
    BTCVal = DoubleField()
    USDVal = DoubleField()
    LastUpdated = DateTimeField()

