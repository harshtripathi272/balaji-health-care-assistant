from firebase_config.config import db

def add_invoice(invoice_data):
    db.collection("invoices").add(invoice_data)

def get_invoice_by_number(invoice_number):
    docs = db.collection("invoices").where("invoice_number", "==", invoice_number).stream()
    return [doc.to_dict() for doc in docs]

def get_all_invoices():
    docs = db.collection("invoices").stream()
    return [doc.to_dict() for doc in docs]

def update_invoice(invoice_id, updated_data):
    db.collection("invoices").document(invoice_id).update(updated_data)

def delete_invoice(invoice_id):
    db.collection("invoices").document(invoice_id).delete()
