all: clean run

install:
	. env/bin/activate; pip install --editable .

clean:
	rm -rf __pycache__/ src/__pycache__/

clean_db:
	rm -f config/database.sqlite3

lint:
	. env/bin/activate; pylint controller.py || exit 0

freeze:
	. env/bin/activate; pip freeze > requirements.txt

test:
	. env/bin/activate; pytest tests.py

dev:
	. env/bin/activate; export FLASK_APP=controller.py; export FLASK_ENV=development; python controller.py

run: 
	. env/bin/activate; uwsgi --socket 127.0.0.1:12345 --protocol=http -w wsgi:APP;
