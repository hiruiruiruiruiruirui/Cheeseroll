"""Aggregate all v1 API routers."""

from fastapi import APIRouter

from .upload import router as upload_router
from .process import router as process_router
from .records import router as records_router
from .export import router as export_router
from .auth import router as auth_router
from .subscription import router as subscription_router
from .payment import router as payment_router
from .wrong_answers import router as wrong_answers_router
from .share import router as share_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, tags=["Auth"])
api_router.include_router(upload_router, tags=["Upload"])
api_router.include_router(process_router, tags=["Process"])
api_router.include_router(records_router, tags=["Records"])
api_router.include_router(export_router, tags=["Export"])
api_router.include_router(subscription_router, tags=["Subscription"])
api_router.include_router(payment_router, tags=["Payment"])
api_router.include_router(wrong_answers_router, tags=["Wrong Answers"])
api_router.include_router(share_router, tags=["Share"])
