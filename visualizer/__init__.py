from flask import Flask
from flask.ext.rethinkdb import RethinkDB


app = Flask(__name__)
app.config.from_object('config')

db = RethinkDB(app)

from visualizer.views import DatasetView
DatasetView.register(app)

if __name__ == '__main__':
    app.run()
