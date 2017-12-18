## Condex (Console Based Index Fund Management)

### Description
Condex is a console based crypto currency Index Fund Management centered around bittrex. It is designed to easily manage the allocation and rebalancing of your index fund.

### Installation Instructions

Requirments:
	Linux Operating System (Ubuntu 16.04 Prefered)
	RabbitMQ Installed

##### Setup Commands
	Open the config folder and create a copy of the CondexConfig.py.template
	Rename the CondexConfig.py.template to CondexConfig.py
	Add your API key to the BITTREX_PUB and BITTREX_SEC fields
>BITTREX_PUB='publickeyhere'

>BITTREX_SEC='secretkeyhere'

	Save the file then proceed to do the following

Open a terminal and type the following
> git clone git@github.com:R4stl1n/condex.git
> cd condex
> pip virtualenv .env
> pip install  -r requirments.txt
> source .env/bin/activate
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
