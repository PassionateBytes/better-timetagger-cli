PACKAGE = ./src/better_timetagger_cli
TESTS   = ./tests
REPORTS = ./.reports


.PHONY: build format lint fix typecheck typecheck-report test test-report clean


build: clean format lint typecheck-report test-report
	uv build


format:
	uv run ruff format ${PACKAGE} ${TESTS}
	uv run ruff check --fix --select I,F401 ${PACKAGE} ${TESTS}


lint:
	uv run ruff check ${PACKAGE} ${TESTS}


fix:
	uv run ruff check --fix ${PACKAGE} ${TESTS}


typecheck:
	uv run mypy ${PACKAGE} ${TESTS}


typecheck-report:
	uv run mypy --html-report=${REPORTS}/typecheck ${PACKAGE} ${TESTS}


test:
	uv run pytest --cov=${PACKAGE} --cov-report=term-missing ${TESTS}


test-report:
	uv run pytest --cov=${PACKAGE} --cov-report=term-missing --cov-report=html:${REPORTS}/covreage --report=${REPORTS}/test/index.html --template=html1/index.html ${TESTS}


clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.eggs" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name ".reports" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	rm -rf .coverage
