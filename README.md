# Confluence CLI

## Contributing

### Prerequisites

1. Install [pyenv](https://github.com/pyenv/pyenv)
1. Install Python 3.7
   ```console
   $ pyenv install 3.7.13
   ```
1. Install [Poetry](https://python-poetry.org/)

### Setup

1. Clone the project.
   ```console
   $ git clone git@github.com:Bellese/confluence-utils.git
   ```
1. From the project root, set the project Python version
   ```console
   $ cd confluence-utils
   $ poetry env use python
   ```
1. Install dependencies and pre-commit hooks
   ```console
   $ poetry install && poetry run pre-commit install --hook-type commit-msg
   ```
1. (Optional) Open in VS Code
   ```console
   $ poetry shell
   $ code .
   ```

## Testing Locally

```console
$ poetry run confluence --help
Usage: confluence [OPTIONS] COMMAND [ARGS]...

  Commandline interface for Confluence.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  publish

$ poetry run confluence publish --help
Usage: confluence publish [OPTIONS] PATH

Options:
  --url TEXT    The URL to the Confluence API. Optionally set with
                CONFLUENCE_URL.  [required]
  --space TEXT  Confluence API Space. Optionally set with CONFLUENCE_SPACE.
                [required]
  --token TEXT  Confluence API Token. Optionally set with CONFLUENCE_TOKEN.
                [required]
  --help        Show this message and exit.

```
