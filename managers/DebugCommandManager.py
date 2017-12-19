import json
import ccxt
import time
from terminaltables import AsciiTable

from Tasks import *
from peewee import *
from config import CondexConfig

from models.TickerModel import TickerModel
from models.CoinBalanceModel import CoinBalanceModel
from models.IndexedCoinModel import IndexedCoinModel
from models.SupportedCoinModel import SupportedCoinModel

class DebugCommandManager:

    def __init__(self):
        pass

    def coin_update(self):
        supported_coins_task()

    def wallet_update(self):
        wallet_update_task()

    def increment_tick(self):
        increment_rebalance_tick_task()

    def perform_algo(self):
        perform_algo_task()

    def perform_rebalance(self, rebalanceTicker, rebalanceSellAmount, elgibleTicker, elgibleBuyAmount):
        perform_rebalance_task(rebalanceTicker, rebalanceSellAmount, elgibleTicker, elgibleBuyAmount)
