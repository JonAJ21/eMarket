from uuid import UUID
from pydantic import BaseModel

class SellerInfoBase(BaseModel):
    id: UUID
    seller_id: UUID
    name: str
    address: str
    postal_code: str
    phone: str
    inn: str
    kpp: str
    payment_account: str
    correspondent_account: str
    bank: str
    bik: str
    verified: bool

class SellerInfoCreateDTO(BaseModel):
    name: str
    address: str
    postal_code: str
    phone: str
    inn: str
    kpp: str
    payment_account: str
    correspondent_account: str
    bank: str
    bik: str

class SellerInfoUpdateDTO(BaseModel):
    name: str | None = None
    address: str | None = None
    postal_code: str | None = None
    phone: str | None = None
    inn: str | None = None
    kpp: str | None = None
    payment_account: str | None = None
    correspondent_account: str | None = None
    bank: str | None = None
    bik: str | None = None