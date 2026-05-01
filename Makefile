MAP ?= $(error Usage: make run MAP=<map_file>)

install:
	pip install -r requirements.txt

run:
	python3 main.py $(MAP)

run-visual:
	python3 main.py $(MAP) --visual

run-capacity:
	python3 main.py $(MAP) --capacity-info

run-all:
	python3 main.py $(MAP) --visual --capacity-info

debug:
	python3 -m pdb main.py $(MAP)

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -nme .mypy_cache -exec rm -rf {} +

.PHONY: install run debug lint lint-strict clean