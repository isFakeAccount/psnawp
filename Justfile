# Justfile for project tasks

# Format the Justfile
just-fmt:
    just --fmt --unstable

# Run code and docstring formatting and linter
fmt:
    poetry run docstrfmt src/psnawp_api/
    poetry run ruff format src/psnawp_api/
    poetry run ruff format tests/
    poetry run ruff check src/psnawp_api/ --fix

# Run pre-commit hooks
pre-commit:
    poetry run pre-commit run --all-files

# Run static analysis and linting
static:
    poetry run mypy src/psnawp_api/
    poetry run pyright src/psnawp_api/

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
