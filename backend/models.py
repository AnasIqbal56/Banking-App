from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# Enums
class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    BILL_PAYMENT = "bill_payment"


class BillStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"


class BillType(str, Enum):
    ELECTRICITY = "electricity"
    WATER = "water"
    INTERNET = "internet"
    PHONE = "phone"
    GAS = "gas"
    OTHER = "other"


# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: datetime


class UserInDB(BaseModel):
    email: str
    full_name: str
    hashed_password: str
    created_at: datetime


# Account Models
class AccountCreate(BaseModel):
    account_name: str = Field(..., min_length=2)


class AccountResponse(BaseModel):
    id: str
    user_id: str
    account_number: str
    account_name: str
    balance: float
    created_at: datetime


# Transaction Models
class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    transaction_type: TransactionType
    description: Optional[str] = ""
    recipient_account: Optional[str] = None  # For transfers


class TransactionResponse(BaseModel):
    id: str
    account_id: str
    amount: float
    transaction_type: TransactionType
    description: str
    balance_after: float
    recipient_account: Optional[str] = None
    created_at: datetime


# Bill Models
class BillCreate(BaseModel):
    bill_type: BillType
    provider_name: str
    amount: float = Field(..., gt=0)
    due_date: datetime
    account_number: str  # Provider account number


class BillResponse(BaseModel):
    id: str
    user_id: str
    bill_type: BillType
    provider_name: str
    amount: float
    due_date: datetime
    account_number: str
    status: BillStatus
    paid_at: Optional[datetime] = None
    created_at: datetime


class BillPayment(BaseModel):
    bill_id: str
    from_account_id: str


# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
