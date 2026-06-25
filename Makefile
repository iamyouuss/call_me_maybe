MAIN= main.py
SRC= engine.py /
		parsing_json.py

install:
	pip install -r requirements.txt

run:
	python3 main.py

debug:
	python3 -m pdb main.py

clean:
	rm -rf __pycache__/*

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . 