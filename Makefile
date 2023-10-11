identify:
	poetry run bean-identify config.py tests/t.csv

extract-dry-run:
	poetry run bean-extract config.py tests/t.csv

bean-file-dry-run:
	poetry run bean-file --dry-run config.py tests/t.csv

fava:
	poetry run fava -d lejon.beancount
