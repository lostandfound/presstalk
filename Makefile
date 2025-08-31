UV ?= uv

.PHONY: help venv install run console simulate test test-file clean dev lint format typecheck build publish distclean install-global uninstall-global alias-pt alias-pt-bash doctor-global path-zsh path-bash bootstrap run-anywhere

help:
	@echo "Targets: venv install run console simulate test test-file clean dev lint format typecheck build publish distclean install-global uninstall-global alias-pt doctor-global"
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
	@echo "  make install-global # uv tool install --editable . (global shim)"
	@echo "  make alias-pt       # add 'pt' alias to ~/.zshrc (zsh)"
	@echo "  make alias-pt-bash  # add 'pt' alias to ~/.bashrc (bash)"
	@echo "  make doctor-global  # check which presstalk is executed"
	@echo "  make path-zsh       # add ~/.local/bin to PATH in ~/.zshrc"
	@echo "  make path-bash      # add ~/.local/bin to PATH in ~/.bashrc"
	@echo "  make bootstrap      # auto-detect (uv/pipx/venv) and set up to run anywhere"
	@echo "  make run-anywhere   # auto-detect and run from here without cd"

venv:
	$(UV) venv

install:
	$(UV) run python task.py install

run:
	$(UV) run python task.py run

console:
	$(UV) run python task.py run --console

CHUNKS ?= hello world
DELAY ?= 40
simulate:
	$(UV) run python task.py simulate --chunks $(CHUNKS) --delay-ms $(DELAY)

test:
	$(UV) run python task.py test

FILE ?= tests/test_controller.py
test-file:
	$(UV) run python task.py test --file $(FILE)

clean:
	$(UV) run python task.py clean

KEY ?= ctrl
MODE ?= hold
dev:
	$(UV) run presstalk run --mode $(MODE) --hotkey $(KEY)

# Install as a user tool (no need to cd into repo)
install-global:
	$(UV) tool install --editable .
	@echo "Installed as a user tool. Ensure \"$$HOME/.local/bin\" is in PATH."

uninstall-global:
	$(UV) tool uninstall presstalk || true

# Optional: add a convenient alias to zshrc that runs from this repo without install
alias-pt:
	@grep -q "alias pt=" $$HOME/.zshrc || echo "alias pt='uv run --with $(PWD) presstalk run'" >> $$HOME/.zshrc
	@echo "Added alias 'pt' to ~/.zshrc (open a new shell or run: source ~/.zshrc)"

alias-pt-bash:
	@grep -q "alias pt=" $$HOME/.bashrc || echo "alias pt='uv run --with $(PWD) presstalk run'" >> $$HOME/.bashrc
	@echo "Added alias 'pt' to ~/.bashrc (open a new shell or run: source ~/.bashrc)"

# Show which presstalk binary will execute
doctor-global:
	@command -v presstalk >/dev/null 2>&1 && which presstalk && presstalk --version || echo "presstalk not found in PATH"

path-zsh:
	@grep -q 'HOME/.local/bin' $$HOME/.zshrc || echo 'export PATH="$$HOME/.local/bin:$$PATH"' >> $$HOME/.zshrc
	@echo "Ensured ~/.local/bin is in PATH (zsh). Open a new shell or run: source ~/.zshrc"

path-bash:
	@grep -q 'HOME/.local/bin' $$HOME/.bashrc || echo 'export PATH="$$HOME/.local/bin:$$PATH"' >> $$HOME/.bashrc
	@echo "Ensured ~/.local/bin is in PATH (bash). Open a new shell or run: source ~/.bashrc"

# One-shot setup that chooses the best available installer
bootstrap:
	@if command -v uv >/dev/null 2>&1; then \
		echo "[bootstrap] Using uv tool install"; \
		$(UV) tool install --editable . && echo "[ok] presstalk installed globally via uv"; \
		echo "Tip: run 'make path-zsh' or 'make path-bash' if presstalk is not found"; \
	elif command -v pipx >/dev/null 2>&1; then \
		echo "[bootstrap] Using pipx"; \
		pipx install . && echo "[ok] presstalk installed globally via pipx"; \
		echo "Tip: ensure pipx path is configured (pipx ensurepath)"; \
	else \
		echo "[bootstrap] Falling back to venv at $$HOME/.venvs/presstalk"; \
		mkdir -p $$HOME/.venvs && python3 -m venv $$HOME/.venvs/presstalk && . $$HOME/.venvs/presstalk/bin/activate && python -m pip install -U pip && python -m pip install -e . && echo "alias pt='$$HOME/.venvs/presstalk/bin/presstalk run'" >> $$HOME/.zshrc && echo "alias pt='$$HOME/.venvs/presstalk/bin/presstalk run'" >> $$HOME/.bashrc && echo "[ok] Added 'pt' alias to your shell rc"; \
	fi

# Run from this repo without prior install; picks best method available
run-anywhere:
	@if command -v presstalk >/dev/null 2>&1; then \
		presstalk run; \
	elif command -v uv >/dev/null 2>&1; then \
		$(UV) run --with . presstalk run; \
	else \
		PYTHONPATH=$(PWD)/src python3 -m presstalk.cli run; \
	fi

lint:
	$(UV) run python task.py lint

format:
	$(UV) run python task.py format

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
