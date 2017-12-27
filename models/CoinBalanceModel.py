from peewee import *

from models.BaseModel import BaseModel
from models.TickerModel import TickerModel

class CoinBalanceModel(BaseModel):
    Coin = CharField(unique=True, max_length=64)
    TotalCoins = DoubleField()
    BTCBalance = DoubleField()
    USDBalance = DoubleField()
    LastUpdated = DateTimeField()

    def get_current_percentage(self, totalBTCValue):

        return round((self.BTCBalance / totalBTCValue)*100,2)
