set shell := ["sh", "-c"]

test *args:
    rm -f .coverage
    uv sync --locked
    uv run coverage run -m pytest {{args}}
    uv sync --all-extras --locked
    uv run coverage run --append -m pytest {{args}}
    uv run coverage report -m
    uv run coverage xml
