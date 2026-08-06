from pydantic import BaseModel


class WSMessage(BaseModel):
    type: str
    message: str | None = None
    audio: str | None = None