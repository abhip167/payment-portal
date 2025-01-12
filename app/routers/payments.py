from fastapi import APIRouter, HTTPException, Body, status, UploadFile, File
from typing import List, Optional
from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
from ..models.payment import Payment, PaymentUpdate, NewPayment, CreatePaymentResponse, UploadEvidenceResponse
from bson import ObjectId
from app.config import database
from app.utils import get_utc_timestamp, calculate_total_due
from gridfs import GridFS
from fastapi.responses import StreamingResponse

router = APIRouter(
    prefix="/payments", 
    tags=["Payments"] 
)

@router.get("/", response_model=List[Payment])
def get_payments(
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    filter_status: Optional[str] = None
) -> List[Payment]:
    payments_collection = database["payments"]
    query = {}

    if search:
        query["$or"] = [
            {"payee_first_name": {"$regex": search, "$options": "i"}},
            {"payee_last_name": {"$regex": search, "$options": "i"}},
            {"payee_email": {"$regex": search, "$options": "i"}}
        ]

    if filter_status:
        query["payee_payment_status"] = filter_status

    sort_order = ASCENDING if sort_order == "asc" else DESCENDING
    sort_criteria = [(sort_by, sort_order)] if sort_by else None

    skip = (page - 1) * page_size
    cursor = payments_collection.find(query).skip(skip).limit(page_size)
    if sort_criteria:
        cursor = cursor.sort(sort_criteria)

    try:
        payments = []
        for payment in cursor:

            payment["id"] = str(payment["_id"])  # Convert ObjectId to string
            payment = Payment(**payment)

            payment = update_payment_status(payment)

            payment.total_due = calculate_total_due(
                payment.due_amount,
                payment.discount_percent,
                payment.tax_percent
            )

            payments.append(payment)
        return payments
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

@router.put("/{payment_id}", response_model=Payment)
def update_payment(
    payment_id: str,
    payment_update: PaymentUpdate = Body(...)
) -> Payment:
    
    if payment_update.payee_payment_status == "completed" and not payment_update.evidence_file_id:
        raise HTTPException(status_code=400, detail="Evidence file is required for 'completed' status")
    
    payments_collection = database["payments"]
    update_fields = payment_update.model_dump(exclude_unset=True)
    
     # Convert date fields to datetime
    if "payee_due_date" in update_fields:
        update_fields["payee_due_date"] = datetime.combine(update_fields["payee_due_date"], datetime.min.time())

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        result = payments_collection.update_one(
            {"_id": ObjectId(payment_id)},
            {"$set": update_fields}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Payment not found")

        updated_payment = payments_collection.find_one({"_id": ObjectId(payment_id)})
        updated_payment["id"] = str(updated_payment["_id"])  # Convert ObjectId to string
        updated_payment = Payment(**updated_payment)

        updated_payment = update_payment_status(updated_payment)

        updated_payment.total_due = calculate_total_due(
                updated_payment.due_amount,
                updated_payment.discount_percent,
                updated_payment.tax_percent
        )
        
        return updated_payment
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@router.delete("/{payment_id}", status_code=status.HTTP_201_CREATED)
def delete_payment(payment_id: str):
    payments_collection = database["payments"]
    result = payments_collection.delete_one({"_id": ObjectId(payment_id)})

    try:
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
        return {"message": "Payment deleted successfully"}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/", response_model=CreatePaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: NewPayment = Body(...)) -> CreatePaymentResponse:
    payments_collection = database["payments"]
    
    try:
        payment_dict = payment.model_dump(exclude_unset=True)
        
        if "payee_due_date" in payment_dict:
            payment_dict["payee_due_date"] = datetime.combine(payment_dict["payee_due_date"], datetime.min.time())

        payment_dict["payee_added_date_utc"] = get_utc_timestamp()
        payment_dict["total_due"] = calculate_total_due(
            payment_dict["due_amount"],
            payment_dict["discount_percent"],
            payment_dict["tax_percent"]
        )
        
        # Validate the payment_dict before inserting into the database
        validated_payment = Payment(**payment_dict).model_dump()

        result = payments_collection.insert_one(validated_payment)

        return {"id": str(result.inserted_id)}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/{payment_id}/evidence", response_model=UploadEvidenceResponse)
def upload_evidence(payment_id: str, evidence_file: UploadFile = File(...)):
   
    try:
        payments_collection = database["payments"]
        payment = payments_collection.find_one({"_id": ObjectId(payment_id)})

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        fs = GridFS(database) 
        file_id = fs.put(evidence_file.file, filename=evidence_file.filename)

        payment["evidence_file_id"] = str(file_id)
        payments_collection.update_one({"_id": ObjectId(payment_id)}, {"$set": payment})

        return UploadEvidenceResponse(evidence_file_id= file_id,message="Evidence uploaded successfully.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading evidence: {str(e)}") 

@router.get("/{payment_id}/evidence")
def download_evidence(payment_id: str):
  
    try:
        payments_collection = database["payments"]
        payment = payments_collection.find_one({"_id": ObjectId(payment_id)})

        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        if "evidence_file_id" not in payment:
            raise HTTPException(status_code=404, detail="No evidence file found for this payment")

        fs = GridFS(database)
        file_id = payment["evidence_file_id"]
        file_data = fs.get(ObjectId(file_id)) 

          # Stream the file data directly from GridFS
        def generate_stream():
            for chunk in file_data:
                yield chunk

        return StreamingResponse(
            generate_stream(),
            media_type=file_data.content_type,
            headers={"Content-Disposition": f"attachment; filename={file_data.filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading evidence: {str(e)}") 
    


def update_payment_status(payment: Payment) -> Payment:
    today = datetime.today()
    if payment.payee_payment_status == "completed":
       return payment
    
    elif payment.payee_due_date == today:
        payment.payee_payment_status = "due_now"
    elif payment.payee_due_date < today:
        payment.payee_payment_status = "overdue"
    return payment