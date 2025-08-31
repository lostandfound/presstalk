UV ?= uv

.PHONY: help venv install run console simulate test test-file clean dev

help:
	@echo "Targets: venv install run console simulate test test-file clean dev"
	@echo "Examples:"
	@echo "  make venv && source .venv/bin/activate && make install"
	@echo "  make run            # global hotkey (default)"
	@echo "  make console        # interactive console mode"
	@echo "  make simulate CHUNKS='hello world' DELAY=40"
	@echo "  make test           # run all tests"
	@echo "  make test-file FILE=tests/test_controller.py"

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

