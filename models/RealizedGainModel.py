from peewee import *

from models.BaseModel import BaseModel

class RealizedGainModel(BaseModel):
    Ticker = CharField(unique=True)
    RealizedGain = DoubleField()
