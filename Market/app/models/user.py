from datetime import datetime
from uuid import UUID, uuid4
from bcrypt import checkpw, gensalt, hashpw
from pydantic import EmailStr
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
    email: Mapped[EmailStr | None] = mapped_column(String(100), unique=True)
    
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
    
    def __init__(
        self,
        login: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        fathers_name: str | None = None,   
        phone: str | None = None,  
        email: EmailStr | None = None,
        
    ) -> None:
        self.id = uuid4()
        self.login = login
        self.password = hashpw(password.encode(), gensalt()).decode()
        self.first_name = first_name,
        self.last_name = last_name,
        self.fathers_name = fathers_name,
        self.phone = phone
        self.email = email
        self.roles = []
        self.social_accounts = []
        self.history = []
        self.seller_info = []
        
    def __repr__(self) -> str:
        return f'<User(id={self.id}, login={self.login})>'
    
    def check_password(self, password: str) -> bool:
        return checkpw(password.encode(), self.password.encode())
    
    def change_password(self, old_password: str, new_password: str) -> None:
        if not self.check_password(old_password):
            raise ValueError('Old password is incorrect')
        self.password = hashpw(new_password.encode(), gensalt()).decode()
        self.updated_at = datetime.now()
    
    def update_personal(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        fathers_name: str | None = None,
        phone: str | None = None,
        email: EmailStr | None = None,
    ) -> None:
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if fathers_name is not None:
            self.fathers_name = fathers_name
        if phone is not None:
            self.phone = phone
        if email is not None:
            self.email = email
        self.updated_at = datetime.now()
    
    def change_active_status(self, is_active: bool) -> None:
        self.is_active = is_active
        self.updated_at = datetime.now()
      
    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)
    
    def assign_role(self, role: 'Role') -> None:
        if not self.has_role(role.name):
            self.roles.append(role)
            
    def remove_role(self, role: 'Role') -> None:
        if self.has_role(role.name):
            self.roles.remove(role)
            
    def add_user_session(self, session: 'UserHistory') -> None:
        self.history.append(session)
            
    def has_social_account(self, social_account: SocialAccount) -> bool:
        for account in self.social_accounts:
            if (account.social_id == social_account.social_id and 
                account.social_name == social_account.social_name):
                return True
        return False
    
    def add_social_account(self, social_account: SocialAccount) -> None:
        if not self.has_social_account(social_account):
            self.social_accounts.append(social_account)
            
    def remove_social_account(self, social_account: SocialAccount) -> None:
        if self.has_social_account(social_account):
            self.social_accounts.remove(social_account)
    
    def has_seller_info(self) -> bool:
        return self.seller_info is not None
    
    def add_seller_info(self, seller_info: 'SellerInfo') -> None:
        if not self.has_seller_info():
            self.seller_info = seller_info
        else:
            raise ValueError('Seller info already exists for this user')

    def remove_seller_info(self) -> None:
        if self.has_seller_info():
            self.seller_info = None    
    
    
    