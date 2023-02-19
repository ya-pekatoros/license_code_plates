#development variables
PORT ?= 8000
DB_NAME = third-project
LOCAL_DB_USER = ypekatoros

install:
		poetry install

build-db: db-drop db-create schema-data-load

db-start:
		sudo service postgresql start

db-status:
		sudo service postgresql status

db-stop:
		sudo service postgresql stop

db-create:
		createdb $(DB_NAME)

db-drop:
		dropdb $(DB_NAME)

db-reset:
	dropdb $(DB_NAME) || true
	createdb $(DB_NAME)

dbs-show:
		psql -l

db-connect:
	psql -d $(DB_NAME)

db-dev-setup: db-reset schema-data-load

schema-data-load:
		psql $(DB_NAME) < database.sql

db-show-log:
		vim /var/log/postgresql/postgresql-14-main.log

db-dump:
		pg_dump -h localhost -d $(DB_NAME) -U $(LOCAL_DB_USER) -W -Ft > db-project.dump

db-railway-update:
		pg_restore -U postgres -h containers-us-west-152.railway.app -p 8050 -W -Ft -d railway db-project.dump

dev-server-run:
		poetry run flask --app license_plates_stat:app run
	
start:
		poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

lint:
		{ \
    	poetry run flake8 page_analyzer;\
		poetry run flake8 tests;\
    	}

test:
		poetry run pytest

tests-cov:
		poetry run pytest --cov=page_analyzer --cov-report xml

show-active-ports:
		sudo lsof -i -P -n | grep LISTEN
# kill -9 processid - force comand to kill process

.PHONY: install