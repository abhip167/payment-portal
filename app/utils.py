from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional


def get_utc_timestamp() -> int:
    utc_now = datetime.now(timezone.utc)
    return int(utc_now.timestamp())

def convert_object_id_to_str(v):
    if isinstance(v, ObjectId):
        return str(v)
    return v

def calculate_total_due(due_amount: float, discount_percent: Optional[float], tax_percent: Optional[float]) -> float:
    discount_amount = (due_amount * discount_percent / 100) if discount_percent else 0
    tax_amount = (due_amount * tax_percent / 100) if tax_percent else 0
    total_due = due_amount - discount_amount + tax_amount
    return round(total_due, 2)

