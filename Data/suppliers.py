from firebase_config.config import db

def get_suppliers():
    suppliers_ref = db.collection("suppliers")
    docs = suppliers_ref.stream()
    return [doc.to_dict() for doc in docs]

def add_supplier(supplier_data):
    db.collection("suppliers").add(supplier_data)

def update_supplier(supplier_id, updated_data):
    db.collection("suppliers").document(supplier_id).update(updated_data)

def delete_supplier(supplier_id):
    db.collection("suppliers").document(supplier_id).delete()

def get_supplier_by_id(supplier_id):
    doc = db.collection("suppliers").document(supplier_id).get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
