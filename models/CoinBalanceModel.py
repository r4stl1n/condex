from peewee import *

from BaseModel import BaseModel

class CoinBalanceModel(BaseModel):
    Coin = CharField(unique=True)
    TotalCoins = DoubleField()
    BTCBalance = DoubleField()
    USDBalance = DoubleField()
    LastUpdated = DateTimeField()