from pydantic import BaseModel, field_validator, Field
from typing import Optional, Union
from datetime import datetime, date
from bson import ObjectId
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.utils import convert_object_id_to_str

class PaymentBase(BaseModel):
    payee_first_name: str
    payee_last_name: str
    payee_payment_status: str = Field(default="pending", Literal=True)
    payee_due_date: datetime
    payee_address_line_1: str
    payee_address_line_2: Optional[str]
    payee_city: str
    payee_country: str = Field(max_length=2)  # ISO 3166-1 alpha-2
    payee_province_or_state: Optional[str]
    payee_postal_code: Union[str, int]
    payee_phone_number: Union[str, int]  # E.164 format
    payee_email: str
    currency: str = Field(max_length=3)  # ISO 4217
    discount_percent: Optional[float] = Field(ge=0, le=100)
    tax_percent: Optional[float] = Field(ge=0)
    due_amount: float = Field(gt=0)

    @field_validator('payee_country')
    def validate_country_code(cls, v):
        if len(v) != 2:
            raise ValueError("Invalid country code. Must be 2 characters.")
        return v

    @field_validator('payee_phone_number')
    def validate_phone_number(cls, v):
        # Basic E.164 validation (TODO: can be more refined)
        if isinstance(v, int):
            v = f"+{v}"
        elif not v.startswith('+'):
            raise ValueError("Invalid phone number. Must start with '+' for E.164 format.")
        return v

    @field_validator('discount_percent', 'tax_percent')
    def validate_decimal_places(cls, v):
        if v is not None and round(v, 2) != v:
            raise ValueError("Value must have at most 2 decimal places.")
        return v

class Payment(PaymentBase):
    id: Optional[str] = Field(default=None)
    payee_payment_status: str = Field(default="pending", pattern=r"^(completed|due_now|overdue|pending)$")
    payee_added_date_utc: datetime
    evidence_file_id: Optional[str] = Field(default=None) 
    total_due: float = Field(gt=0)

    @field_validator('evidence_file_id', mode='before')
    def convert_object_id_to_str(cls, v):
         return convert_object_id_to_str(v)

class PaymentUpdate(BaseModel):
    payee_due_date: Optional[datetime] = Field(None)
    evidence_file_id: Optional[str] = Field(None)
    due_amount: Optional[float] = Field(None, gt=0)
    payee_payment_status: Optional[str] = Field(None, pattern=r"^(completed|due_now|overdue|pending)$")

class NewPayment(PaymentBase):
    payee_payment_status: str = Field(default="pending", Literal=True)

class CreatePaymentResponse(BaseModel):
    id: str

class UploadEvidenceRequest(BaseModel):
    """
    Request model for uploading evidence.
    """
    payment_id: str = Field(..., description="ID of the payment.")
    evidence_file: UploadFile = File(...)

class UploadEvidenceResponse(BaseModel):
    """
    Response model for uploading evidence.
    """
    evidence_file_id: str = Field(..., description="ID of the uploaded evidence file.")
    message: str = Field(..., description="Success message.")

    @field_validator('evidence_file_id', mode='before')
    def convert_object_id_to_str(cls, v):
         return convert_object_id_to_str(v)