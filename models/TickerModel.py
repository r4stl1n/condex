from peewee import *

from models.BaseModel import BaseModel

class TickerModel(BaseModel):

    Ticker = CharField(unique=True)
    BTCVal = DoubleField()
    USDVal = DoubleField()
    LastUpdated = DateTimeField()

