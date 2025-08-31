UV ?= uv

.PHONY: help venv install run console simulate test test-file clean dev lint format typecheck build publish distclean

help:
	@echo "Targets: venv install run console simulate test test-file clean dev lint format typecheck build publish distclean"
	@echo "Examples:"
	@echo "  make venv && source .venv/bin/activate && make install"
	@echo "  make run            # global hotkey (default)"
	@echo "  make console        # interactive console mode"
	@echo "  make simulate CHUNKS='hello world' DELAY=40"
	@echo "  make test           # run all tests"
	@echo "  make test-file FILE=tests/test_controller.py"
	@echo "  make lint           # ruff/flake8 if available"
	@echo "  make format         # ruff format / black if available"
	@echo "  make typecheck      # mypy if available"
	@echo "  make build          # build sdist+wheel (requires 'build')"
	@echo "  make publish        # upload to PyPI (requires 'twine')"

venv:
	$(UV) venv

install:
	$(UV) pip install -e .

run:
	$(UV) run presstalk run

console:
	$(UV) run presstalk run --console

CHUNKS ?= hello world
DELAY ?= 40
simulate:
	$(UV) run presstalk simulate --chunks $(CHUNKS) --delay-ms $(DELAY)

test:
	$(UV) run python -m unittest -v

FILE ?= tests/test_controller.py
test-file:
	$(UV) run python -m unittest $(FILE) -v

clean:
	rm -rf build dist .pytest_cache
	find . -name __pycache__ -prune -exec rm -rf {} +
	find . -name '*.egg-info' -prune -exec rm -rf {} +

KEY ?= ctrl
MODE ?= hold
dev:
	$(UV) run presstalk run --mode $(MODE) --hotkey $(KEY)

lint:
	@if command -v ruff >/dev/null 2>&1; then \
		$(UV) run ruff check . ; \
	elif command -v flake8 >/dev/null 2>&1; then \
		$(UV) run flake8 . ; \
	else \
		echo "No linter found (install ruff or flake8)" ; \
	fi

format:
	@if command -v ruff >/dev/null 2>&1; then \
		$(UV) run ruff format . ; \
	elif command -v black >/dev/null 2>&1; then \
		$(UV) run black . ; \
	else \
		echo "No formatter found (install ruff or black)" ; \
	fi

typecheck:
	@if command -v mypy >/dev/null 2>&1; then \
		$(UV) run mypy src tests ; \
	else \
		echo "mypy not installed" ; \
	fi

build:
	@if command -v python >/dev/null 2>&1; then \
		$(UV) run python -m build ; \
	else \
		echo "Python not found" ; \
	fi

publish:
	@if command -v twine >/dev/null 2>&1; then \
		$(UV) run twine upload --skip-existing dist/* ; \
	else \
		echo "twine not installed" ; \
	fi

distclean: clean
	rm -rf .venv
