import cmd
import json
import sys
import logzero
from logzero import logger

from config import CondexConfig
from terminaltables import AsciiTable

from Util import *
from Tasks import *

from managers.DatabaseManager import *
from managers.ExchangeManager import ExchangeManager
from managers.ShowCommandManager import ShowCommandManager
from managers.IndexCommandManager import IndexCommandManager
from managers.DebugCommandManager import DebugCommandManager

from models.TickerModel import TickerModel
from models.IndexInfoModel import IndexInfoModel
from models.IndexedCoinModel import IndexedCoinModel
from models.CoinBalanceModel import CoinBalanceModel
from models.SupportedCoinModel import SupportedCoinModel

em = ExchangeManager()
scm = ShowCommandManager()
icm = IndexCommandManager()
dcm = DebugCommandManager()

class ConDex(cmd.Cmd):
    """Simple command processor example."""

    prompt = 'ConDex> '
    intro = '''                                                                             
               ,----..            ,--.                                       
  ,----..     /   /   \         ,--.'|    ,---,        ,---,. ,--,     ,--,  
 /   /   \   /   .     :    ,--,:  : |  .'  .' `\    ,'  .' | |'. \   / .`|  
|   :     : .   /   ;.  \,`--.'`|  ' :,---.'     \ ,---.'   | ; \ `\ /' / ;  
.   |  ;. /.   ;   /  ` ;|   :  :  | ||   |  .`\  ||   |   .' `. \  /  / .'  
.   ; /--` ;   |  ; \ ; |:   |   \ | ::   : |  '  |:   :  |-,  \  \/  / ./   
;   | ;    |   :  | ; | '|   : '  '; ||   ' '  ;  ::   |  ;/|   \  \.'  /    
|   : |    .   |  ' ' ' :'   ' ;.    ;'   | ;  .  ||   :   .'    \  ;  ;     
.   | '___ '   ;  \; /  ||   | | \   ||   | :  |  '|   |  |-,   / \  \  \    
'   ; : .'| \   \  ',  / '   : |  ; .''   : | /  ; '   :  ;/|  ;  /\  \  \   
'   | '/  :  ;   :    /  |   | '`--'  |   | '` ,/  |   |    \./__;  \  ;  \  
|   :    /    \   \ .'   '   : |      ;   :  .'    |   :   .'|   : / \  \  ; 
 \   \ .'      `---`     ;   |.'      |   ,.'      |   | ,'  ;   |/   \  ' | 
  `---`                  '---'        '---'        `----'    `---'     `--`  
                 Console Crypto Currency Index Manager



 '''

    doc_header = 'doc_header'
    misc_header = 'misc_header'
    undoc_header = 'undoc_header'
    
    ruler = '-'

    def do_show(self, line):
        command_split = line.split(' ')
        command = command_split[0]

        if len(command_split) >= 1:
            if command == "coins":
                scm.show_avalible_coins()
            elif command == "stats":
                scm.show_stats()
            elif command == "index":
                scm.show_index()
            elif command == "threshold":
                scm.show_threshold()
            elif command == "coin":
                if len(command_split) != 2:
                    sys.stdout.write("coin symbol required\n")
                else:
                    # sys.stdout.write(str(command_split[1]) + "\n")
                    pair = command_split[1].split("/")
                    sys.stdout.write("The market " + str(command_split[1]) + " is active: " + str(em.market_active(pair[0], pair[1])) + "\n")
            else:
                logger.warn("Unknown Command")
        else:
            logger.warn("Not Enough Parameters")

    def do_index(self, line):
        command_split = line.split(' ')
        command = command_split[0]

        if len(command_split) >= 2:
            if command == "add":
                if len(command_split) == 2:
                    icm.index_add_coin(command_split[1])
                elif len(command_split) == 3:
                    icm.index_add_coin(command_split[1],command_split[2])
                elif len(command_split) == 4:
                    icm.index_add_coin(command_split[1],command_split[2], command_split[3])
                else:
                    logger.warn("Not Enough Parameters")
            elif command == "update":
                if len(command_split) == 4:
                    icm.index_update_coin(command_split[1],command_split[2], command_split[3])
                else:
                    logger.warn("Not Enough Parameters")             
            elif command == "remove":
                icm.index_remove_coin(command_split[1])
            elif command == "lock":
                icm.lock_coin(command_split[1])
            elif command == "unlock":
                icm.unlock_coin(command_split[1])
            elif command == 'threshold':
                icm.index_threshold_update(command_split[1])
            elif command == 'rtime':
                icm.index_rebalance_tick_update(command_split[1])
            elif command == 'marketcap':
                if len(command_split) == 2:
                    icm.export_market_cap_index(command_split[1])
                else:
                    logger.warn("Not Enough Parameters")
            elif command == 'bulkadd':
                icm.index_bulkadd_coin(command_split[1])
            else:
                logger.warn("Unknown Command")
        elif len(command_split) >= 1:
            if command == 'start':
                icm.index_start_command()
            elif command == 'gen':
                icm.index_gen_command()
            elif command == 'stop':
                icm.index_stop_command()
            elif command == 'export':
                icm.export_index()
            elif command == 'import':
                icm.import_index()
            elif command == 'equalweight':
                icm.index_equal_weight()
            else:
                logger.warn("Unknown Command")
        else:
            logger.warn("Not Enough Parameters")

    def do_debug(self, line):
        command_split = line.split(' ')
        command = command_split[0]

        if len(command_split) >= 1:
            if command == "coin_update":
                dcm.coin_update()
            elif command == "wallet_update":
                dcm.wallet_update()
            elif command == "perform_algo":
                dcm.perform_algo()
            elif command == "perform_rebalance":
                dcm.perform_rebalance(command_split[1],command_split[2],command_split[3],command_split[4])
            elif command == 'increment_tick':
                dcm.increment_tick()
            elif command == 'market':
                em.check_min_buy(38, "BAT/BTC")
            else:
                logger.warn("Unknown Command")
        else:
            logger.warn("Not Enough Parameters")

    def do_exit(self, line):
        Util.clear_screen()
        return True

    def do_herp(self,line):
        sys.stdout.write(em.get_tickers())
        sys.stdout.write(wallet_data['BTC/USDT']['info']['Ask'])
        sys.stdout.write('\n')

    def do_clear(self,line):
        Util.clear_screen()

    def do_quit(self, line):
        Util.clear_screen()
        return True
    
    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    logzero.loglevel(logging.DEBUG)
    logzero.logfile("condex.log")
    Util.clear_screen()
    Util.bootstrap()
    ConDex().cmdloop()
