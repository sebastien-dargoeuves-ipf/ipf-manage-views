
import typer
import datetime
from loguru import logger

from modules.views_functions import f_backup_views, f_restore_views, f_delete_views
from modules.classDefinitions import Settings

settings = Settings()
app = typer.Typer(add_completion=False, pretty_exceptions_show_locals = False, pretty_exceptions_short=True)


@app.command()
def main(
    backup_views: bool = typer.Option(
        False,
        "--backup-views",
        "-b",
        help="Backup existing views",
    ),
    restore_single_view: bool = typer.Option(
        False,
        "--restore-single-view",
        "-rs",
        help="Restore existing views",
    ),
    restore_views: bool = typer.Option(
        False,
        "--restore-views",
        "-ra",
        help="Restore all saved views",
    ),
    delele_views: bool = typer.Option(
        False,
        "--delete-views",
        "-d",
        help="Delete existing views",
    ),
    unattended: bool = typer.Option(
        False,
        "--unattended",
        "-u",
        help="Backup, delete and restore views, without asking for confirmation",
    ),
):

    logger.add("log_file.log")
    execution_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("---- NEW EXECUTION OF SCRIPT ----")


    if backup_views and f_backup_views(settings=settings, execution_time=execution_time, unattended=False):
        logger.info("Backup of views completed successfully")

    if restore_single_view or restore_views:
        scope = "single" if restore_single_view else "all"
        if f_restore_views(settings=settings, execution_time=execution_time, scope=scope, unattended=False):
            logger.info("Restore of views completed successfully")

    if delele_views and f_delete_views(settings=settings, unattended=unattended):
            logger.info("Deletion of views completed successfully")

    if unattended:
        f_backup_views(settings=settings, execution_time=execution_time, unattended=False)
        f_delete_views(settings=settings, unattended=unattended)
        f_restore_views(settings=settings, execution_time=execution_time, scope="all", unattended=False)



if __name__ == "__main__":
    app()
