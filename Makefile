install:
	clear
	@echo "Creating virtual environment and installing dependancies"
	uv venv
	uv pip install -e .
	clear
	@echo "Everything setup, ready to launch"

run:
	clear
	uv run python -m src $(ARGS)

debug:
	uv run python3 -m pdb main.py

clean:
	clear
	rm -rf .venv
	rm -rf data/output
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -r {} +
	clear
	@echo "✨ Virtual environment and caches deleted ✨"

lint:
	clear
	uv run flake8 src/
	uv run mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --follow-imports=silent

lint-strict:
	clear
	uv run flake8 src/
	uv run mypy src/ --strict --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --follow-imports=silent