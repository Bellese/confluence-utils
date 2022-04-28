# Confluence Utils

CLI Utilities for Confluence.

## Installation

### System Requirements

1. Python 3.7+

### Install with `pipx` (recommended)

1. Install [`pipx`](https://pypa.github.io/pipx/)
1. Run `pipx install confluence-utils`

### Install with `pip`:

1. Run `pip install confluence-utils`

## Usage

### Commands

#### `publish`

```console
$ confluence publish --help
Usage: confluence publish [OPTIONS] PATH

Options:
  --token TEXT  Confluence API Token. Optionally set with CONFLUENCE_TOKEN.
                [required]
  --space TEXT  Confluence Space. Optionally set with CONFLUENCE_SPACE.
                [required]
  --url TEXT    The URL to the Confluence API. Optionally set with
                CONFLUENCE_URL.  [required]
  --help        Show this message and exit.
```
