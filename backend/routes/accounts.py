from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
import random
import string

from database import accounts_collection
from models import AccountCreate, AccountResponse
from auth import get_current_user

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


def generate_account_number() -> str:
    """Generate a unique 10-digit account number"""
    return ''.join(random.choices(string.digits, k=10))


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account: AccountCreate, current_user: dict = Depends(get_current_user)):
    """Create a new bank account"""
    # Generate unique account number
    while True:
        account_number = generate_account_number()
        existing = await accounts_collection.find_one({"account_number": account_number})
        if not existing:
            break
    
    account_doc = {
        "user_id": current_user["id"],
        "account_number": account_number,
        "account_name": account.account_name,
        "balance": 0.0,
        "created_at": datetime.utcnow()
    }
    
    result = await accounts_collection.insert_one(account_doc)
    
    return AccountResponse(
        id=str(result.inserted_id),
        user_id=current_user["id"],
        account_number=account_number,
        account_name=account.account_name,
        balance=0.0,
        created_at=account_doc["created_at"]
    )


@router.get("/", response_model=list[AccountResponse])
async def get_accounts(current_user: dict = Depends(get_current_user)):
    """Get all accounts for current user"""
    accounts = []
    cursor = accounts_collection.find({"user_id": current_user["id"]})
    
    async for account in cursor:
        accounts.append(AccountResponse(
            id=str(account["_id"]),
            user_id=account["user_id"],
            account_number=account["account_number"],
            account_name=account["account_name"],
            balance=account["balance"],
            created_at=account["created_at"]
        ))
    
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific account"""
    account = await accounts_collection.find_one({
        "_id": ObjectId(account_id),
        "user_id": current_user["id"]
    })
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return AccountResponse(
        id=str(account["_id"]),
        user_id=account["user_id"],
        account_number=account["account_number"],
        account_name=account["account_name"],
        balance=account["balance"],
        created_at=account["created_at"]
    )
