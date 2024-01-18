import os
from typing import List
from dotenv import load_dotenv, find_dotenv
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
    KEYS_TO_REMOVE: List[str]= ["savedAt", "favorite", "id", "userId", "username"]
    # KEYS_TO_REMOVE: List[str] = os.getenv("KEYS_TO_REMOVE", "").split(",")


# class CvpComponent(BaseModel):
#     deviceId: str
#     entityId: str
#     hostname: str
#     tags: Dict[str, Any]
#     type: str


# class AristaCvpWebhook(BaseModel):
#     acknowledged: bool
#     components: List[CvpComponent]
#     description: str
#     event_type: str
#     fired_at: datetime
#     is_firing: bool
#     is_test: bool
#     key: str
#     resolved_at: datetime
#     severity: str
#     source: str
#     title: str
