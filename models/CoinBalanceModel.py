from peewee import *

from models.BaseModel import BaseModel
from models.TickerModel import TickerModel

class CoinBalanceModel(BaseModel):
    Coin = CharField(unique=True)
    TotalCoins = DoubleField()
    BTCBalance = DoubleField()
    USDBalance = DoubleField()
    LastUpdated = DateTimeField()

    def calculate_unrealized_gain(ticker:TickerModel):
        btc_cost_per_coin = BTCBalance / TotalCoins

        current_btc_value = ticker.BTCVal

        return ((current_btc_value - btc_cost_per_coin)/ btc_cost_per_coin) * 100