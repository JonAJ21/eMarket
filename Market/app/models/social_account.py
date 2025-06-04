from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import (
    String, DateTime, ForeignKey, Enum,
    UUID as SA_UUID, UniqueConstraint, func
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship
)

from schemas.social import SocialProvider
from db.postgres import Base

class SocialAccount(Base):
    __tablename__ = 'social_accounts'
    __table_args__ = (
        UniqueConstraint('user_id', 'social_name', name='uq_user_social'),
    )
    
    id: Mapped[UUID] = mapped_column(
        SA_UUID(), primary_key=True, default=uuid4, index=True
    )
    
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    
    social_id: Mapped[str] = mapped_column(String(255), nullable=False)
    social_name: Mapped[SocialProvider] = mapped_column(
        Enum(SocialProvider, name='social_provider_enum'),
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    
    user: Mapped['User'] = relationship(back_populates='social_accounts')
    
    def __init__(self, user_id: UUID, social_id: UUID, social_name: SocialProvider):
        self.user_id = user_id
        self.social_id = social_id
        self.social_name = social_name
        
    def __repr__(self):
        return f'<SocialAccount(id={self.id}, user_id={self.user_id}, social_name={self.social_name})>'