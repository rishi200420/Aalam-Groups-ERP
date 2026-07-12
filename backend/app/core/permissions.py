from enum import Enum


class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    FOUNDER = "founder"
    DISTRIBUTOR = "distributor"
    WAREHOUSE = "warehouse"
    SALES_EXECUTIVE = "sales_executive"


class Permission(str, Enum):
    DASHBOARD_VIEW = "dashboard:view"
    USERS_MANAGE = "users:manage"
    OUTLETS_MANAGE = "outlets:manage"
    OUTLETS_CREATE = "outlets:create"
    OUTLETS_EDIT_ASSIGNED = "outlets:edit_assigned"
    OUTLETS_VISIT = "outlets:visit"
    OUTLETS_UPLOAD_PHOTO = "outlets:upload_photo"
    PRODUCTS_MANAGE = "products:manage"
    PRODUCTS_VIEW = "products:view"
    ORDERS_MANAGE = "orders:manage"
    ORDERS_CREATE = "orders:create"
    DISPATCH_MANAGE = "dispatch:manage"
    DISPATCH_UPDATE = "dispatch:update"
    INVENTORY_MANAGE = "inventory:manage"
    REPORTS_VIEW = "reports:view"
    ANALYTICS_VIEW = "analytics:view"
    SETTINGS_MANAGE = "settings:manage"
    EXPORTS = "exports:run"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.SUPER_ADMIN: set(Permission),
    Role.FOUNDER: set(Permission),
    Role.DISTRIBUTOR: {
        Permission.DASHBOARD_VIEW,
        Permission.OUTLETS_CREATE,
        Permission.OUTLETS_EDIT_ASSIGNED,
        Permission.OUTLETS_VISIT,
        Permission.OUTLETS_UPLOAD_PHOTO,
        Permission.PRODUCTS_VIEW,
        Permission.ORDERS_CREATE,
        Permission.DISPATCH_UPDATE,
    },
    Role.WAREHOUSE: {
        Permission.DASHBOARD_VIEW,
        Permission.INVENTORY_MANAGE,
        Permission.DISPATCH_MANAGE,
    },
    Role.SALES_EXECUTIVE: {
        Permission.DASHBOARD_VIEW,
        Permission.OUTLETS_CREATE,
        Permission.OUTLETS_VISIT,
        Permission.OUTLETS_UPLOAD_PHOTO,
        Permission.ORDERS_CREATE,
    },
}


def role_has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
