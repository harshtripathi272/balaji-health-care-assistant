# firebase_utils/inventory.py

from firebase_config.config import db
from google.cloud.firestore import DocumentSnapshot
from typing import List, Dict

def add_inventory_item(item_data: Dict) -> str:
    """Add an inventory item and return the document ID."""
    doc_ref = db.collection("inventory_items").add(item_data)
    return doc_ref[1].id  # Returns document ID

def get_inventory_item_by_name(name: str) -> List[Dict]:
    """Retrieve all inventory items matching a given name."""
    docs = db.collection("inventory_items").where("name", "==", name).stream()
    return [doc.to_dict() | {'id': doc.id} for doc in docs]

def get_inventory_item_by_id(doc_id: str) -> Dict:
    """Retrieve inventory item using its document ID."""
    doc: DocumentSnapshot = db.collection("inventory_items").document(doc_id).get()
    return doc.to_dict() if doc.exists else None

def update_inventory_item(doc_id: str, updated_data: Dict):
    """Update a specific inventory item using its document ID."""
    db.collection("inventory_items").document(doc_id).update(updated_data)

def delete_inventory_item(doc_id: str):
    """Delete an inventory item using its document ID."""
    db.collection("inventory_items").document(doc_id).delete()

def get_all_inventory_items() -> List[Dict]:
    docs = db.collection("inventory_items").stream()
    return [doc.to_dict() | {'id': doc.id} for doc in docs]

def get_items_by_category(category: str) -> List[Dict]:
    docs = db.collection("inventory_items").where("category", "==", category).stream()
    return [doc.to_dict() | {'id': doc.id} for doc in docs]

def get_low_stock_items(threshold: int = 10) -> List[Dict]:
    docs = db.collection("inventory_items").where("stock_quantity", "<=", threshold).stream()
    return [doc.to_dict() | {'id': doc.id} for doc in docs]

def update_stock_quantity(doc_id: str, change: int):
    doc_ref = db.collection("inventory_items").document(doc_id)
    doc_ref.update({"stock_quantity": firestore.Increment(change)})

def search_inventory_by_partial_name(partial: str) -> List[Dict]:
    docs = db.collection("inventory_items").stream()
    return [doc.to_dict() | {'id': doc.id} for doc in docs if partial.lower() in doc.to_dict().get("name", "").lower()]

def get_items_expiring_soon(days=30):
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    future = now + timedelta(days=days)
    docs = db.collection("inventory_items").where("expiry_date", "<=", future).stream()
    return [doc.to_dict() for doc in docs]


