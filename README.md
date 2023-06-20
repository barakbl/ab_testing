# A/B testing tool

A basic a/b testing tool. 
built as part of home assignment
Based on FastAPI framework

## Install
`
python3 -m venv venv
pip install -r requirments.txt
`


## Run:
`
source /venv/bin/activte
python main.py
`


## Features
- based on sqlite db - for easy integration/installation.
- a swagger UI - auto created by FastAPI: http://localhost:8888/docs
- tests under tests directory
- in default db (file: sqlite.db): one experiment named test
with two variants. 

## TODO
- Dockerize
- Improve Algorithem/sql: scale and performance. 
- Add more tests
- Add Alembic for sql migrations
- Consider use of Async IO - as we heavy on DB - this might improve performance
- Add a Locust support - for stress tests
- Tested with Python 3.8 only


