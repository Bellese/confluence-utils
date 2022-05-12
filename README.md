# Confluence Utils

CLI Utilities for Confluence.

## Installation

### System Requirements

1. Python 3.7+
2. [Cairo](https://cairographics.org/)

#### Installing Cairo

For mac systems you can use homebrew and run `brew install cairo`

For alpine linux run
`apk add --no-cache build-base cairo-dev cairo cairo-tools jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev`

For all other systems follow the instructions on [cairo's download page](https://cairographics.org/download/)

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
