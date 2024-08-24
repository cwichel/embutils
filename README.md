# embutils
## Cloning the repository
```shell
git clone git@github.com:cwichel/embutils.git
```

## Project Structure
The project is structured as a [Polylith](https://polylith.gitbook.io/polylith/) project. The Polylith project structure
is a modular architecture that allows the project to be split into multiple modules. Each module is a standalone project
that can be developed and tested independently. The modules are then combined into a single project that can be deployed
as a single artifact.

For more information about the project structure, please refer to:
1. [Polylith documentation](https://polylith.gitbook.io/polylith/)
2. [Polylith Python project](https://github.com/DavidVujic/python-polylith)

## Configuration
### System
#### Requirements
- Operating System: `Any`

### Python
#### Requirements
- Interpreter: `Python3.10+`
- Modules:
   ```requirements.txt
   poetry                     >= 1.5
   poetry-multiproject-plugin >= 1.3
   poetry-polylith-plugin     >= 1.6
   ```

#### Setup process
1. Open a terminal on the repository root.
2. Optional. Use poetry to create the virtual environment with a specific python version:
    ```shell
    poetry env use <python_version>
    ```
   Example:
    ```shell
    poetry env use python3.10
    ```
3. Create the virtual environment using poetry:
    ```shell
    poetry install --with dev,lint,test
    ```
   **Note:** The `--with` flag is optional and will install the modules required for development, linting, and testing.
4. Optional. Install the pre-commit hooks:
    ```shell
    poetry run pre-commit install
    ```
   **Note:** Developers should install the pre-commit hooks to ensure that the code is formatted and linted before committing.

## Development
### Running Development Tasks
1. Open a terminal on the repository root.
2. Run the development tasks using:
    ```shell
    poetry run <task>
    ```
   Available tasks:
    ```
    builder      : Build the applications in the projects directory.
    formatters   : Run the formatters (flake8, isort, black) over the repository.
    linters      : Run the linters (pylint, bandit, etc) over the repository.
    tests        : Run the tests in the tests directory. This generates a coverage report.
    tests-report : Start a web server to view the coverage report.
    type-checks  : Run the type checks (mypy) over the repository.
    ```
   Example:
    ```shell
    poetry run formaters
    ```
3. Optional. Test the pre-commit hooks:
    ```shell
    poetry run pre-commit run --all-files
    ```
   **Note:** Developers should test the pre-commit hooks to ensure that the code is formatted and linted before committing.
