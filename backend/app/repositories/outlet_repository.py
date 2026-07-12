import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models import Outlet, OutletPhoto, OutletVisit


class OutletRepository:
    def __init__(self, db: Session):
        self.db = db

    def next_outlet_id(self) -> str:
        latest = self.db.query(Outlet).order_by(Outlet.outlet_id.desc()).first()
        if not latest:
            return "OUT000001"
        try:
            number = int(latest.outlet_id.replace("OUT", "")) + 1
        except ValueError:
            number = self.db.query(func.count(Outlet.id)).scalar() + 1
        return f"OUT{number:06d}"

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        status: str | None,
        territory: str | None,
        business_type: str | None,
        assigned_distributor_id: uuid.UUID | None,
    ) -> tuple[list[Outlet], int]:
        query = (
            self.db.query(Outlet)
            .options(
                joinedload(Outlet.assigned_distributor),
                joinedload(Outlet.photos),
                joinedload(Outlet.visits),
                joinedload(Outlet.contacts),
            )
            .filter(Outlet.deleted_at.is_(None))
        )

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Outlet.outlet_id.ilike(pattern),
                    Outlet.shop_name.ilike(pattern),
                    Outlet.owner_name.ilike(pattern),
                    Outlet.phone_number.ilike(pattern),
                    Outlet.area.ilike(pattern),
                )
            )
        if status:
            query = query.filter(Outlet.status == status)
        if territory:
            query = query.filter(Outlet.territory == territory)
        if business_type:
            query = query.filter(Outlet.business_type == business_type)
        if assigned_distributor_id:
            query = query.filter(Outlet.assigned_distributor_id == assigned_distributor_id)

        total = query.count()
        rows = query.order_by(Outlet.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return rows, total

    def get(self, outlet_id: uuid.UUID) -> Outlet | None:
        return (
            self.db.query(Outlet)
            .options(
                joinedload(Outlet.assigned_distributor),
                joinedload(Outlet.photos),
                joinedload(Outlet.visits),
                joinedload(Outlet.contacts),
            )
            .filter(Outlet.id == outlet_id, Outlet.deleted_at.is_(None))
            .first()
        )

    def get_by_public_id(self, outlet_id: str) -> Outlet | None:
        return self.db.query(Outlet).filter(Outlet.outlet_id == outlet_id, Outlet.deleted_at.is_(None)).first()

    def create(self, outlet: Outlet) -> Outlet:
        self.db.add(outlet)
        self.db.commit()
        self.db.refresh(outlet)
        return outlet

    def soft_delete(self, outlet: Outlet, user_id: uuid.UUID) -> None:
        outlet.deleted_at = datetime.now(timezone.utc)
        outlet.updated_by = user_id
        self.db.add(outlet)
        self.db.commit()

    def add_visit(self, visit: OutletVisit) -> OutletVisit:
        self.db.add(visit)
        self.db.commit()
        self.db.refresh(visit)
        return visit

    def add_photo(self, photo: OutletPhoto) -> OutletPhoto:
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return photo

    def summary(self, assigned_distributor_id: uuid.UUID | None = None) -> dict[str, int]:
        outlet_query = self.db.query(Outlet).filter(Outlet.deleted_at.is_(None))
        visit_query = self.db.query(OutletVisit).join(Outlet).filter(Outlet.deleted_at.is_(None))
        if assigned_distributor_id:
            outlet_query = outlet_query.filter(Outlet.assigned_distributor_id == assigned_distributor_id)
            visit_query = visit_query.filter(Outlet.assigned_distributor_id == assigned_distributor_id)

        today = date.today()
        month_start = today.replace(day=1)
        return {
            "total": outlet_query.count(),
            "active": outlet_query.filter(Outlet.status == "active").count(),
            "new_this_month": outlet_query.filter(func.date(Outlet.created_at) >= month_start.isoformat()).count(),
            "visits_today": visit_query.filter(func.date(OutletVisit.visit_date) == today.isoformat()).count(),
        }
