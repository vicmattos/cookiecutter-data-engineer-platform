SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
VENV = .venv
# make it work on windows
ifeq ($(OS), Windows_NT)
    VEXECS = $(VENV)/Scripts
else
	VEXECS = $(VENV)/bin
endif
PYTHON = $(VEXECS)/python


.PHONY: help
help:  ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: setup
setup:  ## Create development environment with venv and pre-commit
	make $(PYTHON)
	make pre-commit-install


.PHONY: pre-commit-install
pre-commit-install: $(VEXECS)  ## Execute pre-commit installation of script and hooks
	$(VEXECS)/pre-commit install --install-hooks --overwrite


.PHONY: bake
BAKE_OUTPUT=output
BAKE_ARGS=--no-input
bake: $(PYTHON)  ## Call cookiecutter with default options targeting `output/`
	$(PYTHON) -m cookiecutter . --output-dir $(BAKE_OUTPUT) --overwrite-if-exists $(BAKE_ARGS)


.PHONY: bake-watch
bake-watch: $(VEXECS)  ## Execute watchdog's `watchmedo` to "re-bake" whenever some template's relevant file changes
	$(VEXECS)/watchmedo shell-command \
		--command='make bake' \
		--recursive \
		\{\{cookiecutter.project_directory\}\} \
		hooks \
		cookiecutter.json


.PHONY: test
test: $(PYTHON)  ## Call pytest with xdist filtering out slow tests
	$(PYTHON) -m pytest -n auto -m "not slow"


.PHONY: test-slow
test-slow: $(PYTHON)  ## Call pytest with xdist for tests marked as slow
	$(PYTHON) -m pytest -n auto -m slow


.PHONY: test-all
test-all: $(PYTHON)  ## Call pytest with xdist
	$(PYTHON) -m pytest -n auto


.PHONY: docs-serve
docs-serve: $(PYTHON)  ## Call mkdocs to serve current docs in local server
	$(PYTHON) -m mkdocs serve


.PHONY: commit
commit: $(VEXECS)  ## Execute commitizen's `cz commit` to create commit message and use it in `git commit`
ifeq ($(shell git diff --name-only --cached),)
	$(error Git stage empty. Add files to commit.)
endif
	$(VEXECS)/cz commit --dry-run --write-message-to-file .cz-msg
	git commit --file .cz-msg && rm -f .cz-msg || rm -f .cz-msg


.PHONY: clean
clean: $(PYTHON)  ## Call cleanpy skipping envs and `rm -rf` directories `sites/`, `outputs/` and `.ruff_cache`
	rm -rf site/
	rm -rf $(BAKE_OUTPUT)
	rm -rf .ruff_cache/
	$(PYTHON) -m cleanpy --all --exclude-envs .


$(PYTHON):
	$(SYSTEM_PYTHON) -m venv $(VENV)
	$(VEXECS)/pip install --upgrade pip
	$(VEXECS)/pip install -r requirements-dev.txt

$(VEXECS): $(PYTHON)

$(VENV): $(PYTHON)
