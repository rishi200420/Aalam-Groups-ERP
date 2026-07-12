import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import User
from app.repositories.user_management_repository import UserManagementRepository
from app.schemas.auth import UserRead
from app.schemas.common import PaginatedResponse
from app.schemas.user_management import (
    PasswordResetRequest,
    UserCreateRequest,
    UserManagementRead,
    UserUpdateRequest,
)


def _require_founder(current_user: UserRead) -> None:
    if "founder" not in current_user.roles and "super_admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Only founders can manage users")


class UserManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserManagementRepository(db)

    def _serialize(self, user: User) -> UserManagementRead:
        return UserManagementRead(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.primary_role or "distributor",
            is_active=user.is_active,
            employee_id=user.employee_id,
            distributor_code=user.distributor_code,
            territory=user.territory,
            brand=user.brand,
            joining_date=user.joining_date,
            profile_image_url=user.profile_image_url,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def list_users(
        self,
        *,
        current_user: UserRead,
        page: int,
        page_size: int,
        search: str | None,
        role: str | None,
        is_active: bool | None,
    ) -> PaginatedResponse[UserManagementRead]:
        _require_founder(current_user)
        rows, total = self.repo.list(page=page, page_size=page_size, search=search, role_code=role, is_active=is_active)
        total_pages = (total + page_size - 1) // page_size if total else 0
        return PaginatedResponse(
            success=True,
            message="Users retrieved",
            data=[self._serialize(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def get_user(self, user_id: uuid.UUID, current_user: UserRead) -> UserManagementRead:
        _require_founder(current_user)
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self._serialize(user)

    def create_user(self, payload: UserCreateRequest, current_user: UserRead) -> UserManagementRead:
        _require_founder(current_user)
        if self.repo.get_by_email(payload.email):
            raise HTTPException(status_code=409, detail="Email already registered")
        if payload.employee_id and self.repo.get_by_employee_id(payload.employee_id):
            raise HTTPException(status_code=409, detail="Employee ID already exists")
        if payload.distributor_code and self.repo.get_by_distributor_code(payload.distributor_code):
            raise HTTPException(status_code=409, detail="Distributor code already exists")
        role = self.repo.get_role(payload.role)
        if not role:
            raise HTTPException(status_code=400, detail="Invalid role")
        if payload.role in ("founder",) and "super_admin" not in current_user.roles and "founder" not in current_user.roles:
            raise HTTPException(status_code=403, detail="Cannot create founder accounts")

        user = User(
            id=uuid.uuid4(),
            email=payload.email.lower(),
            password_hash=get_password_hash(payload.password),
            full_name=payload.full_name,
            phone=payload.phone,
            is_active=True,
            employee_id=payload.employee_id,
            distributor_code=payload.distributor_code,
            territory=payload.territory,
            brand=payload.brand,
            joining_date=payload.joining_date,
            created_by=uuid.UUID(current_user.id),
        )
        self.repo.create(user, role)
        return self._serialize(user)

    def update_user(self, user_id: uuid.UUID, payload: UserUpdateRequest, current_user: UserRead) -> UserManagementRead:
        _require_founder(current_user)
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = payload.model_dump(exclude_unset=True, exclude={"role"})
        if "employee_id" in update_data and update_data["employee_id"]:
            existing = self.repo.get_by_employee_id(update_data["employee_id"])
            if existing and existing.id != user.id:
                raise HTTPException(status_code=409, detail="Employee ID already exists")
        if "distributor_code" in update_data and update_data["distributor_code"]:
            existing = self.repo.get_by_distributor_code(update_data["distributor_code"])
            if existing and existing.id != user.id:
                raise HTTPException(status_code=409, detail="Distributor code already exists")
        if "is_active" in update_data and update_data["is_active"] is False:
            if user.primary_role in ("founder", "super_admin") and self.repo.count_active_founders(exclude_user_id=user.id) == 0:
                raise HTTPException(status_code=409, detail="Cannot deactivate the last active founder")

        for key, value in update_data.items():
            setattr(user, key, value)

        if payload.role and payload.role != user.primary_role:
            role = self.repo.get_role(payload.role)
            if not role:
                raise HTTPException(status_code=400, detail="Invalid role")
            self.repo.set_role(user, role)

        self.repo.save(user)
        return self._serialize(user)

    def reset_password(self, user_id: uuid.UUID, payload: PasswordResetRequest, current_user: UserRead) -> None:
        _require_founder(current_user)
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.password_hash = get_password_hash(payload.new_password)
        self.repo.save(user)

    def deactivate_user(self, user_id: uuid.UUID, current_user: UserRead) -> UserManagementRead:
        return self.update_user(user_id, UserUpdateRequest(is_active=False), current_user)

    def activate_user(self, user_id: uuid.UUID, current_user: UserRead) -> UserManagementRead:
        return self.update_user(user_id, UserUpdateRequest(is_active=True), current_user)

    def delete_user(self, user_id: uuid.UUID, current_user: UserRead) -> None:
        _require_founder(current_user)
        if str(user_id) == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.primary_role in ("founder", "super_admin") and self.repo.count_active_founders(exclude_user_id=user.id) == 0:
            raise HTTPException(status_code=409, detail="Cannot delete the last active founder")
        if self.repo.outlet_assignment_count(user.id) > 0:
            raise HTTPException(status_code=409, detail="Reassign this distributor's outlets before deleting")
        self.repo.delete(user)
