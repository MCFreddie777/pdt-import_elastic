# [PDT] Import ElasticSearch

This project imports large data dump of twitter tweets into ElasticSearch

### Data
from [https://drive.google.com/drive/folders/1erM4udXKUDRuhzX6n0WeXTb-G87xbIHf](https://drive.google.com/drive/folders/1erM4udXKUDRuhzX6n0WeXTb-G87xbIHf) 

### Prerequisites

- Python 3
- [Pip](https://packaging.python.org/tutorials/installing-packages/)
- [Pipenv](https://github.com/pypa/pipenv)


### Installation

Following script will load and install all  needed dependencies from Pipfile 

```shell script
pipenv install
```

### Usage

All data should be unarchived into the data folder in project root first.
Then, you need to configure your database connection info in `config/connection.py`, e.g:
```
hostname = "localhost"
port = "9200"
index = "tweets"
```

Activate pip environment

```shell script
pipenv shell
```

Then run `run.sh`:

```shell script
. ./run.sh
```

This shell script runs both migration (drops and recreates the index with correct mapping) and and import.

If you only wish to run one of it you might run:

```shell script
python3 src/migrate.py
```

or 

```shell script
python3 src/script.py
```  
