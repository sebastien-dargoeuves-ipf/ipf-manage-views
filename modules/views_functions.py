import json
import os
import re

from ipfabric import IPFClient
from loguru import logger
import typer

from modules.classDefinitions import Settings


def select_json_file(settings: Settings):
    """
    UI to select a JSON file for restoration
    Args:
        settings (Settings): The settings object containing the folder path.
    Returns:
        str: The path to the selected JSON file.
    """

    # # Get the list of files in the folders
    file_list = []
    for root, dirs, files in os.walk(settings.FOLDER_JSON):
        file_list.extend(os.path.join(root, file) for file in files)
    if not file_list:
        logger.warning(f"No files found in the '{settings.FOLDER_JSON}' folder, nothing to restore.")
        return False
    # Display the list of files with corresponding numbers
    print(f"List of files in the '{settings.FOLDER_JSON}' folder:")
    for i, filename in enumerate(file_list):
        print(f"{i+1}. {filename}")

    while True:
        # Prompt for file selection
        selection = typer.prompt("Enter the number corresponding to the JSON file to read", type=int)

        # Check if the selected number is within range
        if 1 <= selection <= len(file_list):
            # Get the selected file name
            return file_list[selection - 1]
        else:
            print("Selection outside the scope. Please select a valid number.")


def select_json_folder(settings: Settings, unattended: bool = False, latest_backup_folder: str = None):
    """
    UI to select a JSON folder for restoration.

    Args:
        settings (Settings): The settings object containing the folder path.
        unattended (bool): Flag indicating whether the selection should be done automatically without user interaction.
        latest_backup_folder (str): The path to the latest backup folder.

    Returns:
        List[str]: A list of file paths within the selected folder.
    """
    folder_list = []
    for root, dirs, files in os.walk(settings.FOLDER_JSON):
        folder_list.extend(
            os.path.join(root, dir)
            for dir in dirs
            if dir.endswith(settings.FOLDER_JSON_ORIGINAL_SN)
        )
    if not folder_list:
        logger.warning(f"No files found in the '{settings.FOLDER_JSON}' folder, nothing to restore.")
        return False

    if unattended:
        folder_name = latest_backup_folder
    else:
        print(f"List of folders in the `{settings.FOLDER_JSON}` directory:")
        for i, folder_name in enumerate(folder_list):
            print(f"{i+1}. {folder_name}")

        while True:
            # Prompt for file selection
            selection = typer.prompt(
                "Enter the number corresponding to the Folder to restore",
                type=int,
            )

            # Check if the selected number is within range
            if 1 <= selection <= len(folder_list):
                # Get the selected file name
                folder_name = folder_list[selection - 1]
                break
            else:
                print("Selection outside the scope. Please select a valid number.")
    return [os.path.join(folder_name, file) for file in os.listdir(folder_name)]


def create_view(current_view_name, ipf, selected_json, unattended):
    """
    Create a new view in IPF based on the selected JSON data.
    Args:
        current_view_name (str): The name of the current view.
        ipf (IPFClient): The IPF client instance.
        selected_json (dict): The JSON data for the new view.
        unattended (bool): Flag indicating whether to prompt for a new view name.
    """
    if unattended:
        new_view_name = f"{current_view_name}"
    else:
        new_view_name = typer.prompt("Chose a name for this view", type=str, default=f"{current_view_name}")
    
    selected_json["name"] = new_view_name
    post_create_view = ipf.post("graphs/views", json=selected_json)
    if post_create_view.status_code == 200:
        logger.info(f"View `{new_view_name}` successfully created - {post_create_view}")
    else:
        logger.error(f"View `{new_view_name}` NOT created - {post_create_view}")


def f_backup_views(settings: Settings, execution_time, unattended: bool = False):
    """
    Backup all views from IPF to JSON files.

    Args:
        settings (Settings): The settings object containing the IPF configuration.
        execution_time (str): The execution time of the backup operation.
        unattended (bool, optional): Flag indicating whether the backup should be performed without user interaction. Defaults to False.

    Returns:
        None
    """
    if unattended:
        backup_folder_name = f"{execution_time.replace(':','').replace(' ','_')}_backup"
    else:
        backup_folder_name = typer.prompt(
            "Chose a name for this backup folder",
            type=str,
            default=f"{execution_time.replace(':','').replace(' ','_')}_backup",
        )

    backup_folder = os.path.join(settings.FOLDER_JSON, backup_folder_name)
    if not os.path.exists(backup_folder):
        os.makedirs(f"{backup_folder}/{settings.FOLDER_JSON_ORIGINAL_SN}")

    ipf = IPFClient(base_url=settings.IPF_URL, auth=settings.IPF_TOKEN, verify=settings.IPF_VERIFY)
    all_views = ipf.get("graphs/views").json()
    for view_data in all_views:
        view_name = re.sub(r'[<>:"/\\|?*&#^()\[\]+={}%$@!`~]', "", view_data["name"])
        for key in settings.KEYS_TO_REMOVE:
            if key in view_data:
                del view_data[key]
        # Save the original JSON file
        with open(f"{backup_folder}/{settings.FOLDER_JSON_ORIGINAL_SN}/{view_name}.json", "w") as file:
            json.dump(view_data, file, indent=4)
        logger.debug(f"View {view_name} successfully backed up")
    return f"{backup_folder}/{settings.FOLDER_JSON_ORIGINAL_SN}"


def f_restore_views(
    settings: Settings,
    scope: str,
    unattended: bool = False,
    latest_backup_folder: str = None,
):
    """
    Restore views in IPF based on selected JSON files.

    Args:
        settings (Settings): The settings object containing the IPF configuration.
        scope (str): The scope of the restore operation. Can be "single" or "multiple".
        unattended (bool, optional): Flag indicating whether the restore operation should be performed without user interaction. Defaults to False.
        latest_backup_folder (str, optional): The path to the latest backup folder. Defaults to None.

    Returns:
        bool: True if the views are successfully restored, False otherwise.
    """

    def restore_selected_file(selected_file, ipf: IPFClient, unattended: bool = False):
        """
        Restore a selected JSON file as a view in IPF.

        Args:
            selected_file (str): The path to the selected JSON file.

        Returns:
            bool: True if the view is successfully created, False otherwise.
        """
        # Read the JSON file
        with open(selected_file, "r") as file:
            selected_json = json.load(file)
            # Use the json_data variable to access the contents of the file
            logger.debug(f"JSON file `{selected_file}` successfully read.")
        current_view_name = selected_json["name"]

        # Now we can create the view
        create_view(current_view_name, ipf, selected_json, unattended)
        return True

    if not os.path.exists(settings.FOLDER_JSON):
        os.makedirs(settings.FOLDER_JSON)
    ipf = IPFClient(base_url=settings.IPF_URL, auth=settings.IPF_TOKEN, verify=settings.IPF_VERIFY)
    if scope == "single":
        selected_file = select_json_file(settings)
        if selected_file:
            restore_selected_file(selected_file=selected_file, ipf=ipf, unattended=False)
    else:
        files_in_folder = select_json_folder(settings=settings, unattended=unattended, latest_backup_folder=latest_backup_folder) 
        if not files_in_folder:
            logger.error("No files found in the selected folder, nothing to restore.")
            return False
        for selected_file in files_in_folder:
            restore_selected_file(selected_file=selected_file, ipf=ipf, unattended=True)
    return True


def f_delete_views(settings: Settings, unattended: bool):
    """
    Delete all views in IPF

    Args:
        ipf_url (str): The base URL of the IPF server.
        ipf_token (str): The authentication token for accessing the IPF server.

    Returns:
        None
    """
    if not unattended:
        confirm = typer.confirm("Are you sure you want to delete all existing views?")
        if not confirm:
            logger.warning("Aborting deletion of views")
            return False
    ipf = IPFClient(base_url=settings.IPF_URL, auth=settings.IPF_TOKEN, verify=settings.IPF_VERIFY)
    all_views = ipf.get("graphs/views").json()
    for view_data in all_views:
        view_name = view_data["name"]
        view_id = view_data["id"]
        delete_view = ipf.delete(f"graphs/views/{view_id}")
        if delete_view.status_code == 204:
            logger.info(f"View `{view_name}` Deleted - {delete_view}")
        else:
            logger.error(f"View `{view_name}` NOT deleted - {delete_view}")
    return True
