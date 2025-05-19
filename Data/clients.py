from firebase_config.config import db

def get_clients():
    clients_ref = db.collection("clients")
    docs = clients_ref.stream()
    return [doc.to_dict() for doc in docs]

def add_client(client_data):
    db.collection("clients").add(client_data)

def update_client(client_id, updated_data):
    db.collection("clients").document(client_id).update(updated_data)

def delete_client(client_id):
    db.collection("clients").document(client_id).delete()

def get_client_by_id(client_id):
    doc = db.collection("clients").document(client_id).get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
