# Embutils
Python utilities for embedded projects

[![PyPi Version](https://img.shields.io/pypi/v/embutils.svg?style=flat-square)](https://pypi.org/project/embutils/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/embutils.svg?style=flat-square)](https://pypi.org/project/embutils/)
[![License](https://img.shields.io/:license-mit-blue.svg?style=flat-square)](https://badges.mit-license.org)
[![LGTM](https://img.shields.io/lgtm/grade/python/github/cwichel/embutils.svg?style=flat-square)](https://lgtm.com/projects/g/cwichel/embutils)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Docs Status](https://readthedocs.org/projects/embutils/badge/?version=latest)](https://embutils.readthedocs.io/en/latest/?badge=latest)

## Usage
### Install
```shell
pip install embutils
```

## Development
### Cloning the repository
```shell
git clone git@github.com:cwichel/embutils.git
```

### Setup python environment
#### System Requirements
- Interpreter: Python3.8+
- Modules:
   ```requirements.txt
   poetry                     >= 1.2
   poethepoet[poetry_plugin]  >= 0.16
   ```

#### Install process
1. Open a console on the repository root.
2. Create a virtual environment using poetry:
   ```shell
   poetry install --with docs,lint,test
   ```
   **Note:** This will install a full development environment.
3. Install pre-commit hooks locally:
   ```shell
   poetry run pre-commit install
   ```
   **Note:** Development requirements for the project should include pre-commit module.

### Running development tasks
1. Check available tasks:
   ```shell
   poetry poe
   ```
2. Execute a task using:
   ```shell
   poetry poe <task-name>
   ```
   For example, running the project linters:
   ```shell
   poetry poe run-linters
   ```
