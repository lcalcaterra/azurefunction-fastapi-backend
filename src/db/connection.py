import os
from elasticsearch import Elasticsearch

ES_HOST = os.getenv("ELASTIC_HOST", "https://localhost:9200")
ES_USER = os.getenv("ELASTIC_USER", "elastic")
ES_PWD = os.getenv("ELASTIC_PASSWORD", "PcC+fifn2OQ6oS=iM*Xf")

def get_es_client() -> Elasticsearch:
    return Elasticsearch(hosts=[ES_HOST], basic_auth=(ES_USER, ES_PWD), verify_certs=False)
