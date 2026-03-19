"""
Compatibility entrypoint.

The FastAPI composition root is `app.http_app` (more descriptive), but many tools
and tutorials default to `uvicorn app.main:app`, so we keep this shim.
"""

from app.http_app import app, create_app  # re-export

