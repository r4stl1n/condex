from peewee import *

from BaseModel import BaseModel

class RealizedGainModel(BaseModel):
    Ticker = CharField(unique=True)
    RealizedGain = DoubleField()
