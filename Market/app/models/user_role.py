from datetime import datetime
from uuid import UUID
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from db.postgres import Base

class UserRole(Base):
    __tablename__ = 'user_role'
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )
    
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    role_id: Mapped[UUID] = mapped_column(
        ForeignKey('roles.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    def __init__(self, user_id: UUID, role_id: UUID):
        self.user_id = user_id
        self.role_id = role_id
    
    def __repr__(self):
        return f'<UserRole(user_id={self.user_id}, role_id={self.role_id})>'