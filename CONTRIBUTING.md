# Contributing

Thank you for considering contributing to Android MS11! This project uses `pytest` for automated tests. Before running the tests, make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

After installing the requirements you can run the full suite with `pytest` or simply use the provided make target:

```bash
make test
```

The `test` target installs the dependencies and then runs `pytest` for you.
