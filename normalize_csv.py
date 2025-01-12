import pandas as pd
import numpy as np
from pymongo import MongoClient
from datetime import datetime
from app.config import database
import re

# Load CSV
csv_file = "payment_information.csv"
try:
    df = pd.read_csv(csv_file)
except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
    print(f"Error: {e}")
    exit(1)

# Normalize and Validate Columns
def validate_and_normalize(data):
    # Define valid sets
    valid_statuses = {"completed", "due_now", "overdue", "pending"}
    
    # Validate payment status
    data["payee_payment_status"] = data["payee_payment_status"].str.lower()
    data.loc[~data["payee_payment_status"].isin(valid_statuses), "payee_payment_status"] = np.nan

    # Validate and format dates
    data["payee_added_date_utc"] = pd.to_datetime(data["payee_added_date_utc"], errors="coerce")
    data["payee_due_date"] = pd.to_datetime(data["payee_due_date"], errors="coerce")

    # Mandatory fields validation
    mandatory_columns = [
        "payee_address_line_1", "payee_city", "payee_country",
        "payee_postal_code", "payee_phone_number", "payee_email", "currency", "due_amount"
    ]
    data[mandatory_columns] = data[mandatory_columns].replace("", np.nan)

    # ISO Validation (Country and Currency)
    data["payee_country"] = data["payee_country"].apply(lambda x: x if re.match(r"^[A-Z]{2}$", str(x)) else np.nan)
    data["currency"] = data["currency"].apply(lambda x: x if re.match(r"^[A-Z]{3}$", str(x)) else np.nan)

    # Email Validation
    data["payee_email"] = data["payee_email"].apply(
        lambda x: x if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", str(x)) else np.nan
    )

    # Phone Number Validation (E.164 format)
    data["payee_phone_number"] = data["payee_phone_number"].apply(
        lambda x: f"+{x}" if re.match(r"^[1-9]\d{1,14}$", str(x)) else np.nan
    )

    # Handle Discount and Tax Percent
    data["discount_percent"] = pd.to_numeric(data["discount_percent"], errors="coerce").round(2)
    data["tax_percent"] = pd.to_numeric(data["tax_percent"], errors="coerce").round(2)

    # Due Amount Validation
    data["due_amount"] = pd.to_numeric(data["due_amount"], errors="coerce").round(2)

    # Calculate Total Due
    data["total_due"] = (
        data["due_amount"] * (1 - data["discount_percent"].fillna(0) / 100) * (1 + data["tax_percent"].fillna(0) / 100)
    ).round(2)

    # Log missing data before dropping rows
    missing_data_summary = data[mandatory_columns].isna().sum()
    print("Missing data summary before dropping rows:")
    print(missing_data_summary)

    # Drop rows with missing mandatory data
    data.dropna(subset=mandatory_columns, inplace=True)

    # Convert datetime.date to datetime.datetime
    data["payee_due_date"] = data["payee_due_date"].apply(
        lambda x: datetime.combine(x, datetime.min.time()) if pd.notnull(x) else x
    )

    return data

# Normalize Data
normalized_df = validate_and_normalize(df)

# Save to MongoDB
try:
    collection = database["payments"]
    collection.drop()  # Drop the existing collection if it exists
    records = normalized_df.to_dict("records")
    collection.insert_many(records)
    print("Data normalized and saved to MongoDB.")
except Exception as e:
    print(f"Error: {e}")