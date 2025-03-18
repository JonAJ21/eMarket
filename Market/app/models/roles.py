from uuid import uuid4
from sqlalchemy import UUID, Column, String, Text
from sqlalchemy.orm import relationship

from db.postgres import Base


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(Text)
    users = relationship(
        "User",
        secondary=UserRole.__tablename__,
        back_populates="roles",
        cascade="all, delete",
    )

    def __init__(self, name: str, description: str | None = None) -> None:
        self.name = name
        self.description = description
        
    def __repr__(self) -> str:
        return f"<Role {self.name}>"

    def update_role(self, name: str, description: str | None = None):
        self.name = name
        self.description = description