from peewee import *

from models.BaseModel import BaseModel
from models.TickerModel import TickerModel

class CoinBalanceModel(BaseModel):
    Coin = CharField(unique=True)
    TotalCoins = DoubleField()
    BTCBalance = DoubleField()
    USDBalance = DoubleField()
    LastUpdated = DateTimeField()

    def calculate_unrealized_gain(self, ticker):
        if (self.TotalCoins == 0):
            return 0
        btc_cost_per_coin = self.BTCBalance / self.TotalCoins

        current_btc_value = ticker.BTCVal

        return ((current_btc_value - btc_cost_per_coin)/ btc_cost_per_coin) * 100
