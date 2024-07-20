from fastapi import APIRouter
from app.api.v1.resources.load_profile.load_profile import load_router

load_profile_router = APIRouter()

# load_profile_router.include_router(appliance_router, prefix="/appliances", tags=["LoadProfile"])
load_profile_router.include_router(load_router, prefix="", tags=["LoadProfile"])
