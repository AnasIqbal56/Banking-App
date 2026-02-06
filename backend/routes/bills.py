from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId

from database import accounts_collection, transactions_collection, bills_collection
from models import BillCreate, BillResponse, BillPayment, BillStatus, TransactionType
from auth import get_current_user

router = APIRouter(prefix="/api/bills", tags=["Bills"])


@router.post("/", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(bill: BillCreate, current_user: dict = Depends(get_current_user)):
    """Create a new bill"""
    bill_doc = {
        "user_id": current_user["id"],
        "bill_type": bill.bill_type.value,
        "provider_name": bill.provider_name,
        "amount": bill.amount,
        "due_date": bill.due_date,
        "account_number": bill.account_number,
        "status": BillStatus.PENDING.value,
        "paid_at": None,
        "created_at": datetime.utcnow()
    }
    
    result = await bills_collection.insert_one(bill_doc)
    
    return BillResponse(
        id=str(result.inserted_id),
        user_id=current_user["id"],
        bill_type=bill.bill_type,
        provider_name=bill.provider_name,
        amount=bill.amount,
        due_date=bill.due_date,
        account_number=bill.account_number,
        status=BillStatus.PENDING,
        paid_at=None,
        created_at=bill_doc["created_at"]
    )


@router.get("/", response_model=list[BillResponse])
async def get_bills(current_user: dict = Depends(get_current_user)):
    """Get all bills for current user"""
    bills = []
    cursor = bills_collection.find({"user_id": current_user["id"]}).sort("due_date", 1)
    
    async for bill in cursor:
        # Check if bill is overdue
        status = bill["status"]
        if status == BillStatus.PENDING.value and bill["due_date"] < datetime.utcnow():
            status = BillStatus.OVERDUE.value
            await bills_collection.update_one(
                {"_id": bill["_id"]},
                {"$set": {"status": status}}
            )
        
        bills.append(BillResponse(
            id=str(bill["_id"]),
            user_id=bill["user_id"],
            bill_type=bill["bill_type"],
            provider_name=bill["provider_name"],
            amount=bill["amount"],
            due_date=bill["due_date"],
            account_number=bill["account_number"],
            status=status,
            paid_at=bill.get("paid_at"),
            created_at=bill["created_at"]
        ))
    
    return bills


@router.post("/pay", response_model=BillResponse)
async def pay_bill(payment: BillPayment, current_user: dict = Depends(get_current_user)):
    """Pay a bill from an account"""
    # Get the bill
    bill = await bills_collection.find_one({
        "_id": ObjectId(payment.bill_id),
        "user_id": current_user["id"]
    })
    
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    if bill["status"] == BillStatus.PAID.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bill already paid"
        )
    
    # Get the account
    account = await accounts_collection.find_one({
        "_id": ObjectId(payment.from_account_id),
        "user_id": current_user["id"]
    })
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if account["balance"] < bill["amount"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds"
        )
    
    # Deduct from account
    new_balance = account["balance"] - bill["amount"]
    await accounts_collection.update_one(
        {"_id": account["_id"]},
        {"$set": {"balance": new_balance}}
    )
    
    # Create transaction record
    transaction_doc = {
        "account_id": payment.from_account_id,
        "amount": bill["amount"],
        "transaction_type": TransactionType.BILL_PAYMENT.value,
        "description": f"Bill payment - {bill['provider_name']} ({bill['bill_type']})",
        "balance_after": new_balance,
        "recipient_account": bill["account_number"],
        "created_at": datetime.utcnow()
    }
    await transactions_collection.insert_one(transaction_doc)
    
    # Update bill status
    paid_at = datetime.utcnow()
    await bills_collection.update_one(
        {"_id": bill["_id"]},
        {"$set": {"status": BillStatus.PAID.value, "paid_at": paid_at}}
    )
    
    return BillResponse(
        id=str(bill["_id"]),
        user_id=bill["user_id"],
        bill_type=bill["bill_type"],
        provider_name=bill["provider_name"],
        amount=bill["amount"],
        due_date=bill["due_date"],
        account_number=bill["account_number"],
        status=BillStatus.PAID,
        paid_at=paid_at,
        created_at=bill["created_at"]
    )


@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill(bill_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a bill"""
    result = await bills_collection.delete_one({
        "_id": ObjectId(bill_id),
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
