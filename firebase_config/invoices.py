from firebase_config.config import db

# Add a new invoice and return its document ID
def add_invoice(invoice_data):
    doc_ref = db.collection("invoices").add(invoice_data)
    return doc_ref[1].id

# Get invoice(s) by exact invoice number
def get_invoice_by_number(invoice_number):
    docs = db.collection("invoices").where("invoice_number", "==", invoice_number).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

# Get invoice by document ID
def get_invoice_by_id(invoice_id):
    doc = db.collection("invoices").document(invoice_id).get()
    return doc.to_dict() | {"id": doc.id} if doc.exists else None

# Get all invoices
def get_all_invoices():
    docs = db.collection("invoices").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

# Update invoice data by document ID
def update_invoice(invoice_id, updated_data):
    db.collection("invoices").document(invoice_id).update(updated_data)

# Delete invoice by document ID
def delete_invoice(invoice_id):
    db.collection("invoices").document(invoice_id).delete()
