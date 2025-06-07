from firebase_config.config import db
from google.cloud import firestore
from datetime import datetime
from typing import List, Dict
from google.cloud.firestore_v1 import FieldFilter
# ------------------------ Clients ------------------------

def add_client(client_data: dict) -> str:
    client_data["created_at"] = firestore.SERVER_TIMESTAMP
    client_data["updated_at"] = firestore.SERVER_TIMESTAMP
    doc_ref = db.collection("clients").add(client_data)
    return doc_ref[1].id

def get_client_by_name(name: str) -> list:
    docs = db.collection("Clients").where(filter=FieldFilter("name", "==", name)).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_client_by_id(client_id: str):
    doc = db.collection("Clients").document(client_id).get()
    return doc.to_dict() | {"id": doc.id} if doc.exists else None

def update_client(client_id: str, updated_data: dict):
    updated_data["updated_at"] = firestore.SERVER_TIMESTAMP
    db.collection("Clients").document(client_id).update(updated_data)

def delete_client(client_id: str):
    db.collection("Clients").document(client_id).delete()

def get_all_clients() -> list:
    docs = db.collection("Clients").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def search_clients_by_partial_name(partial_name: str) -> list:
    docs = db.collection("Clients").stream()
    return [
        doc.to_dict() | {"id": doc.id}
        for doc in docs
        if partial_name.lower() in doc.to_dict().get("name", "").lower()
    ]

def get_client_order_history(client_id: str) -> list:
    orders = (
        db.collection("Orders")
        .where(filter=FieldFilter("client_id", "==", client_id))
        .where(filter=FieldFilter("type", "==", "sell"))
        .stream()
    )
    return [doc.to_dict() | {"id": doc.id} for doc in orders]


def update_client_due(client_id: str, change_amount: float):
    doc_ref = db.collection("Clients").document(client_id)
    doc_ref.update({
        "total_due": firestore.Increment(change_amount),
        "updated_at": firestore.SERVER_TIMESTAMP
    })

def get_client_payments(client_id: str) -> list:
    docs = db.collection("Payments").where(filter=FieldFilter("client_id", "==", client_id)).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

# ------------------------ Utilities ------------------------

def resolve_client_id_by_name(name: str) :
    docs = db.collection("Clients").where(filter=FieldFilter("name", "==", name)).limit(1).stream()
    for doc in docs:
        return doc.id
    return None
