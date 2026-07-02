install:
	clear
	@echo "Creating virtual environment and installing dependancies"
	uv sync
	clear
	@echo "Everything setup, ready to launch"

run:
	clear
	uv run python -m src $(ARGS)

debug:
	uv run python3 -m pdb -m src

lint:
	clear
	uv run flake8 src/
	uv run mypy src/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --follow-imports=silent

lint-strict:
	clear
	uv run flake8 src/
	uv run mypy src/ --strict --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --follow-imports=silent

clean:
	clear
	rm -rf .mypy_cache
	rm -rf `find . -type d -name "__pycache__"`
	clear
	@echo "Caches deleted"

fclean: clean
	clear
	rm -rf uv.lock
	rm -rf .venv
	rm -rf src/Call_Me_Maybe.egg-info
	rm -rf data/output
	clear
	@echo "Virtual environment and caches deleted"
	
.PHONY: install run debug lint lint-strict clean fclean