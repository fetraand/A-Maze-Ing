NAME         = a_maze_ing.py
CONFIG       = config.txt
PYTHON       = python3
PIP          = pip3
RM           = rm -rf

MYPY_FLAGS   = . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
               --disallow-untyped-defs --check-untyped-defs

BASE_EXCLUDE = .git,__pycache__,.mypy_cache,.pytest_cache,build,dist,*.egg-info
VENV_NAME    := $(notdir $(VIRTUAL_ENV))

ifneq ($(VIRTUAL_ENV),)
FLAKE8_EXCLUDE = $(BASE_EXCLUDE),$(VENV_NAME)
else
FLAKE8_EXCLUDE = $(BASE_EXCLUDE)
endif

FLAKE8_FLAGS = . --exclude=$(FLAKE8_EXCLUDE)

all: run

install:
	@$(PIP) install --upgrade pip -q
	@$(PIP) install -r requirements.txt -q
	@if ls mazegen-*.whl >/dev/null 2>&1; then \
		$(PIP) install --force-reinstall mazegen-*.whl -q; \
		echo "Dependencies and mazegen package installed."; \
	else \
		echo "No mazegen-*.whl found, run 'make build-mazegen' first."; \
		echo "Dependencies installed."; \
	fi
	@echo

build-mazegen:
	@echo
	@$(PYTHON) -m build

run:
	@$(PYTHON) $(NAME) $(CONFIG)

debug:
	@$(PYTHON) -m pdb $(NAME) $(CONFIG)

clean:
	@echo
	@if [ -f $(CONFIG) ]; then \
		OUT=$$(grep -E '^[[:space:]]*OUTPUT_FILE[[:space:]]*=' $(CONFIG) \
			| head -n1 | cut -d'=' -f2 | tr -d '[:space:]'); \
		if [ -n "$$OUT" ]; then $(RM) "$$OUT"; fi; \
	fi
	@$(RM) .mypy_cache .pytest_cache dist build
	@find . -type d -name "*.egg-info" -exec $(RM) {} +
	@find . -type d -name "__pycache__" -exec $(RM) {} +

lint:
	@flake8 $(FLAKE8_FLAGS)
	@mypy $(MYPY_FLAGS)

lint-strict:
	@flake8 $(FLAKE8_FLAGS)
	@mypy --strict .

.PHONY: all install run debug clean lint lint-strict build-mazegen