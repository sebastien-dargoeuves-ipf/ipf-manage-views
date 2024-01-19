import json
import os
import re
from datetime import datetime

from ipfabric import IPFClient
from ipfabric.tools import DiscoveryHistory
from loguru import logger
import typer

from modules.classDefinitions import Settings


def select_json_file(settings: Settings):
    # # Get the list of files in the folders
    file_list = []
    for root, dirs, files in os.walk(settings.FOLDER_JSON):
        file_list.extend(os.path.join(root, file) for file in files)
    if not file_list:
        logger.warning(
            f"No files found in the '{settings.FOLDER_JSON}' folder, nothing to restore."
        )
        return False
    # Display the list of files with corresponding numbers
    print(f"List of files in the '{settings.FOLDER_JSON}' folder:")
    for i, filename in enumerate(file_list):
        print(f"{i+1}. {filename}")

    while True:
        # Prompt for file selection
        selection = typer.prompt(
            "Enter the number corresponding to the JSON file to read", type=int
        )

        # Check if the selected number is within range
        if 1 <= selection <= len(file_list):
            # Get the selected file name
            return file_list[selection - 1]
        else:
            print("Selection outside the scope. Please select a valid number.")


def select_json_folder(
    settings: Settings, unattended: bool = False, latest_backup_folder: str = None
):
    """
    Select a JSON folder for restoration.

    Args:
        settings (Settings): The settings object containing the folder path.
        unattended (bool): Flag indicating whether the selection should be done automatically without user interaction.

    Returns:
        List[str]: A list of file paths within the selected folder.
    """
    folder_list = []
    for root, dirs, files in os.walk(settings.FOLDER_JSON):
        folder_list.extend(
            os.path.join(root, dir)
            for dir in dirs
            if dir.endswith(settings.FOLDER_JSON_ORIGINAL_SN)
            or dir.endswith(settings.FOLDER_JSON_HOSTNAME)
            or dir.endswith(settings.FOLDER_JSON_NEW_SN)
        )
    if not folder_list:
        logger.warning(
            f"No files found in the '{settings.FOLDER_JSON}' folder, nothing to restore."
        )
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
                "Enter the number corresponding to the Folder to restore (ideally use a `xxx/w_hostname` folder)", type=int
            )

            # Check if the selected number is within range
            if 1 <= selection <= len(folder_list):
                # Get the selected file name
                folder_name = folder_list[selection - 1]
                break
            else:
                print("Selection outside the scope. Please select a valid number.")
    return [os.path.join(folder_name, file) for file in os.listdir(folder_name)]


def get_sn_to_device_mapping(ipf: IPFClient):
    """
    Get the mapping of serial number to device name
    :param ipf: IPFClient object
    :return: dict
    """
    dh = DiscoveryHistory(ipf)
    return dh.get_all_history(columns=["sn", "hostname"])


def get_last_hostname_to_sn_mapping(ipf: IPFClient):
    """
    Get the mapping of serial number to device name
    :param ipf: IPFClient object
    :return: dict
    """
    return ipf.inventory.devices.all(columns=["hostname", "sn"])


def replace_sn_with_hostname(destination_file, json_data, sn_to_device_mapping):
    """
    Replace the serial number with the hostname
    :param sn_to_device_mapping: dict
    :return: None
    """
    # Replace the serial number with the hostname
    for item in sn_to_device_mapping:
        sn = item["sn"]
        hostname = item["hostname"]
        # Check if the sn exists in the positions dictionary
        if sn in json_data["positions"]:
            # Replace the sn key with hostname key
            json_data["positions"][hostname] = json_data["positions"].pop(sn)

    # Save the updated JSON file
    # new_file = f"w_hostname/{destination_file.replace('.json','_HOSTNAME.json')}"
    with open(destination_file, "w") as file:
        json.dump(json_data, file, indent=4)

    logger.debug(f"JSON file successfully created/updated: {destination_file}")
    return destination_file


def replace_hostname_with_last_sn(selected_file, json_data, hostname_to_sn_mapping):
    """
    Replace the serial number with the hostname
    :param sn_to_device_mapping: dict
    :return: None
    """
    # Replace the serial number with the hostname
    for item in hostname_to_sn_mapping:
        sn = item["sn"]
        hostname = item["hostname"]
        # Check if the sn exists in the positions dictionary
        if hostname in json_data["positions"]:
            # Replace the sn key with hostname key
            json_data["positions"][sn] = json_data["positions"].pop(hostname)

    # Save the updated JSON file
    new_file = selected_file.replace("_HOSTNAME.json", "_NEW_SN.json")
    with open(new_file, "w") as file:
        json.dump(json_data, file, indent=4)

    logger.debug(f"JSON file successfully created/updated: {new_file}")
    return new_file


def create_view(current_view_name, ipf, selected_json, unattended):
    if not unattended:
        new_view_name = typer.prompt(
            "Chose a name for this view", type=str, default=f"{current_view_name}"
        )
    else:
        new_view_name = f"{current_view_name}"

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
        ipf_url (str): The base URL of the IPF server.
        ipf_token (str): The authentication token for accessing the IPF server.

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
        os.makedirs(f"{backup_folder}/{settings.FOLDER_JSON_HOSTNAME}")
        os.makedirs(f"{backup_folder}/{settings.FOLDER_JSON_NEW_SN}")

    ipf = IPFClient(
        base_url=settings.IPF_URL, auth=settings.IPF_TOKEN, verify=settings.IPF_VERIFY
    )
    sn_to_device_mapping = get_sn_to_device_mapping(ipf)
    all_views = ipf.get("graphs/views").json()
    for view_data in all_views:
        view_name = re.sub(r'[<>:"/\\|?*&#^()\[\]+={}%$@!`~]', "", view_data["name"])
        for key in settings.KEYS_TO_REMOVE:
            if key in view_data:
                del view_data[key]
        # Replace the serial number with the hostname
        replace_sn_with_hostname(
            f"{backup_folder}/{settings.FOLDER_JSON_HOSTNAME}/{view_name}_HOSTNAME.json",
            view_data,
            sn_to_device_mapping,
        )
        # Save the original JSON file
        with open(
            f"{backup_folder}/{settings.FOLDER_JSON_ORIGINAL_SN}/{view_name}.json", "w"
        ) as file:
            json.dump(view_data, file, indent=4)
        logger.debug(f"View {view_name} successfully backed up")
    return f"{backup_folder}/{settings.FOLDER_JSON_HOSTNAME}"


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

        # if the file is a raw json from IP Fabric, we need to replace all SN by HOSTNAME
        # using the information from the Discovery History
        if not selected_file.endswith("_HOSTNAME.json") and not selected_file.endswith(
            "_NEW_SN.json"
        ):
            sn_to_device_mapping = get_sn_to_device_mapping(ipf)
            # if the device deosn't end with HOSTNAME, we need to copy it in the w_hostname folder
            selected_file = selected_file.replace(".json", "_HOSTNAME.json")
            selected_file = replace_sn_with_hostname(
                selected_file.replace(
                    settings.FOLDER_JSON_ORIGINAL_SN, settings.FOLDER_JSON_HOSTNAME
                ),
                selected_json,
                sn_to_device_mapping,
            )

        # if the file is a json with HOSTNAME instead of SN, we need to replace all HOSTNAME by SN
        # using the information from the latest snapshot
        if selected_file.endswith("_HOSTNAME.json"):
            last_hostname_to_sn_mapping = get_last_hostname_to_sn_mapping(ipf)
            selected_file = replace_hostname_with_last_sn(
                selected_file.replace("w_hostname", "w_new_sn"),
                selected_json,
                last_hostname_to_sn_mapping,
            )

        # Now we can create the view
        if selected_file.endswith("_NEW_SN.json"):
            create_view(current_view_name, ipf, selected_json, unattended)
            return True

    if not os.path.exists(settings.FOLDER_JSON):
        os.makedirs(settings.FOLDER_JSON)
    ipf = IPFClient(
        base_url=settings.IPF_URL, auth=settings.IPF_TOKEN, verify=settings.IPF_VERIFY
    )
    if scope == "single":
        selected_file = select_json_file(settings)
        if selected_file:
            restore_selected_file(selected_file, ipf, False)
    else:
        files_in_folder = select_json_folder(settings, unattended, latest_backup_folder)
        if not files_in_folder:
            logger.error("No files found in the selected folder, nothing to restore.")
            return False
        for selected_file in files_in_folder:
            restore_selected_file(selected_file, ipf, unattended=True)
    return True


def f_delete_views(settings: Settings, unattended: bool):
    """
    Delete all views in IPF.

    Args:
        ipf_url (str): The base URL of the IPF server.
        ipf_token (str): The authentication token for accessing the IPF server.

    Returns:
        None
    """
    if not unattended:
        confirm = typer.confirm("Are you sure you want to delete all views?")
        if not confirm:
            logger.warning("Aborting deletion of views")
            return False
    ipf = IPFClient(
        base_url=settings.IPF_URL, auth=settings.IPF_TOKEN, verify=settings.IPF_VERIFY
    )
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
