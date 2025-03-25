import os
from dotenv import load_dotenv, find_dotenv
from typing import List
from pydantic_settings import BaseSettings

load_dotenv(find_dotenv(), override=True)


class Settings(BaseSettings):
    # LOG_FILE: str = os.getenv("LOG_FILE", "logs.txt")
    # HTTP_PORT: int = int(os.getenv("HTTP_PORT", 8080))

    IPF_URL: str = os.getenv("IPF_URL")
    IPF_TOKEN: str = os.getenv("IPF_TOKEN")
    IPF_SNAPSHOT_ID: str = os.getenv("IPF_SNAPSHOT_ID", "$last")
    IPF_VERIFY: bool = eval(os.getenv("IPF_VERIFY", "False").title())

    FOLDER_JSON: str = os.getenv("FOLDER_JSON", "json")
    FOLDER_JSON_ORIGINAL_SN: str = os.getenv("FOLDER_OLD_SN", "w_original_sn")
    FOLDER_JSON_HOSTNAME: str = os.getenv("FOLDER_OLD_SN", "w_hostname")
    FOLDER_JSON_NEW_SN: str = os.getenv("FOLDER_OLD_SN", "w_new_sn")
    KEYS_TO_REMOVE: List[str] = ["savedAt", "favorite", "id", "userId", "username"] # keys to remove from the JSON file, as the new views will note keep that information
    # KEYS_TO_REMOVE: List[str] = os.getenv("KEYS_TO_REMOVE", "").split(",")
