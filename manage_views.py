
import typer
import datetime
from loguru import logger

from modules.views_functions import f_backup_views, f_restore_views, f_delete_views
from modules.classDefinitions import Settings

settings = Settings()
app = typer.Typer(add_completion=False, pretty_exceptions_show_locals = False, pretty_exceptions_short=True)


@app.callback()
def logging_configuration():
    logger.add("log_file.log")
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
    unattended: bool = typer.Option(
        False,
        "--unattended",
        "-u",
        help="Restore views, without asking for confirmation",
    ),
):
    if single_view or all_views:
        scope = "single" if single_view else "all"
        execution_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if f_restore_views(settings=settings, execution_time=execution_time, scope=scope, unattended=unattended):
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

@app.command("do-all")
def force_update(
    unattended: bool = typer.Option(
        False,
        "--unattended",
        "-u",
        help="Backup/Delete/Restore views, without asking for confirmation",
    ),
):
    execution_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f_backup_views(settings=settings, execution_time=execution_time, unattended=unattended)
    f_delete_views(settings=settings, unattended=unattended)
    f_restore_views(settings=settings, execution_time=execution_time, scope="all", unattended=False)


if __name__ == "__main__":
    app()
