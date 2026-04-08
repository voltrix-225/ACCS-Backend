from pydantic import BaseModel
from enum import Enum


class ActionType(str, Enum):
    MAKE_CALL = "MAKE_CALL"
    OPEN_APP = "OPEN_APP"
    SEND_SMS = "SEND_SMS"
    SET_REMINDER = "SET_REMINDER"
    OPEN_URL = "OPEN_URL"
    CREATE_NOTE = "CREATE_NOTE"
    READ_NOTIFICATIONS = "READ_NOTIFICATIONS"
    SPOTIFY_PLAY = "SPOTIFY_PLAY"
    SPOTIFY_PAUSE = "SPOTIFY_PAUSE"
    SPOTIFY_NEXT = "SPOTIFY_NEXT"
    SPOTIFY_PREVIOUS = "SPOTIFY_PREVIOUS"
    SPOTIFY_PLAY_PLAYLIST = "SPOTIFY_PLAY_PLAYLIST"
    OPEN_GMAIL = "OPEN_GMAIL"
    SEND_EMAIL = "SEND_EMAIL"
    SEND_WHATSAPP = "SEND_WHATSAPP"
    GET_NOTE = "GET_NOTE"
    SEARCH_NOTE = "SEARCH_NOTE"
    SUMMARIZE_NOTIFICATIONS = "SUMMARIZE_NOTIFICATIONS"    
    FLASHLIGHT_ON = "FLASHLIGHT_ON"
    FLASHLIGHT_OFF = "FLASHLIGHT_OFF"
    VOLUME_UP = "VOLUME_UP"
    VOLUME_DOWN = "VOLUME_DOWN"
    MAX_VOLUME = "VOLUME_MAX"
    MIN_VOLUME = "VOLUME_MIN"
    OPEN_SETTINGS = "OPEN_SETTINGS"
    GENERAL_CHAT = "GENERAL_CHAT"


class IntentResponse(BaseModel):
    action: ActionType
    parameters: dict
    confidence: float
    missing_fields: list[str] = []
    requires_input: bool = False
    requires_confirmation: bool = False