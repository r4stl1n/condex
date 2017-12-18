from peewee import *

from BaseModel import BaseModel

class SupportedCoinModel(BaseModel):
    Ticker = CharField(unique=True)


