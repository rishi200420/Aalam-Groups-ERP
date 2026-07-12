"""Seed roles, permissions, and demo users."""

import uuid

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import Outlet, OutletContact, Permission, Role, RolePermission, User, UserRole

PERMISSIONS = [
    ("dashboard:view", "View Dashboard", "Access dashboard"),
    ("users:manage", "Manage Users", "Create and manage users"),
    ("outlets:manage", "Manage Outlets", "Full outlet management"),
    ("outlets:create", "Create Outlets", "Add new outlets"),
    ("outlets:edit_assigned", "Edit Assigned Outlets", "Edit assigned outlet records"),
    ("outlets:visit", "Add Outlet Visits", "Record outlet visit notes"),
    ("outlets:upload_photo", "Upload Outlet Photos", "Upload outlet photos"),
    ("products:manage", "Manage Products", "Full product management"),
    ("products:view", "View Products", "View product catalog"),
    ("orders:manage", "Manage Orders", "Full order management"),
    ("orders:create", "Create Orders", "Create orders"),
    ("dispatch:manage", "Manage Dispatch", "Full dispatch management"),
    ("dispatch:update", "Update Dispatch", "Update delivery status"),
    ("inventory:manage", "Manage Inventory", "Inventory operations"),
    ("reports:view", "View Reports", "Access reports"),
    ("analytics:view", "View Analytics", "Access analytics"),
    ("settings:manage", "Manage Settings", "System settings"),
    ("exports:run", "Run Exports", "Export data"),
    ("gps:capture", "Capture GPS", "Capture field GPS coordinates"),
]

ROLES = [
    ("super_admin", "Super Admin", "Full system access across all brands", PERMISSIONS),
    ("founder", "Founder", "Full operational access for Aalam Groups", PERMISSIONS),
    (
        "distributor",
        "Distributor",
        "Field distributor operations",
        [
            ("dashboard:view", "View Dashboard", ""),
            ("outlets:create", "Create Outlets", ""),
            ("outlets:edit_assigned", "Edit Assigned Outlets", ""),
            ("outlets:visit", "Add Outlet Visits", ""),
            ("outlets:upload_photo", "Upload Outlet Photos", ""),
            ("gps:capture", "Capture GPS", ""),
            ("products:view", "View Products", ""),
            ("orders:create", "Create Orders", ""),
            ("dispatch:update", "Update Dispatch", ""),
        ],
    ),
    (
        "warehouse",
        "Warehouse",
        "Warehouse and inventory operations",
        [
            ("dashboard:view", "View Dashboard", ""),
            ("inventory:manage", "Manage Inventory", ""),
            ("dispatch:manage", "Manage Dispatch", ""),
        ],
    ),
    (
        "sales_executive",
        "Sales Executive",
        "Shop visits, lead capture, and territory field activity",
        [
            ("dashboard:view", "View Dashboard", ""),
            ("outlets:create", "Create Outlets", ""),
            ("outlets:visit", "Add Outlet Visits", ""),
            ("outlets:upload_photo", "Upload Outlet Photos", ""),
            ("gps:capture", "Capture GPS", ""),
        ],
    ),
]

FOUNDER_USERS = [
    {
        "email": "faaiq@aalamgroups.com",
        "password": "Faaiq@123",
        "full_name": "Mohammed Faaiq Dhanish MH",
        "phone": "9876543210",
        "role_code": "founder",
    },
    {
        "email": "rishi@aalamgroups.com",
        "password": "Rishi@123",
        "full_name": "Rishi K",
        "phone": "9876543211",
        "role_code": "founder",
    },
    {
        "email": "abhishek@aalamgroups.com",
        "password": "Abhishek@123",
        "full_name": "Abhishek Balaji",
        "phone": "9876543212",
        "role_code": "founder",
    },
]

SAMPLE_OUTLETS = [
    ("Sri Murugan Tea Stall", "Murugan R", "9884001001", "Tambaram", "Chennai", "Chengalpattu", "Tamil Nadu", "600045", "Tambaram", "tea_shop", ["TASTIQ"], 12.9249, 80.1000),
    ("Lemuria Cafe Corner", "Janani S", "9884001002", "Chromepet", "Chennai", "Chengalpattu", "Tamil Nadu", "600044", "Chromepet", "cafe", ["LEMURIA"], 12.9516, 80.1462),
    ("Aachi Bakery", "Karthik P", "9884001003", "Pallavaram", "Chennai", "Chengalpattu", "Tamil Nadu", "600043", "Pallavaram", "bakery", ["TASTIQ", "LEMURIA"], 12.9675, 80.1491),
    ("Green Park Restaurant", "Naveen K", "9884001004", "Medavakkam", "Chennai", "Chengalpattu", "Tamil Nadu", "600100", "Medavakkam", "restaurant", ["TASTIQ"], 12.9171, 80.1923),
    ("Royal Residency Hotel", "Suresh B", "9884001005", "Velachery", "Chennai", "Chennai", "Tamil Nadu", "600042", "Velachery", "hotel", ["LEMURIA"], 12.9756, 80.2207),
    ("Fresh Basket Supermarket", "Priya M", "9884001006", "Guduvanchery", "Chennai", "Chengalpattu", "Tamil Nadu", "603202", "Guduvanchery", "supermarket", ["TASTIQ", "LEMURIA"], 12.8450, 80.0606),
    ("Anbu General Store", "Anbu V", "9884001007", "Sembakkam", "Chennai", "Chengalpattu", "Tamil Nadu", "600073", "Sembakkam", "general_store", ["TASTIQ"], 12.9222, 80.1588),
    ("Metro Tea Point", "Abdul Rahman", "9884001008", "Perungalathur", "Chennai", "Chengalpattu", "Tamil Nadu", "600063", "Perungalathur", "tea_shop", ["TASTIQ"], 12.9048, 80.0889),
    ("Oasis Cafe", "Meera L", "9884001009", "Madipakkam", "Chennai", "Chennai", "Tamil Nadu", "600091", "Madipakkam", "cafe", ["LEMURIA"], 12.9647, 80.1961),
    ("Golden Crust Bakery", "Harish T", "9884001010", "Sholinganallur", "Chennai", "Chennai", "Tamil Nadu", "600119", "Sholinganallur", "bakery", ["TASTIQ", "LEMURIA"], 12.9000, 80.2279),
    ("Spice Route Meals", "Deepak N", "9884001011", "Adyar", "Chennai", "Chennai", "Tamil Nadu", "600020", "Adyar", "restaurant", ["TASTIQ"], 13.0067, 80.2570),
    ("Blue Moon Hotel", "Arun C", "9884001012", "T Nagar", "Chennai", "Chennai", "Tamil Nadu", "600017", "T Nagar", "hotel", ["LEMURIA"], 13.0418, 80.2341),
    ("Daily Needs Mart", "Ramesh G", "9884001013", "Porur", "Chennai", "Chennai", "Tamil Nadu", "600116", "Porur", "supermarket", ["TASTIQ"], 13.0382, 80.1565),
    ("Selvi Stores", "Selvi A", "9884001014", "Nanganallur", "Chennai", "Chennai", "Tamil Nadu", "600061", "Nanganallur", "general_store", ["TASTIQ", "LEMURIA"], 12.9807, 80.1882),
    ("Morning Cup Tea", "Bala S", "9884001015", "Mylapore", "Chennai", "Chennai", "Tamil Nadu", "600004", "Mylapore", "tea_shop", ["TASTIQ"], 13.0338, 80.2684),
    ("Lemuria Lounge", "Vikram J", "9884001016", "Anna Nagar", "Chennai", "Chennai", "Tamil Nadu", "600040", "Anna Nagar", "cafe", ["LEMURIA"], 13.0850, 80.2101),
    ("Sweet Oven Bakery", "Divya R", "9884001017", "Ambattur", "Chennai", "Chennai", "Tamil Nadu", "600053", "Ambattur", "bakery", ["TASTIQ"], 13.1143, 80.1548),
    ("Heritage Kitchen", "Mohan P", "9884001018", "Guindy", "Chennai", "Chennai", "Tamil Nadu", "600032", "Guindy", "restaurant", ["TASTIQ", "LEMURIA"], 13.0067, 80.2206),
    ("City Stay Hotel", "Ravi D", "9884001019", "Egmore", "Chennai", "Chennai", "Tamil Nadu", "600008", "Egmore", "hotel", ["LEMURIA"], 13.0732, 80.2609),
    ("Corner Provision Store", "Uma K", "9884001020", "Saidapet", "Chennai", "Chennai", "Tamil Nadu", "600015", "Saidapet", "general_store", ["TASTIQ"], 13.0213, 80.2231),
]


def seed_auth_data(db: Session) -> None:
    permission_map: dict[str, Permission] = {}

    for code, name, description in PERMISSIONS:
        existing = db.query(Permission).filter(Permission.code == code).first()
        if existing:
            permission_map[code] = existing
            continue
        permission = Permission(id=uuid.uuid4(), code=code, name=name, description=description)
        db.add(permission)
        permission_map[code] = permission

    db.flush()

    role_map: dict[str, Role] = {}

    for code, name, description, perm_defs in ROLES:
        role = db.query(Role).filter(Role.code == code).first()
        if not role:
            role = Role(id=uuid.uuid4(), code=code, name=name, description=description)
            db.add(role)
            db.flush()
        else:
            role.name = name
            role.description = description

        role_map[code] = role

        for perm_code, _, _ in perm_defs:
            permission_id = permission_map[perm_code].id
            exists = (
                db.query(RolePermission)
                .filter(RolePermission.role_id == role.id, RolePermission.permission_id == permission_id)
                .first()
            )
            if not exists:
                db.add(
                    RolePermission(
                        id=uuid.uuid4(),
                        role_id=role.id,
                        permission_id=permission_id,
                    )
                )

    db.flush()

    for user_data in FOUNDER_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            continue

        user = User(
            id=uuid.uuid4(),
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            phone=user_data["phone"],
            is_active=True,
            last_login_at=None,
        )
        db.add(user)
        db.flush()

        db.add(
            UserRole(
                id=uuid.uuid4(),
                user_id=user.id,
                role_id=role_map[user_data["role_code"]].id,
            )
        )

    db.flush()
    distributor_id = None
    founder = db.query(User).filter(User.email == "faaiq@aalamgroups.com").first()
    founder_id = founder.id if founder else None

    for index, outlet_data in enumerate(SAMPLE_OUTLETS, start=1):
        existing = db.query(Outlet).filter(Outlet.phone_number == outlet_data[2]).first()
        if existing:
            continue
        outlet_id = f"OUT{index:06d}"
        (
            shop_name,
            owner_name,
            phone,
            area,
            city,
            district,
            state,
            pincode,
            territory,
            business_type,
            brands,
            latitude,
            longitude,
        ) = outlet_data
        outlet = Outlet(
            id=uuid.uuid4(),
            outlet_id=outlet_id,
            shop_name=shop_name,
            owner_name=owner_name,
            phone_number=phone,
            whatsapp_number=phone,
            email=None,
            gst_number=None,
            address=f"{area} main road, {city}",
            area=area,
            city=city,
            district=district,
            state=state,
            pincode=pincode,
            territory=territory,
            latitude=latitude,
            longitude=longitude,
            google_maps_url=f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}",
            business_type=business_type,
            brands=brands,
            assigned_distributor_id=distributor_id,
            status="active",
            notes="Seed outlet for field sales and distributor workflows.",
            qr_code_value=f"/outlets/{outlet_id}",
            created_by=founder_id,
            updated_by=founder_id,
        )
        outlet.contacts.append(
            OutletContact(
                id=uuid.uuid4(),
                name=owner_name,
                role="Owner",
                phone=phone,
                whatsapp=phone,
                email=None,
                created_by=founder_id,
                updated_by=founder_id,
            )
        )
        db.add(outlet)

    db.commit()
