all: clean run

source:
	source env/bin/active

install:
	pip install -r requirements.txt 

clean:
	rm -rf __pycache__/ src/__pycache__/

clean_db:
	rm -f config/database.sqlite3

lint:
	~/.local/bin/pylint controller.py

freeze:
	pip freeze > requirements.txt

run:
	export FLASK_APP=controller.py; export FLASK_ENV=development; python controller.py 
