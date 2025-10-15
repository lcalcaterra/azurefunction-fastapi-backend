import os
from openai import AzureOpenAI

# ⚡ Configure Azure OpenAI client
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

if not AZURE_OPENAI_KEY or not AZURE_OPENAI_ENDPOINT:
    raise RuntimeError("Azure OpenAI configuration missing")

openai_client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)
