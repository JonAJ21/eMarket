from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import (
    String, Boolean, DateTime, UUID as SA_UUID,  func
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)

from models.seller_info import SellerInfo
from models.user_history import UserHistory
from models.social_account import SocialAccount
from models.role import Role
from db.postgres import Base


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[UUID] = mapped_column(
        SA_UUID(), primary_key=True, default=uuid4, index=True
    )
    
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    fathers_name: Mapped[str | None] = mapped_column(String(50))
    
    phone: Mapped[str | None] = mapped_column(String(11), unique=True)
    email: Mapped[str | None] = mapped_column(String(100), unique=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    roles: Mapped[list['Role']] = relationship(
        secondary='user_role', back_populates='users', cascade='all, delete'
    )
    
    social_accounts: Mapped[list['SocialAccount']] = relationship(
        back_populates='user', cascade='all, delete-orphan', lazy='selectin'
    )
    
    history: Mapped[list['UserHistory']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )
    
    seller_info: Mapped['SellerInfo'] = relationship(
        back_populates='user', uselist=False
    )
    
    
    
    