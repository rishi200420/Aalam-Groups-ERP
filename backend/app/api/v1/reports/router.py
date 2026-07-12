import csv
import io
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.auth import UserRead
from app.schemas.common import APIResponse
from app.schemas.reports import (
    DeadStockRead,
    DispatchReportRead,
    InventoryReportRead,
    LowStockReportRead,
    OrderReportRead,
    OutletReportRead,
    SalesReportRead,
    StockMovementReportRead,
    TopSellingRead,
    WarehouseReportRead,
)
from app.services.reports_service import ReportsService

router = APIRouter()


@router.get("/status")
async def reports_module_status():
    return {"module": "reports", "status": "ready"}


@router.get("/sales", response_model=APIResponse[SalesReportRead])
async def sales_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
    brand: str | None = None,
):
    return APIResponse(success=True, message="Sales report generated", data=ReportsService(db).sales_report(current_user, start_date, end_date, brand))


@router.get("/inventory", response_model=APIResponse[InventoryReportRead])
async def inventory_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    warehouse_id: str | None = None,
):
    return APIResponse(success=True, message="Inventory report generated", data=ReportsService(db).inventory_report(current_user, warehouse_id))


@router.get("/stock-movements", response_model=APIResponse[StockMovementReportRead])
async def stock_movement_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
    warehouse_id: str | None = None,
    movement_type: str | None = None,
):
    return APIResponse(
        success=True,
        message="Stock movement report generated",
        data=ReportsService(db).stock_movement_report(current_user, start_date, end_date, warehouse_id, movement_type),
    )


@router.get("/dispatch", response_model=APIResponse[DispatchReportRead])
async def dispatch_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
    status: str | None = None,
):
    return APIResponse(success=True, message="Dispatch report generated", data=ReportsService(db).dispatch_report(current_user, start_date, end_date, status))


@router.get("/orders", response_model=APIResponse[OrderReportRead])
async def order_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
    status: str | None = None,
):
    return APIResponse(success=True, message="Order report generated", data=ReportsService(db).order_report(current_user, start_date, end_date, status))


@router.get("/outlets", response_model=APIResponse[OutletReportRead])
async def outlet_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
):
    return APIResponse(success=True, message="Outlet report generated", data=ReportsService(db).outlet_report(current_user, start_date, end_date))


@router.get("/warehouses", response_model=APIResponse[WarehouseReportRead])
async def warehouse_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Warehouse report generated", data=ReportsService(db).warehouse_report(current_user))


@router.get("/top-selling", response_model=APIResponse[TopSellingRead])
async def top_selling_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=20, ge=1, le=100),
):
    return APIResponse(success=True, message="Top selling report generated", data=ReportsService(db).top_selling_report(current_user, start_date, end_date, limit))


@router.get("/low-stock", response_model=APIResponse[LowStockReportRead])
async def low_stock_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    warehouse_id: str | None = None,
):
    return APIResponse(success=True, message="Low stock report generated", data=ReportsService(db).low_stock_report(current_user, warehouse_id))


@router.get("/dead-stock", response_model=APIResponse[DeadStockRead])
async def dead_stock_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    threshold_days: int = Query(default=60, ge=1, le=365),
):
    return APIResponse(success=True, message="Dead stock report generated", data=ReportsService(db).dead_stock_report(current_user, threshold_days))


@router.get("/export")
async def export_report(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    report: str = Query(description="One of: sales, inventory, stock-movements, dispatch, orders, outlets, warehouses, top-selling, low-stock, dead-stock"),
    start_date: date | None = None,
    end_date: date | None = None,
    brand: str | None = None,
    warehouse_id: str | None = None,
    status: str | None = None,
    movement_type: str | None = None,
    threshold_days: int = Query(default=60, ge=1, le=365),
):
    filename, header, rows = ReportsService(db).export_csv(
        current_user,
        report,
        start_date=start_date,
        end_date=end_date,
        brand=brand,
        warehouse_id=warehouse_id,
        status=status,
        movement_type=movement_type,
        threshold_days=threshold_days,
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
