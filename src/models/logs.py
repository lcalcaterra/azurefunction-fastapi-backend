from pydantic import BaseModel

class LogRequest(BaseModel):
    message: str
    level: str = "info"