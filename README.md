# OrangeHRM Selenium Pytest Suite

This repository contains a Selenium + pytest suite for the OrangeHRM demo application.

## Suggested structure

- `orangehrm/` - project-specific helpers and page objects
  - `pages/` - page object classes for UI flows
  - `components/` - reusable UI components
- `tests/` - pytest test modules and fixtures
  - `conftest.py` - shared browser and page fixtures
- `pytest.ini` - pytest configuration
- `requirements.txt` - Python dependencies

## Why there is no `src/` folder

A `src/` layout is most useful when you are packaging a reusable Python library. For a Selenium test project, keeping the test code and page objects at the repository root is simpler and more idiomatic, especially because pytest can run directly from the repo.

## Prerequisites

This suite expects the OrangeHRM demo application to be running locally before tests are executed.

### Docker prerequisites

The repository includes a Docker Compose setup for the required services:

- MySQL 8.4
- OrangeHRM latest image

Start them with:

```bash
docker compose up -d
```

If you only want the database container, you can still use the MySQL service from the same file.

## Run tests

Activate the virtual environment and run:

```bash
.venv\Scripts\activate
pytest
```

## Notes

- The suite expects ChromeDriver to be available either on the PATH or in the repository root.
- Fixtures are defined in `tests/conftest.py` for browser setup and reusable page objects.
- Page objects are designed for reuse and easier maintenance.
