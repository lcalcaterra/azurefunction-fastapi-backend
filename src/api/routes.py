import os, jwt, datetime
from passlib.hash import bcrypt

from fastapi import APIRouter, Request, UploadFile, File, HTTPException
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
from src.utils.security import verify_user

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
SECRET_KEY = os.getenv("JWT_SECRET", "")

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
    if resp["hits"]["total"]["value"] == 0:
        return {"status": "KO"}

    user_doc = resp["hits"]["hits"][0]["_source"]
    # NB: la password su database dev'essere salvata codificandola prima in base64
    # if not bcrypt.verify(req.password, user_doc["password"]):
    if req.password != user_doc["password"]: # rimuovere questa linea
        return {"status": "KO"}

    # Crea token JWT
    token = jwt.encode(
        {"sub": req.username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
        SECRET_KEY,
        algorithm="HS256"
    )

    response = JSONResponse(content={"status": "OK"})
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=3600,
        path="/"
    )
    return response


@router.get("/users/session")
async def check_session(request: Request):
    """
    Verifica se l'utente è autenticato.
    Usa il cookie HttpOnly 'session' e decode del JWT.
    """
    try:
        username = verify_user(request)
        return {"authenticated": True, "username": username}
    except HTTPException:
        # verify_user alza 401 in caso di token invalido
        return {"authenticated": False}


@router.post("/users/logout")
async def logout():
    """
    Invalida la sessione rimuovendo il cookie JWT.
    """
    response = JSONResponse(content={"status": "logged out"})
    response.delete_cookie(
        key="session",
        path="/",
        secure=True,
        httponly=True,
        samesite="Strict"
    )
    return response


# Azure Storage Account
@router.post("/storage/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    username = verify_user(request)
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
    username = verify_user(request)
    if not search_req.query or len(search_req.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Empty query")
    try:
        response = openai_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
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
async def send_to_app_insights(request: LogRequest, message, level = "info"):
    if not request.log:
        raise HTTPException(status_code=400, detail="Missing log content")
    try:
        send_logs(request.log, level, message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Log sending Failed: {str(e)}")