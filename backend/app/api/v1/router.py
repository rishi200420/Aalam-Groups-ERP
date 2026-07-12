from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.users.router import router as users_router
from app.api.v1.roles.router import router as roles_router
from app.api.v1.brands.router import router as brands_router
from app.api.v1.territories.router import router as territories_router
from app.api.v1.outlets.router import router as outlets_router
from app.api.v1.products.router import router as products_router
from app.api.v1.inventory.router import router as inventory_router
from app.api.v1.orders.router import router as orders_router
from app.api.v1.dispatch.router import router as dispatch_router
from app.api.v1.reports.router import router as reports_router
from app.api.v1.analytics.router import router as analytics_router
from app.api.v1.notifications.router import router as notifications_router
from app.api.v1.uploads.router import router as uploads_router
from app.api.v1.gps.router import router as gps_router
from app.api.v1.activity_logs.router import router as activity_logs_router
from app.api.v1.settings.router import router as settings_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(users_router, prefix="/users", tags=["Users"])
api_v1_router.include_router(roles_router, prefix="/roles", tags=["Roles"])
api_v1_router.include_router(brands_router, prefix="/brands", tags=["Brands"])
api_v1_router.include_router(territories_router, prefix="/territories", tags=["Territories"])
api_v1_router.include_router(outlets_router, prefix="/outlets", tags=["Outlets"])
api_v1_router.include_router(products_router, prefix="/products", tags=["Products"])
api_v1_router.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
api_v1_router.include_router(orders_router, prefix="/orders", tags=["Orders"])
api_v1_router.include_router(dispatch_router, prefix="/dispatch", tags=["Dispatch"])
api_v1_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_v1_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_v1_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_v1_router.include_router(uploads_router, prefix="/uploads", tags=["Uploads"])
api_v1_router.include_router(gps_router, prefix="/gps", tags=["GPS"])
api_v1_router.include_router(activity_logs_router, prefix="/activity-logs", tags=["Activity Logs"])
api_v1_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
