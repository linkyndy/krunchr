import os


DEBUG = os.environ['DEBUG']
SECRET_KEY = os.environ['SECRET_KEY']

RETHINKDB_HOST = os.environ['RETHINKDB_HOST']
RETHINKDB_PORT = os.environ['RETHINKDB_PORT']
RETHINKDB_AUTH = os.environ['RETHINKDB_AUTH']
RETHINKDB_DB = os.environ['RETHINKDB_DB']

API_DATASET_ANALYSE = 'http://batman.krunchr.net/v1/analyse/'
API_VISUALIZATION_CREATE = 'http://batman.krunchr.net/v1/create/'
