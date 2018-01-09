import sys
import json
import ccxt
import time

from ascii_graph.colors import *
from ascii_graph import Pyasciigraph
from ascii_graph.colordata import vcolor
from ascii_graph.colordata import hcolor

from terminaltables import AsciiTable

from config import CondexConfig

from models.TickerModel import TickerModel
from models.IndexInfoModel import IndexInfoModel
from models.IndexedCoinModel import IndexedCoinModel
from models.CoinBalanceModel import CoinBalanceModel
from models.SupportedCoinModel import SupportedCoinModel

from managers.DatabaseManager import DatabaseManager

class ShowCommandManager:

    def __init__(self):
        pass

    def show_avalible_coins(self):

        table_data = [['Available','Coins','.','.','.','.','.','.','.','.','.']]

        count = 0
        current_array = []
        
        for coin in SupportedCoinModel.select():
            
            current_array.append(coin.Ticker)

            if count == 10:
                table_data.append(current_array)
                current_array = []
                count = 0
            else:
                count = count + 1

        table = AsciiTable(table_data)

        sys.stdout.write(table.table)
        sys.stdout.write('\n')

    def show_stats(self):
        indexInfo = IndexInfoModel.get(id=1)

        # Create the Index Table
        cointTableData =[['Coin', 'Amount', 'BTC Val', 'USD Val', 'Locked', 'Desired %', 'Current %', 'Off Target %']]

        for coin in IndexedCoinModel.select():

            coinBalance = CoinBalanceModel.get(CoinBalanceModel.Coin == coin.Ticker)

            newArray = [coin.Ticker, coinBalance.TotalCoins, coinBalance.BTCBalance, round(coinBalance.USDBalance, 2),
                        coin.Locked, coin.DesiredPercentage, coin.get_current_percentage(indexInfo.TotalBTCVal), coin.get_percent_from_coin_target(coinBalance,indexInfo.TotalBTCVal)]
            cointTableData.append(newArray)

        # Create the summary table
        summary_table_data = [['Active', 'Index Count', 'BTC Val', 'USD Val',]]
        summary_table_data.append([True, len(IndexedCoinModel.select()), indexInfo.TotalBTCVal, indexInfo.TotalUSDVal])

        coin_table = AsciiTable(cointTableData)
        summary_table = AsciiTable(summary_table_data)

        sys.stdout.write("\nCurrent Index Summary\n")
        sys.stdout.write(summary_table.table)

        sys.stdout.write("\nCurrent Index Table\n")
        sys.stdout.write(coin_table.table)
        sys.stdout.write('\n')

    def show_index(self):
        graphArray = []

        for coin in IndexedCoinModel.select():
            graphArray.append((coin.Ticker, coin.DesiredPercentage))

        pyGraph = Pyasciigraph(
            line_length=50,
            min_graph_length=50,
            separator_length=4,
            multivalue=False,
            human_readable='si',
            graphsymbol='*',
            float_format='{0:,.2f}'
            )

        thresholds = {
          15:  Gre, 30: Blu, 50: Yel, 60: Red,
        }
        data = hcolor(graphArray, thresholds)


        sys.stdout.write("\n")
        for line in  pyGraph.graph('Index Distribution', data=data):
            sys.stdout.write(line + "\n")
        sys.stdout.write("\n")

    def show_threshold(self):
        indexInfo = DatabaseManager.get_index_info_model()
        sys.stdout.write("\nCurrent Rebalance Threshold\n")

        summary_table_data = [["Active", "Balance Threshold", "Order Timeout", "Rebalance Tick Setting"]]
        summary_table_data.append([indexInfo.Active, indexInfo.BalanceThreshold, indexInfo.OrderTimeout, indexInfo.RebalanceTickSetting])

        summary_table = AsciiTable(summary_table_data)
        sys.stdout.write(summary_table.table)
        sys.stdout.write("\n")