import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models import Outlet, OutletContact, OutletPhoto, OutletVisit
from app.repositories.outlet_repository import OutletRepository
from app.schemas.auth import UserRead
from app.schemas.common import PaginatedResponse
from app.schemas.outlet import (
    OutletContactRead,
    OutletCreate,
    OutletPhotoRead,
    OutletRead,
    OutletSummary,
    OutletUpdate,
    OutletVisitCreate,
    OutletVisitRead,
)

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "outlets"
ALLOWED_PHOTO_TYPES = {"shop_front", "inside_shop", "name_board"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


class OutletService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OutletRepository(db)

    def _user_uuid(self, user: UserRead) -> uuid.UUID:
        return uuid.UUID(user.id)

    def _is_founder(self, user: UserRead) -> bool:
        return "founder" in user.roles or "super_admin" in user.roles

    def _is_distributor(self, user: UserRead) -> bool:
        return "distributor" in user.roles

    def _ensure_can_view(self, outlet: Outlet, user: UserRead) -> None:
        if self._is_founder(user):
            return
        if self._is_distributor(user) and str(outlet.assigned_distributor_id) == user.id:
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Outlet is not assigned to this user")

    def _ensure_can_edit(self, outlet: Outlet, user: UserRead) -> None:
        if self._is_founder(user):
            return
        if self._is_distributor(user) and str(outlet.assigned_distributor_id) == user.id:
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit this outlet")

    def _serialize_user(self, user) -> UserRead | None:
        if not user:
            return None
        return UserRead(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            roles=user.role_codes,
            primary_role=user.primary_role,
            is_active=user.is_active,
        )

    def _qr_code_url(self, qr_value: str) -> str:
        encoded = quote(qr_value, safe="")
        return f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={encoded}"

    def _serialize(self, outlet: Outlet) -> OutletRead:
        return OutletRead(
            id=str(outlet.id),
            outlet_id=outlet.outlet_id,
            shop_name=outlet.shop_name,
            owner_name=outlet.owner_name,
            phone_number=outlet.phone_number,
            whatsapp_number=outlet.whatsapp_number,
            email=outlet.email,
            gst_number=outlet.gst_number,
            address=outlet.address,
            area=outlet.area,
            city=outlet.city,
            district=outlet.district,
            state=outlet.state,
            pincode=outlet.pincode,
            territory=outlet.territory,
            latitude=outlet.latitude,
            longitude=outlet.longitude,
            google_maps_url=outlet.google_maps_url,
            business_type=outlet.business_type,
            brands=outlet.brands,
            assigned_distributor_id=str(outlet.assigned_distributor_id) if outlet.assigned_distributor_id else None,
            assigned_distributor=self._serialize_user(outlet.assigned_distributor),
            status=outlet.status,
            notes=outlet.notes,
            qr_code_value=outlet.qr_code_value,
            qr_code_url=self._qr_code_url(outlet.qr_code_value),
            visits=[
                OutletVisitRead(
                    id=str(visit.id),
                    visit_date=visit.visit_date,
                    distributor_id=str(visit.distributor_id) if visit.distributor_id else None,
                    latitude=visit.latitude,
                    longitude=visit.longitude,
                    photo_url=visit.photo_url,
                    notes=visit.notes,
                    next_follow_up_date=visit.next_follow_up_date,
                    created_at=visit.created_at,
                )
                for visit in sorted(outlet.visits, key=lambda visit: visit.visit_date, reverse=True)
            ],
            photos=[
                OutletPhotoRead(
                    id=str(photo.id),
                    photo_type=photo.photo_type,
                    file_name=photo.file_name,
                    file_url=photo.file_url,
                    content_type=photo.content_type,
                    size_bytes=photo.size_bytes,
                    created_at=photo.created_at,
                )
                for photo in sorted(outlet.photos, key=lambda photo: photo.created_at, reverse=True)
            ],
            contacts=[
                OutletContactRead(
                    id=str(contact.id),
                    name=contact.name,
                    role=contact.role,
                    phone=contact.phone,
                    whatsapp=contact.whatsapp,
                    email=contact.email,
                )
                for contact in outlet.contacts
            ],
            created_at=outlet.created_at,
            updated_at=outlet.updated_at,
        )

    def list_outlets(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        status: str | None,
        territory: str | None,
        business_type: str | None,
        current_user: UserRead,
    ) -> PaginatedResponse[OutletRead]:
        assigned_id = None if self._is_founder(current_user) else self._user_uuid(current_user)
        rows, total = self.repo.list(
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            territory=territory,
            business_type=business_type,
            assigned_distributor_id=assigned_id,
        )
        total_pages = (total + page_size - 1) // page_size if total else 0
        return PaginatedResponse(
            success=True,
            message="Outlets retrieved",
            data=[self._serialize(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_outlet(self, outlet_id: uuid.UUID, current_user: UserRead) -> OutletRead:
        outlet = self.repo.get(outlet_id)
        if not outlet:
            raise HTTPException(status_code=404, detail="Outlet not found")
        self._ensure_can_view(outlet, current_user)
        return self._serialize(outlet)

    def create_outlet(self, payload: OutletCreate, current_user: UserRead) -> OutletRead:
        if not (self._is_founder(current_user) or self._is_distributor(current_user)):
            raise HTTPException(status_code=403, detail="Cannot create outlets")

        user_id = self._user_uuid(current_user)
        assigned_distributor_id = (
            uuid.UUID(payload.assigned_distributor_id)
            if payload.assigned_distributor_id and self._is_founder(current_user)
            else user_id if self._is_distributor(current_user) else None
        )
        public_id = self.repo.next_outlet_id()
        outlet = Outlet(
            id=uuid.uuid4(),
            outlet_id=public_id,
            shop_name=payload.shop_name,
            owner_name=payload.owner_name,
            phone_number=payload.phone_number,
            whatsapp_number=payload.whatsapp_number,
            email=str(payload.email) if payload.email else None,
            gst_number=payload.gst_number,
            address=payload.address,
            area=payload.area,
            city=payload.city,
            district=payload.district,
            state=payload.state,
            pincode=payload.pincode,
            territory=payload.territory,
            latitude=payload.latitude,
            longitude=payload.longitude,
            google_maps_url=payload.google_maps_url,
            business_type=payload.business_type,
            brands=list(payload.brands),
            assigned_distributor_id=assigned_distributor_id,
            status=payload.status,
            notes=payload.notes,
            qr_code_value=f"/outlets/{public_id}",
            created_by=user_id,
            updated_by=user_id,
        )
        for contact in payload.contacts:
            outlet.contacts.append(
                OutletContact(
                    id=uuid.uuid4(),
                    name=contact.name,
                    role=contact.role,
                    phone=contact.phone,
                    whatsapp=contact.whatsapp,
                    email=str(contact.email) if contact.email else None,
                    created_by=user_id,
                    updated_by=user_id,
                )
            )
        self.repo.create(outlet)
        return self.get_outlet(outlet.id, current_user)

    def update_outlet(self, outlet_id: uuid.UUID, payload: OutletUpdate, current_user: UserRead) -> OutletRead:
        outlet = self.repo.get(outlet_id)
        if not outlet:
            raise HTTPException(status_code=404, detail="Outlet not found")
        self._ensure_can_edit(outlet, current_user)

        update_data = payload.model_dump(exclude_unset=True)
        if "assigned_distributor_id" in update_data and not self._is_founder(current_user):
            update_data.pop("assigned_distributor_id")
        for key, value in update_data.items():
            if key == "email" and value is not None:
                value = str(value)
            if key == "assigned_distributor_id" and value:
                value = uuid.UUID(value)
            setattr(outlet, key, value)
        outlet.updated_by = self._user_uuid(current_user)
        self.db.add(outlet)
        self.db.commit()
        return self.get_outlet(outlet.id, current_user)

    def delete_outlet(self, outlet_id: uuid.UUID, current_user: UserRead) -> None:
        if not self._is_founder(current_user):
            raise HTTPException(status_code=403, detail="Distributors cannot delete outlets")
        outlet = self.repo.get(outlet_id)
        if not outlet:
            raise HTTPException(status_code=404, detail="Outlet not found")
        self.repo.soft_delete(outlet, self._user_uuid(current_user))

    def add_visit(self, outlet_id: uuid.UUID, payload: OutletVisitCreate, current_user: UserRead) -> OutletRead:
        outlet = self.repo.get(outlet_id)
        if not outlet:
            raise HTTPException(status_code=404, detail="Outlet not found")
        self._ensure_can_edit(outlet, current_user)
        user_id = self._user_uuid(current_user)
        visit = OutletVisit(
            id=uuid.uuid4(),
            outlet_id=outlet.id,
            visit_date=payload.visit_date or datetime.now(timezone.utc),
            distributor_id=user_id if self._is_distributor(current_user) else outlet.assigned_distributor_id,
            latitude=payload.latitude,
            longitude=payload.longitude,
            photo_url=payload.photo_url,
            notes=payload.notes,
            next_follow_up_date=payload.next_follow_up_date,
            created_by=user_id,
            updated_by=user_id,
        )
        self.repo.add_visit(visit)
        return self.get_outlet(outlet.id, current_user)

    def add_photo(self, outlet_id: uuid.UUID, photo_type: str, file: UploadFile, current_user: UserRead) -> OutletRead:
        outlet = self.repo.get(outlet_id)
        if not outlet:
            raise HTTPException(status_code=404, detail="Outlet not found")
        self._ensure_can_edit(outlet, current_user)
        if photo_type not in ALLOWED_PHOTO_TYPES:
            raise HTTPException(status_code=400, detail="Invalid photo type")
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WEBP images are allowed")

        suffix = Path(file.filename or "").suffix.lower() or ".jpg"
        safe_name = f"{photo_type}-{uuid.uuid4()}{suffix}"
        target_dir = UPLOAD_ROOT / outlet.outlet_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / safe_name
        with target.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        photo = OutletPhoto(
            id=uuid.uuid4(),
            outlet_id=outlet.id,
            photo_type=photo_type,
            file_name=safe_name,
            file_url=f"/uploads/outlets/{outlet.outlet_id}/{safe_name}",
            content_type=file.content_type,
            size_bytes=target.stat().st_size,
            created_by=self._user_uuid(current_user),
            updated_by=self._user_uuid(current_user),
        )
        self.repo.add_photo(photo)
        return self.get_outlet(outlet.id, current_user)

    def summary(self, current_user: UserRead) -> OutletSummary:
        assigned_id = None if self._is_founder(current_user) else self._user_uuid(current_user)
        values = self.repo.summary(assigned_id)
        return OutletSummary(**values)
