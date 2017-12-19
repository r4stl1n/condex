from peewee import *

from models.BaseModel import BaseModel

class CoinBalanceModel(BaseModel):
    Coin = CharField(unique=True)
    TotalCoins = DoubleField()
    BTCBalance = DoubleField()
    USDBalance = DoubleField()
    LastUpdated = DateTimeField()