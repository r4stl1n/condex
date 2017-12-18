from peewee import *

from BaseModel import BaseModel

class CoinLockModel(BaseModel):

    Ticker = CharField(unique=True)