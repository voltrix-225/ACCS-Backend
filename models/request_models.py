from pydantic import BaseModel


class UserInput(BaseModel):
    user_command: str

class NotificationRequest(BaseModel):
    text : str