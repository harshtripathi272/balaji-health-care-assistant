from firebase_config.config import db
from google.cloud import firestore
from google.cloud.firestore import DocumentSnapshot
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# ---------------- Inventory CRUD ----------------

def add_inventory_item(item_data: Dict) -> str:
    item_data["created_at"] = firestore.SERVER_TIMESTAMP
    item_data["updated_at"] = firestore.SERVER_TIMESTAMP
    doc_ref = db.collection("Inventory Items").add(item_data)
    return doc_ref[1].id

def get_inventory_item_by_name(name: str) -> List[Dict]:
    docs = db.collection("Inventory Items").where("name", "==", name).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_inventory_item_by_id(doc_id: str) -> Optional[Dict]:
    doc: DocumentSnapshot = db.collection("Inventory Items").document(doc_id).get()
    return doc.to_dict() | {"id": doc.id} if doc.exists else None

def update_inventory_item(doc_id: str, updated_data: Dict):
    updated_data["updated_at"] = firestore.SERVER_TIMESTAMP
    db.collection("Inventory Items").document(doc_id).update(updated_data)

def delete_inventory_item(doc_id: str):
    db.collection("Inventory Items").document(doc_id).delete()

def get_all_inventory_items() -> List[Dict]:
    docs = db.collection("Inventory Items").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

# ---------------- Filtering & Helpers ----------------

def get_items_by_category(category: str) -> List[Dict]:
    docs = db.collection("Inventory Items").where("category", "==", category).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_low_stock_items(threshold: int = 10) -> List[Dict]:
    docs = db.collection("Inventory Items").where("stock_quantity", "<=", threshold).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def update_stock_quantity(doc_id: str, change: int):
    db.collection("Inventory Items").document(doc_id).update({
        "stock_quantity": firestore.Increment(change),
        "updated_at": firestore.SERVER_TIMESTAMP
    })

def search_inventory_by_partial_name(partial: str) -> List[Dict]:
    docs = db.collection("Inventory Items").stream()
    return [
        doc.to_dict() | {"id": doc.id}
        for doc in docs
        if partial.lower() in doc.to_dict().get("name", "").lower()
    ]

def get_items_expiring_soon(days: int = 30) -> List[Dict]:
    now = datetime.utcnow()
    future = now + timedelta(days=days)
    docs = db.collection("Inventory Items")\
             .where("expiry_date", "<=", future)\
             .stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def resolve_inventory_item_id_by_name(name: str) -> Optional[str]:
    docs = db.collection("Inventory Items").where("name", "==", name).limit(1).stream()
    for doc in docs:
        return doc.id
    return None
