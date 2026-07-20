"""
Aggregate router for API version 1.

Every new endpoint module in `api/v1/endpoints/` gets registered here with
its own prefix and tags. This file should stay a thin list of
`include_router` calls — no route logic lives here.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health

api_router = APIRouter()
api_router.include_router(health.router)

# Future phases register here, e.g.:
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
