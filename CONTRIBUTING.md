# Contributing to UrsaProxy

Thanks for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/alanbato/ursaproxy.git
cd ursaproxy
uv sync --group dev --group test
```

## Making Changes

1. Fork the repository and create a branch for your changes
2. Make your changes
3. Run the checks:
   ```bash
   uv run ruff check --fix .
   uv run ruff format .
   uv run ty check
   uv run pytest
   ```
4. Commit with a clear message describing the change
5. Open a pull request

## Code Style

- Code is formatted with [ruff](https://docs.astral.sh/ruff/)
- Type hints are checked with [ty](https://github.com/astral-sh/ty)
- Pre-commit hooks run automatically if installed: `uv run pre-commit install`

## Tests

All new code should include tests. Tests use pytest with respx for mocking HTTP requests:

```bash
uv run pytest           # Run all tests
uv run pytest -v        # Verbose output
uv run pytest -x        # Stop on first failure
```

## Questions?

Open an issue if you have questions or want to discuss a larger change before implementing it.
