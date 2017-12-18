## Condex (Console Based Index Fund Management)

### Description
Condex is a console based crypto currency Index Fund Management centered around bittrex. It is designed to easily manage the allocation and rebalancing of your index fund.

### Installation Instructions

Requirments:
	Linux Operating System (Ubuntu 16.04 Prefered)

##### Setup Commands
Open a terminal and type the following
> git clone git@github.com:R4stl1n/condex.git
> cd condex
> pip virtualenv .env
> pip install  -r requirments.txt
> source .env/bin/activate

##### Configure your Bittrex API key
1. Create a copy of the configuration template
> cp config/CondexConfig.py.template CondexConfig.py
2. edit the configuration file and paste your Bittrex public API key in BITTREX_PUB and your secret key in BITTREX_SEC


##### Run Condex
>python main.py

In another terminal run the following:
>cd condex
>source .env/bin/activate
>celery -A Tasks worker -B --loglevel=DEBUG --concurrency=4


##### Notes
Only the celery task is required for your index to continue to be managed. The condex main frontend main.py is only require for modifying and maintaining the index fund.

### Usage
FILL THIS IN NOTNIGHT


### Who To Thank:

LTC Address

Raynaldo (R4stl1n) Rivera: LbAVtQeSQFQ3bBDNCQVBrqaEMwGt5jf9Uh

Michael (notnight) Pierson: LP11dCTqrbyAjn7z4N5R4fAdjy6QGYd9xy
