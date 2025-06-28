# Contributing

Thank you for considering contributing to Android MS11! This project uses `pytest` for automated tests.
Before running the tests, make sure all dependencies are installed. The easiest way is to run:

```bash
./scripts/setup_test_env.sh
```

This will install both `requirements.txt` and `requirements-test.txt`. You can also perform these steps manually if preferred.

After installing the requirements you can run the full suite with `pytest` or simply use the provided make target:

```bash
make test
```

The `test` target installs the dependencies and then runs `pytest` for you.

For quick checks during development you can run just the mode specific tests
once the requirements are installed:

```bash
pytest -k support_mode -q
pytest -k rls_mode -q
```
