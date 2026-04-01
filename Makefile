.PHONY: install download build app test lint

install:
	pip install -r requirements.txt

download:
	python scripts/download_data.py

build:
	python scripts/build_dataset.py

app:
	python scripts/run_app.py

test:
	pytest

lint:
	ruff check .

