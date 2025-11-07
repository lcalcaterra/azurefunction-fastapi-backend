import os
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class SWASecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures requests originate from the allowed SWA frontend
    and are routed through Azure Static Web Apps infrastructure.
    Disabled automatically in local development.
    """

    def __init__(self, app):
        super().__init__(app)
        self.env = os.getenv("AZURE_FUNCTIONS_ENVIRONMENT", "Development")

    async def dispatch(self, request: Request, call_next):
        # ✅ Skip checks if running locally
        if self.env.lower() == "development":
            return await call_next(request)

        # --- 2. Check x-ms-client-principal header ---
        if not request.headers.get("x-ms-client-principal"):
            raise HTTPException(status_code=403, detail="Forbidden: not called from SWA")

        return await call_next(request)
