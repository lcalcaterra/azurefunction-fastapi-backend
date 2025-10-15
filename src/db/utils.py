from .connection import get_es_client

es = get_es_client()

def is_es_up():
    return es.info()

def get_index(index: str):
    return es.indices.get(index=index)

def create_index(index: str, body: dict | None = None):
    return es.indices.create(index=index, body=body or {})

def delete_index(index: str):
    return es.indices.delete(index=index, ignore=[400, 404])

def insert_document(index: str, body: dict, doc_id: str | None = None):
    return es.index(index=index, id=doc_id, body=body.dict())

def get_document(index: str, doc_id: str):
    return es.get(index=index, id=doc_id, ignore=[404])

def search_document(index: str, query: dict):
    return es.search(index=index, body=query)

def update_document(index: str, doc_id: str, body: dict):
    return es.update(index=index, id=doc_id, body={"doc": body})

def delete_document(index: str, doc_id: str):
    return es.delete(index=index, id=doc_id, ignore=[404])

def get_users(index):
    resp = es.search(index, body={"query": {"match_all": {}}})
    return [hit["_source"] for hit in resp["hits"]["hits"]]