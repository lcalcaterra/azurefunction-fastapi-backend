import os

from fastapi import APIRouter, Request, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

from src.db.utils import (
    is_es_up, get_index, search_document
)
from src.storage.connection import container_client
from src.ai.connection import openai_client

from src.models.elastic import LoginRequest
from src.models.ai import SearchRequest
from src.models.logs import LogRequest

from src.utils.logger import get_logger, send_logs

from src.utils.security import create_access_token, verify_user_from_header

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


@router.get("/users/session")
async def check_session(request: Request):
    try:
        username = verify_user_from_header(request)
        return {"authenticated": True, "username": username}
    except HTTPException as e:
        return JSONResponse(status_code=200, content={"authenticated": False})
    

# Specific User Index
USER_INDEX = os.getenv("USER_INDEX", "users")

@router.post("/users/login")
def login(req: LoginRequest):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"username": req.username}},
                    {"term": {"password": req.password}}  # TODO: replace with hashed password check
                ]
            }
        }
    }
    resp = search_document(USER_INDEX, query)
    if resp["hits"]["total"]["value"] == 0:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user_doc = resp["hits"]["hits"][0]["_source"]

    # TODO: in production, store hashed passwords and verify:
    # if not bcrypt.verify(req.password, user_doc["password"]):
    #     raise HTTPException(status_code=401, detail="Invalid credentials")
    if req.password != user_doc["password"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(req.username)

    return JSONResponse(status_code=200, content={"status": "OK", "access_token": token, "token_type": "bearer", "username": req.username})


@router.post("/users/logout")
async def logout():
    response = JSONResponse(content={"status": "logged out"})
    return response


# Azure Storage Account
@router.post("/storage/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    username = verify_user_from_header(request)
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    try:
        blob_client = container_client.get_blob_client(file.filename)
        blob_client.upload_blob(file.file, overwrite=True)

        return {"status": "Upload succeeded", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Failed: {str(e)}")


# Azure OpenAI
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
@router.post("/ai/search")
async def search(search_req: SearchRequest, request: Request):
    username = verify_user_from_header(request)
    if not search_req.query or len(search_req.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Empty query")
    try:
        response = openai_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "Sei un assistente utile."},
                {"role": "user", "content": search_req.query},
            ],
            max_tokens=200,
        )

        reply = response.choices[0].message.content
        return {"status": "success", "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Can't search. Retry later: {str(e)}")

# App Insights
@router.post("/logs")
async def send_to_app_insights(request: LogRequest):
    try:
        send_logs(logger, request.level, request.message)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Log sending failed: {str(e)}")