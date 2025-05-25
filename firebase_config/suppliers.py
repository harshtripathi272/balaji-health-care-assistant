from firebase_config.config import db
from google.cloud import firestore

def add_supplier(supplier_data):
    doc_ref = db.collection("suppliers").add(supplier_data)
    return doc_ref[1].id

def get_supplier_by_name(name):
    docs = db.collection("suppliers").where("name", "==", name).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_supplier_by_id(supplier_id):
    doc = db.collection("suppliers").document(supplier_id).get()
    return doc.to_dict() | {"id": doc.id} if doc.exists else None

def update_supplier(supplier_id, updated_data):
    db.collection("suppliers").document(supplier_id).update(updated_data)

def delete_supplier(supplier_id):
    db.collection("suppliers").document(supplier_id).delete()

def get_all_suppliers():
    docs = db.collection("suppliers").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def search_suppliers_by_partial_name(partial_name):
    docs = db.collection("suppliers").stream()
    return [
        doc.to_dict() | {"id": doc.id}
        for doc in docs
        if partial_name.lower() in doc.to_dict().get("name", "").lower()
    ]

def update_supplier_due(supplier_id, change_amount: float):
    db.collection("suppliers").document(supplier_id).update({
        "total_due": firestore.Increment(change_amount)
    })

def get_supplier_payments(supplier_id):
    docs = db.collection("payments").where("supplier_id", "==", supplier_id).stream()
    return [doc.to_dict() for doc in docs]

def get_supplier_order_history(supplier_id):
    purchase_orders = db.collection("orders").where("supplier_id", "==", supplier_id).stream()
    return [doc.to_dict() for doc in purchase_orders]
