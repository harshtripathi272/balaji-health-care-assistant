from firebase_config.config import db
from google.cloud import firestore
from typing import List, Dict


# Add a new supplier
from google.cloud import firestore

def add_supplier(supplier_data):
    supplier_data["created_at"] = firestore.SERVER_TIMESTAMP
    supplier_data["updated_at"] = firestore.SERVER_TIMESTAMP
    # Optional: add `updated_by` if tracking user
    doc_ref = db.collection("Suppliers").add(supplier_data)
    return doc_ref[1].id


# Get supplier by exact name
def get_supplier_by_name(name: str) -> List[Dict]:
    docs = db.collection("Suppliers").where("name", "==", name).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]


# Get supplier by document ID
def get_supplier_by_id(supplier_id: str) -> Dict:
    doc = db.collection("Suppliers").document(supplier_id).get()
    return doc.to_dict() | {"id": doc.id} if doc.exists else None


# Update a supplier
def update_supplier(supplier_id: str, updated_data: Dict):
    updated_data["updated_at"] = firestore.SERVER_TIMESTAMP
    db.collection("Suppliers").document(supplier_id).update(updated_data)


# Delete a supplier
def delete_supplier(supplier_id: str):
    db.collection("Suppliers").document(supplier_id).delete()


# Get all suppliers
def get_all_suppliers() -> List[Dict]:
    docs = db.collection("Suppliers").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]


# Fuzzy search by partial name
def search_suppliers_by_partial_name(partial_name: str) -> List[Dict]:
    docs = db.collection("Suppliers").stream()
    return [
        doc.to_dict() | {"id": doc.id}
        for doc in docs
        if partial_name.lower() in doc.to_dict().get("name", "").lower()
    ]


# Increment or decrement supplier's due amount
def update_supplier_due(supplier_id: str, change_amount: float):
    db.collection("Suppliers").document(supplier_id).update({
        "due_amount": firestore.Increment(change_amount),
        "updated_at": firestore.SERVER_TIMESTAMP
    })


# Get payment records made to a supplier
def get_supplier_payments(supplier_id: str) -> List[Dict]:
    docs = db.collection("P ayments").where("supplier_id", "==", supplier_id).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]


# Get all purchase orders from a supplier
def get_supplier_order_history(supplier_id: str) -> list:
    orders = (
        db.collection("Orders")
        .where("supplier_id", "==", supplier_id)
        .where("type", "==", "purchase")
        .stream()
    )
    return [doc.to_dict() | {"id": doc.id} for doc in orders]


# OPTIONAL: Add supply history for a specific item from a supplier
def add_supply_record(supplier_id: str, item_id: str, supply_record: Dict):
    doc_ref = db.collection("Suppliers").document(supplier_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise ValueError("Supplier not found")

    supplier = doc.to_dict()
    items = supplier.get("supplied_items", [])

    found = False
    for item in items:
        if item["item_id"] == item_id:
            item["supply_history"].append(supply_record)
            found = True
            break

    if not found:
        items.append({
            "item_id": item_id,
            "supply_history": [supply_record]
        })

    doc_ref.update({
        "supplied_items": items,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
