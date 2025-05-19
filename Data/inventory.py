from firebase_config.config import db

def get_inventory():
    inventory_ref = db.collection("inventory")
    docs = inventory_ref.stream()
    return [doc.to_dict() for doc in docs]

def add_inventory(inventory_data):
    db.collection("inventory").add(inventory_data)

def update_inventory(inventory_id,updated_data):
    db.collection("inventory").document(inventory_id).update(updated_data)

def delete_inventory(inventory_id):
    db.collection("inventory").document(inventory_id).delete()

def get_inventory_by_id(inventory_id):
    doc = db.collection("inventory").document(inventory_id).get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None


