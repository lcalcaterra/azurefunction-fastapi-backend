import os

from fastapi import APIRouter, UploadFile, File, HTTPException

from src.db.utils import (
    is_es_up, get_index, update_document, search_document
)
from src.storage.connection import container_client
from src.ai.connection import openai_client
from src.models.elastic import IndexRequest, DocumentRequest, UpdateRequest, LoginRequest
from src.models.ai import SearchRequest
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/status")
async def stato():
    return {"Function Staus": "Up and Running"}

# Elasticsearch
@router.get("/elastic/status")
def status():
    return {"elasticsearch_up": is_es_up()}

@router.get("/elastic/index/{index_name}")
def get_index_api(index_name: str):
    return get_index(index_name)



# Specific User Index
USER_INDEX = os.getenv("USER_INDEX", "users")
@router.post("/users/login")
def login(req: LoginRequest):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"username": req.username}},
                    {"term": {"password": req.password}}
                ]
            }
        }
    }
    resp = search_document(USER_INDEX, query)
    if resp["hits"]["total"]["value"] > 0:
        return {"status": "OK"}
    return {"status": "KO"}



# Azure Storage Account
@router.post("/storage/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        blob_client = container_client.get_blob_client(file.filename)
        blob_client.upload_blob(file.file, overwrite=True)

        return {"status": "Upload succeeded", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Failed: {str(e)}")


# Azure OpenAI
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
@router.post("/ai/search")
async def search(request: SearchRequest):
    try:
        response = openai_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.query},
            ],
            max_tokens=200,
        )

        reply = response.choices[0].message.content
        return {"status": "success", "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Can't search. Retry later: {str(e)}")
