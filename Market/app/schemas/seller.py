from uuid import UUID
from pydantic import BaseModel


class SellerCreateDTO(BaseModel):
    name: str
    address: str
    postal_code: str
    inn: str
    kpp: str
    payment_account: str
    correspondent_account: str
    bank: str
    bik: str