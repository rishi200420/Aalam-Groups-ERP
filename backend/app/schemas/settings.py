from app.schemas.common import SchemaBase


class SystemSettingsRead(SchemaBase):
    business_name: str
    support_email: str | None = None
    support_phone: str | None = None
    address: str | None = None
    gst_number: str | None = None
    default_currency: str
    low_stock_default_threshold: int
    invoice_footer_note: str | None = None


class SystemSettingsUpdate(SchemaBase):
    business_name: str | None = None
    support_email: str | None = None
    support_phone: str | None = None
    address: str | None = None
    gst_number: str | None = None
    default_currency: str | None = None
    low_stock_default_threshold: int | None = None
    invoice_footer_note: str | None = None


class NotificationPreferenceRead(SchemaBase):
    notify_orders: bool
    notify_dispatch: bool
    notify_stock: bool
    notify_system: bool


class NotificationPreferenceUpdate(SchemaBase):
    notify_orders: bool | None = None
    notify_dispatch: bool | None = None
    notify_stock: bool | None = None
    notify_system: bool | None = None
