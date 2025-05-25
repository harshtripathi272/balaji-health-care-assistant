from firebase_config.config import db
from google.cloud import firestore

# Add a payment received from a client
def add_payment(payment_data: dict) -> str:
    """
    payment_data example:
    {
        "client_id": "abc123",
        "amount": 5000.0,
        "date": firestore.SERVER_TIMESTAMP,  # or a datetime object
        "invoice_id": "inv123",  # optional
        "payment_method": "cash",  # optional
        "notes": "Partial payment"
    }
    """
    doc_ref = db.collection("payments").add(payment_data)
    return doc_ref[1].id

# Get all payments, optionally filter by client_id or date range
def get_payments(client_id=None, start_date=None, end_date=None) -> list:
    payments_ref = db.collection("payments")
    query = payments_ref

    if client_id:
        query = query.where("client_id", "==", client_id)
    if start_date:
        query = query.where("date", ">=", start_date)
    if end_date:
        query = query.where("date", "<=", end_date)

    docs = query.stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

# Add an expense record
def add_expense(expense_data: dict) -> str:
    """
    expense_data example:
    {
        "category": "rent",
        "amount": 15000.0,
        "date": firestore.SERVER_TIMESTAMP,  # or datetime
        "description": "Office rent for May",
        "paid_to": "Landlord"
    }
    """
    doc_ref = db.collection("expenses").add(expense_data)
    return doc_ref[1].id

# Get all expenses, optionally filtered by category or date range
def get_expenses(category=None, start_date=None, end_date=None) -> list:
    expenses_ref = db.collection("expenses")
    query = expenses_ref

    if category:
        query = query.where("category", "==", category)
    if start_date:
        query = query.where("date", ">=", start_date)
    if end_date:
        query = query.where("date", "<=", end_date)

    docs = query.stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

# Update an expense by ID
def update_expense(expense_id: str, updated_data: dict):
    db.collection("expenses").document(expense_id).update(updated_data)

# Delete an expense by ID
def delete_expense(expense_id: str):
    db.collection("expenses").document(expense_id).delete()

# Calculate total payments received (optionally for a client and/or date range)
def get_total_payments(client_id=None, start_date=None, end_date=None) -> float:
    payments = get_payments(client_id, start_date, end_date)
    return sum(p.get("amount", 0) for p in payments)

# Calculate total expenses (optionally by category and/or date range)
def get_total_expenses(category=None, start_date=None, end_date=None) -> float:
    expenses = get_expenses(category, start_date, end_date)
    return sum(e.get("amount", 0) for e in expenses)

# Fetch all dues (clients who owe money)
def get_all_dues():
    clients_ref = db.collection("clients")
    docs = clients_ref.where("total_due", ">", 0).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

# Update client's total due amount (increment or decrement)
def update_client_due(client_id: str, change_amount: float):
    doc_ref = db.collection("clients").document(client_id)
    doc_ref.update({"total_due": firestore.Increment(change_amount)})

# Fetch payments made to suppliers (if you track these)
def get_supplier_payments(supplier_id=None, start_date=None, end_date=None):
    payments_ref = db.collection("supplier_payments")
    query = payments_ref
    if supplier_id:
        query = query.where("supplier_id", "==", supplier_id)
    if start_date:
        query = query.where("date", ">=", start_date)
    if end_date:
        query = query.where("date", "<=", end_date)
    docs = query.stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

# Add supplier payment
def add_supplier_payment(payment_data: dict) -> str:
    doc_ref = db.collection("supplier_payments").add(payment_data)
    return doc_ref[1].id

