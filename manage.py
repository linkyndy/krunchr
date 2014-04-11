#!/usr/bin/env python

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

from flask.ext.script import Manager, Server
from krunchr import app, db


manager = Manager(app)

manager.add_command('runserver', Server())


@manager.command
def create_db():
    tables = ['datasets', 'visualizations']
    for table in tables:
        try:
            r.table_create(table).run(db.conn)
        except RqlRuntimeError:
            print 'Table `%s` already exists' % table
    print 'Tables have been created.'


@manager.command
def drop_db():
    tables = r.table_list().run(db.conn)
    for table in tables:
        r.table_drop(table).run(db.conn)
    print 'Tables have been dropped.'


if __name__ == '__main__':
    manager.run()
