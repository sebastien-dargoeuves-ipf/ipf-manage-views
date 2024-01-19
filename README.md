# Manage Views Script

This script provides command-line interface (CLI) commands to manage views. It supports backup, restore, delete, and force update operations.

## Requirements

- Python 3.6 or higher
- typer
- loguru
- python-ipfabric
- pydantic-settings

## Installation

1. Clone the repository
2. Install the dependencies with pip:

\```bash
pip install -r requirements.txt
\```

## Usage

### Backup

To backup views, run:

\```bash
python manage_views.py backup [--unattended]
\```

The `--unattended` flag is optional and allows you to backup views without asking for confirmation.

### Restore

To restore views, run:

\```bash
python manage_views.py restore [--single-file] [--all-files]
\```

You must select either `--single-file` to restore a single view or `--all-files` to restore all saved views.

### Delete

To delete views, run:

\```bash
python manage_views.py delete [--unattended]
\```

The `--unattended` flag is optional and allows you to delete views without asking for confirmation.

### Force Update

To backup, delete, and restore views, run:

\```bash
python manage_views.py do-all [--unattended]
\```

The `--unattended` flag is optional and allows you to perform all operations without asking for confirmation.

## Logging

The script logs its operations to a file named `log_file.log` in the `logs` directory. The log file is rotated when it reaches 1 MB in size, and logs older than 180 days are deleted. The log file is compressed using `tar.gz`.