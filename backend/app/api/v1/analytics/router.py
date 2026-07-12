from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.auth import UserRead
from app.schemas.common import APIResponse
from app.schemas.dashboard import DashboardStats
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/dashboard", response_model=APIResponse[DashboardStats])
async def dashboard_stats(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    brand: str | None = Query(default=None, description="Filter by brand: all, tastiq, lemuria"),
):
    return APIResponse(success=True, message="Dashboard stats retrieved", data=DashboardService(db).get_stats(brand))
