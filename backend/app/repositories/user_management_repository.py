import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models import Role, User, UserRole


class UserManagementRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None,
        role_code: str | None,
        is_active: bool | None,
    ) -> tuple[list[User], int]:
        query = self.db.query(User).options(
            joinedload(User.user_roles).joinedload(UserRole.role)
        )

        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(pattern),
                    User.email.ilike(pattern),
                    User.employee_id.ilike(pattern),
                    User.distributor_code.ilike(pattern),
                )
            )
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if role_code:
            query = query.join(UserRole).join(Role).filter(Role.code == role_code)

        total = query.distinct().count()
        rows = (
            query.distinct()
            .order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def get(self, user_id: uuid.UUID) -> User | None:
        return (
            self.db.query(User)
            .options(joinedload(User.user_roles).joinedload(UserRole.role))
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_by_employee_id(self, employee_id: str) -> User | None:
        return self.db.query(User).filter(User.employee_id == employee_id).first()

    def get_by_distributor_code(self, code: str) -> User | None:
        return self.db.query(User).filter(User.distributor_code == code).first()

    def get_role(self, code: str) -> Role | None:
        return self.db.query(Role).filter(Role.code == code).first()

    def count_active_founders(self, exclude_user_id: uuid.UUID | None = None) -> int:
        query = (
            self.db.query(User)
            .join(UserRole)
            .join(Role)
            .filter(Role.code.in_(["founder", "super_admin"]), User.is_active.is_(True))
        )
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.distinct().count()

    def create(self, user: User, role: Role) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.add(UserRole(id=uuid.uuid4(), user_id=user.id, role_id=role.id))
        self.db.commit()
        self.db.refresh(user)
        return user

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_role(self, user: User, role: Role) -> None:
        for existing in list(user.user_roles):
            self.db.delete(existing)
        self.db.flush()
        self.db.add(UserRole(id=uuid.uuid4(), user_id=user.id, role_id=role.id))
        self.db.commit()
        self.db.refresh(user)

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

    def outlet_assignment_count(self, user_id: uuid.UUID) -> int:
        from app.models import Outlet

        return self.db.query(Outlet).filter(Outlet.assigned_distributor_id == user_id).count()
