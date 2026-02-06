from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from typing import Optional

from database import accounts_collection, transactions_collection
from models import TransactionCreate, TransactionResponse, TransactionType
from auth import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("/{account_id}", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    account_id: str,
    transaction: TransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new transaction (deposit, withdrawal, or transfer)"""
    # Get the source account
    account = await accounts_collection.find_one({
        "_id": ObjectId(account_id),
        "user_id": current_user["id"]
    })
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    new_balance = account["balance"]
    
    # Handle different transaction types
    if transaction.transaction_type == TransactionType.DEPOSIT:
        new_balance += transaction.amount
    
    elif transaction.transaction_type == TransactionType.WITHDRAWAL:
        if account["balance"] < transaction.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
        new_balance -= transaction.amount
    
    elif transaction.transaction_type == TransactionType.TRANSFER:
        if not transaction.recipient_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recipient account number required for transfers"
            )
        
        if account["balance"] < transaction.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
        
        # Find recipient account
        recipient = await accounts_collection.find_one({
            "account_number": transaction.recipient_account
        })
        
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient account not found"
            )
        
        if recipient["account_number"] == account["account_number"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer to the same account"
            )
        
        # Update recipient balance
        await accounts_collection.update_one(
            {"_id": recipient["_id"]},
            {"$inc": {"balance": transaction.amount}}
        )
        
        # Create transaction record for recipient
        recipient_transaction = {
            "account_id": str(recipient["_id"]),
            "amount": transaction.amount,
            "transaction_type": TransactionType.DEPOSIT.value,
            "description": f"Transfer from {account['account_number']}",
            "balance_after": recipient["balance"] + transaction.amount,
            "recipient_account": None,
            "created_at": datetime.utcnow()
        }
        await transactions_collection.insert_one(recipient_transaction)
        
        new_balance -= transaction.amount
    
    # Update source account balance
    await accounts_collection.update_one(
        {"_id": ObjectId(account_id)},
        {"$set": {"balance": new_balance}}
    )
    
    # Create transaction record
    transaction_doc = {
        "account_id": account_id,
        "amount": transaction.amount,
        "transaction_type": transaction.transaction_type.value,
        "description": transaction.description or f"{transaction.transaction_type.value.title()}",
        "balance_after": new_balance,
        "recipient_account": transaction.recipient_account,
        "created_at": datetime.utcnow()
    }
    
    result = await transactions_collection.insert_one(transaction_doc)
    
    return TransactionResponse(
        id=str(result.inserted_id),
        account_id=account_id,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        description=transaction_doc["description"],
        balance_after=new_balance,
        recipient_account=transaction.recipient_account,
        created_at=transaction_doc["created_at"]
    )


@router.get("/{account_id}", response_model=list[TransactionResponse])
async def get_transactions(
    account_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get all transactions for an account"""
    # Verify account ownership
    account = await accounts_collection.find_one({
        "_id": ObjectId(account_id),
        "user_id": current_user["id"]
    })
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    transactions = []
    cursor = transactions_collection.find(
        {"account_id": account_id}
    ).sort("created_at", -1).limit(limit)
    
    async for transaction in cursor:
        transactions.append(TransactionResponse(
            id=str(transaction["_id"]),
            account_id=transaction["account_id"],
            amount=transaction["amount"],
            transaction_type=transaction["transaction_type"],
            description=transaction["description"],
            balance_after=transaction["balance_after"],
            recipient_account=transaction.get("recipient_account"),
            created_at=transaction["created_at"]
        ))
    
    return transactions
