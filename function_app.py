import azure.functions as func
from fastapi import FastAPI

from src.api.routes import router


fastapi_app = FastAPI(title="Backend Integration", root_path="/api")
fastapi_app.include_router(router)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.function_name(name="HttpFunction")
@app.route(route="{*route}", methods=["GET", "POST"])
async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    Entry point for Azure Function app, forwards all requests to FastAPI app.

    Args:
        req (func.HttpRequest): HTTP request.
        context (func.Context): Azure Function execution context.

    Returns:
        func.HttpResponse: HTTP response from FastAPI.
    """
    return await func.AsgiMiddleware(fastapi_app).handle_async(req, context)