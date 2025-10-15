from pydantic import BaseModel
from typing import Optional, Dict

# ---- User models ----
class LoginRequest(BaseModel):
    username: str
    password: str

# ---- Generic ES models ----
class IndexRequest(BaseModel):
    index_name: str
    body: Optional[Dict] = None

class DocumentBody(BaseModel):
    username: str
    password: str

class DocumentRequest(BaseModel):
    index_name: str
    document_id: str | None = None
    body: DocumentBody

class UpdateRequest(BaseModel):
    index_name: str
    document_id: str
    body: dict
