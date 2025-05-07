from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Text, Enum,
    UUID as SA_UUID, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schemas.user import UserDeviceType
from db.postgres import Base

class UserHistory(Base):
    __tablename__ = 'user_history'
    
    id: Mapped[UUID] = mapped_column(
        SA_UUID(), primary_key=True, default=uuid4, index=True
    )
    
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    
    user_agent: Mapped[str | None] = mapped_column(Text)
    user_device_type: Mapped[UserDeviceType | None] = mapped_column(
        Enum(UserDeviceType, name='user_device_type_enum')
    )
    
    attemted_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    is_success: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    
    user: Mapped['User'] = relationship(back_populates='user_history')