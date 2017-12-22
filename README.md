## Condex (Console Based Index Fund Management)

### Description
Condex is a console based crypto currency Index Fund Management centered around bittrex. It is designed to easily manage the allocation and rebalancing of your index fund.

### Installation Instructions

Requirements:
* Linux Operating System (Ubuntu 16.04 Prefered)
* RabbitMQ Installed
* Python installed - this app should work with both Python 2.7 and Python 3
* Pip installed

##### Configure your Bittrex API key
1. Create a copy of the configuration template
```
$ cp config/CondexConfig.py.template config/CondexConfig.py
```
2. edit the configuration file and paste your Bittrex public API key in BITTREX_PUB and your secret key in BITTREX_SEC

##### Setup Commands
Open a terminal and type the following
```text
$ git clone git@github.com:R4stl1n/condex.git

$ cd condex

$ virtualenv --python=python2.7 .env (where python.27 is the path to your python 2.7 interpreter)

or for python 3
$ python3 -m venv .env

$ source .env/bin/activate

$ pip install  -r requirements.txt

$ python main.py
```

In another terminal run the following:
```text
$ cd condex

$ source .env/bin/activate

$ celery -A Tasks worker -B --loglevel=DEBUG --concurrency=4
```


##### Notes
Only the celery task is required for your index to continue to be managed. The condex main frontend main.py is only require for modifying and maintaining the index fund.

### Usage

#### Condex Terminal Commands

##### Show Commands

>show coins  

	Display all available coin pairs on the exchange.

>show stats 

	Display text representation of the current value of the index and the individual percentage distributions and values of any coins held in the index.
 
>show index  

	Display visual representation of the current value of the index and the individual percentage distributions and values of any coins held in the index.

##### Index Commands

>index add (coin) (percentage) (lock)

	Add a new coin into the index  
		coin - the desired coin symbol to add  
		percentage - the desired percentage (as a number) of the index the new coin should be allocated  
		lock - boolean (true/false) value to lock the desired % of a coin and prevent it being adjusted when other coins are
		added/updated  

>index update (coin) (percentage) (lock)

	Update a coin within the index  
		coin - the desired coin symbol to update  
		percentage - the new desired percentage of the index the coin should be allocated  
		lock - boolean (true/false) value to lock the desired % of a coin and prevent it being adjusted when other coins are
		added/updated  
	
>index remove (coin)  

	Remove a coin from the index  
		coin - the desired coin symbol to remove

>index threshhold (percentage)  

	Change the rebalance threshold percentage within the index  
		percentage - the new percentage a coin can move from it's desired percentage before it becomes eligible to be rebalanced

>index rtime (tickcount)  

	Change the frequency the index performs a rebalance 
		tickcount - number (in minutes) between each rebalance

>index start 

	Start the index process

>index stop
	Stops the index process

>index gen
	Starts the index process and buys all the required amounts of coins to match the desired percentages

##### Debug Commands - The below functions are run automatically within the Celery task processes and are not required during normal usage of the index.

>debug coin_update

	Run an API call to request the current values of coins from the exchange

>debug wallet_update

	Run an API call to request the current amounts of owned coins from the exchange and update the index with those values

>debug perform_algo

	Run the function to calculate and create the list of coins which have exceeded the threshold are are due for rebalancing
	and pass them into the rebalance funtion to be purchased and sold.

>debug perform_rebalance (coin1) (amount1) (coin2) (amount2)

	Run the function to sell a coin above the threshold percentage and buy one below it
		coin1 - the coin to sell
		amount1 - the amount of coin1 to sell
		coin2 - the coin to buy
		amount2 - the amount of coin2 to buy

### Who To Thank:

LTC Address

Raynaldo (R4stl1n) Rivera: LbAVtQeSQFQ3bBDNCQVBrqaEMwGt5jf9Uh

Michael (notnight) Pierson: LP11dCTqrbyAjn7z4N5R4fAdjy6QGYd9xy
