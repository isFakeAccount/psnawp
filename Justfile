# Justfile for project tasks

# Format the Justfile
just-fmt:
    just --fmt --unstable

# Run code and docstring formatting and linter
fmt:
    poetry run docstrfmt src
    poetry run ruff format src
    poetry run ruff check src --fix

    poetry run docstrfmt tests
    poetry run ruff format tests

# Run pre-commit hooks
pre-commit:
    poetry run pre-commit run --all-files

# Run static analysis and linting
static:
    poetry run mypy src
    poetry run pyright src

# Build and check documentation
docs:
    cd docs && make apidoc
    cd docs && make clean
    cd docs && make html
    cd docs && make linkcheck

# Run integration test
integration clean="FALSE":
    #!/usr/bin/env bash
    if [[ {{clean}} = "clean=TRUE" ]]; then
        echo 'Removing Old cassettes files.'
        rm tests/integration_tests/integration_test_psnawp_api/cassettes/*.json;
    fi
    poetry run pytest --cov-config=pyproject.toml

# Runs all tasks
all: pre-commit static fmt docs integration
