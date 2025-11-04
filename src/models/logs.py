from pydantic import BaseModel

class LogRequest(BaseModel):
    log: str