from datetime import datetime
from uuid import UUID
from sqlalchemy import (
    DateTime, String, ForeignKey, Text, func
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)

from db.postgres import Base

class SellerInfo(Base):
    __tablename__ = 'sellers_info'
    
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, index=True
    )
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String(20))
    inn: Mapped[str] = mapped_column(String(12), nullable=False)
    kpp: Mapped[str | None] = mapped_column(String(9))
    payment_account: Mapped[str] = mapped_column(String(20), nullable=False)
    correspondent_account: Mapped[str] = mapped_column(String(20), nullable=False)
    bank: Mapped[str] = mapped_column(String(100), nullable=False)
    bik: Mapped[str] = mapped_column(String(9), nullable=False)
    
    is_verified: Mapped[bool] = mapped_column(default=False)
    verificated_at: Mapped[datetime | None] = mapped_column(DateTime)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
     
    user: Mapped['User'] = relationship(back_populates='seller_info')