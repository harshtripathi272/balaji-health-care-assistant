from firebase_config.config import db
from google.cloud import firestore  

def add_client(client_data):
    doc_ref = db.collection("clients").add(client_data)
    return doc_ref[1].id

def get_client_by_name(name):
    docs = db.collection("clients").where("name", "==", name).stream()
    return [doc.to_dict() for doc in docs]

def get_client_by_id(client_id):
    doc = db.collection("clients").document(client_id).get()
    return doc.to_dict() if doc.exists else None

def update_client(client_id, updated_data):
    db.collection("clients").document(client_id).update(updated_data)

def delete_client(client_id):
    db.collection("clients").document(client_id).delete()

def get_all_clients():
    docs = db.collection("clients").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def search_clients_by_partial_name(partial_name):
    docs = db.collection("clients").stream()
    return [
        doc.to_dict() | {"id": doc.id}
        for doc in docs
        if partial_name.lower() in doc.to_dict().get("name", "").lower()
    ]
def get_client_order_history(client_id):
    sell_orders = db.collection("sell_orders").where("client_id", "==", client_id).stream()
    return [doc.to_dict() for doc in sell_orders]

def update_client_due(client_id, change_amount: float):
    doc_ref = db.collection("clients").document(client_id)
    doc_ref.update({"total_due": firestore.Increment(change_amount)})

def get_client_payments(client_id):
    docs = db.collection("payments").where("client_id", "==", client_id).stream()
    return [doc.to_dict() for doc in docs]
