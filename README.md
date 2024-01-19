# Manage Views Script

This script provides command-line interface (CLI) commands to manage views. It supports backup, restore, delete, and force update operations.

## Requirements

- Python 3.6 or higher
- typer
- loguru
- ipfabric
- pydantic-settings

## Installation

1. Clone the repository
2. Install the dependencies with pip:

    ```bash
    pip install -r requirements.txt
    ```

3. Create the `.env` file using the `.env.sample` and change the variables accordingly

    ```bash
    cp .env.sample .env
    vi .env
    ```

## Automation usage

To run as part as the automated process, you will want to use this command:

```bash
python manage_views.py do-all --unattended
```

This will:

1. get a backup of all views in IP Fabric, this is a JSON file, containing the SN as of when the view was created
2. create a new JSON, replacing that SN by the matching hostname
3. delete all views in IP Fabric
4. find the SN matching the hostname in the LAST snapshot of IP Fabric
5. Push the views in IP Fabric

## Usage

### Backup

Files will be saved in the `json` folder. To manually backup views, run:

```bash
python manage_views.py backup [--unattended]
```

The `--unattended` flag is optional and allows you to backup views without asking for destination folder.

### Restore

To restore views, run:

```bash
python manage_views.py restore [--single-file] [--all-files]
```

You must select either `--single-file` to restore a single view or `--all-files` to restore all saved views inside a folder. A prompt will ask you to select the file or folder.

### Delete

```warning
This will delete all views from IP Fabric, make sure you do have a backup of everything beforehand.
```

To delete all views from IP Fabric, run:

```bash
python manage_views.py delete [--unattended]
```

The `--unattended` flag is optional and allows you to delete views without asking for confirmation.

### Force Update

To backup, delete, and restore views, run:

```bash
python manage_views.py do-all [--unattended]
```

The `--unattended` flag is optional and allows you to perform all operations without asking for confirmation.
