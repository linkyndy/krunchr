krunchr
==========

krunchr is an online service that draws custom visualizations of fairly large data sets.

Setup
-----

* Clone this repo and create a virtualenv
* Install reqs:

    ```bash
    pip install -r requirements.txt
    ```

* Create an `.env` file to store your env vars:

    ```bash
    DEBUG=True
    RETHINKDB_AUTH=
    RETHINKDB_DB=krunchr
    RETHINKDB_HOST=localhost
    RETHINKDB_PORT=28015
    ```

* Enable the env vars you've just created:

    ```bash
    source <path-to-env-file>/.env
    ```

* Turn on the datastore:

    ```bash
    rethinkdb [-d <directory-to-store-your-data>]
    ```

* Open `localhost:8080` and create a database called `krunchr`
* Create the necessary tables for the database:

    ```bash
    <path-to-repo>/manage.py create_db
    ```

* Start the dev server:

    ```bash
    <path-to-repo>/manage.py runserver
    ```

* Go rock those datasets!
