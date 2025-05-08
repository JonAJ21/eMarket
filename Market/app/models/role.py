from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import (
    String, DateTime, Text, UUID as SA_UUID, func
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)

from db.postgres import Base


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[UUID] = mapped_column(
        SA_UUID(), primary_key=True, default=uuid4, index=True
    )
    
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    users: Mapped[list['User']] = relationship(
        secondary='user_role', back_populates='roles'
    )
    
    def __init__(
        self,
        name: str,
        description: str | None = None
    ):
        self.name = name
        self.description = description
        
    def __repr__(self):
        return f'<Role(id={self.id}, name={self.name})>'
    
    def update_role(
        self,
        name: str,
        description: str | None = None
    ):
        if name:
            self.name = name
        if description:
            self.description = description