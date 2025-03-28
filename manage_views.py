import datetime
import os

from loguru import logger
import typer

from modules.classDefinitions import Settings
from modules.views_functions import (
    f_backup_views,
    f_delete_views,
    f_restore_views,
)

settings = Settings()
app = typer.Typer(
    add_completion=False,
    pretty_exceptions_show_locals=False,
)


@app.callback()
def logging_configuration():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    default_log_dir = os.path.join(root_dir, "logs")
    os.makedirs(default_log_dir, exist_ok=True)
    log_file_path = os.path.join(default_log_dir, "log_file.log")
    logger.add(
        log_file_path,
        retention="180 days",
        rotation="1 MB",
        level="INFO",
        compression="tar.gz",
    )
    logger.info("---- NEW EXECUTION OF SCRIPT ----")


@app.command("backup")
def backup(
    unattended: bool = typer.Option(
        False,
        "--unattended",
        "-u",
        help="Backup views, without asking for confirmation",
    ),
):
    execution_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if f_backup_views(settings=settings, execution_time=execution_time, unattended=unattended):
        logger.info("Backup completed successfully")
    else:
        logger.warning("Backup failed")


@app.command("restore")
def restore(
    single_view: bool = typer.Option(
        False,
        "--single-file",
        "-s",
        help="Restore a single view",
    ),
    all_views: bool = typer.Option(
        False,
        "--all-files",
        "-a",
        help="Restore all saved views",
    ),
):
    if single_view or all_views:
        scope = "single" if single_view else "all"
        if f_restore_views(
            settings=settings,
            scope=scope,
        ):
            logger.info("Restore completed successfully")
        else:
            logger.warning("Restore failed")
    else:
        logger.warning("None or both option(s) selected. Please select either --single-file or --all-files")


@app.command("delete")
def delete(
    unattended: bool = typer.Option(
        False,
        "--unattended",
        "-u",
        help="Delete views, without asking for confirmation",
    ),
):
    if f_delete_views(settings=settings, unattended=unattended):
        logger.info("Delete completed successfully")
    else:
        logger.warning("Delete failed")

if __name__ == "__main__":
    app()
