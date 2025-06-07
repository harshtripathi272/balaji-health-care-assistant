from firebase_config.config import db
from google.cloud import firestore
from typing import List, Dict, Optional
from datetime import datetime, timezone

# ---------------- Order Handling ----------------
from firebase_config.config import db
from google.cloud import firestore
from typing import Dict, List, Optional
from datetime import datetime
from google.cloud.firestore_v1 import FieldFilter

def add_order(order_data: Dict) -> str:
    """
    Expects order_data in this format:
    {
        "client_id": str,
        "supplier_id": Optional[str],
        "order_type": "purchase" | "sales",
        "status": str,
        "items": List[{
            "item_id": str,
            "quantity": int,
            "price": float,
            "discount": float (optional),
            "tax": float (optional),
            "batch_number": str (optional)
        }],
        "total_amount": float,
        "invoice_number": str,
        "remarks": str (optional),
        "updated_by": str
    }
    """

    # Resolve optional fields
    supplier_id = order_data.get("supplier_id")
    remarks = order_data.get("remarks", "")
    status = order_data.get("status", "pending")
    invoice_number = order_data.get("invoice_number")
    updated_by = order_data.get("updated_by", "system")

    # Fetch optional names for easier querying
    client_name = ""
    supplier_name = ""

    if order_data["order_type"] == "sales" and order_data.get("client_id"):
        client_doc = db.collection("Clients").document(order_data["client_id"]).get()
        if client_doc.exists:
            client_name = client_doc.to_dict().get("name", "")

    if order_data["order_type"] == "purchase" and supplier_id:
        supplier_doc = db.collection("Suppliers").document(supplier_id).get()
        if supplier_doc.exists:
            supplier_name = supplier_doc.to_dict().get("name", "")

    # Process each item and update inventory
    processed_items = []
    for item in order_data["items"]:
        item_id = item["item_id"]
        quantity = item["quantity"]
        price = item["price"]
        discount = item.get("discount", 0)
        tax = item.get("tax", 0)
        batch_number = item.get("batch_number", "")

        # Fetch item name and update stock
        item_doc = db.collection("Inventory Items").document(item_id).get()
        if not item_doc.exists:
            print(f"Item {item_id} not found.")
            continue

        item_data = item_doc.to_dict()
        item_name = item_data.get("name", "Unnamed")

        current_stock = item_data.get("stock_quantity", 0)
        new_stock = current_stock + quantity if order_data["order_type"] == "purchase" else current_stock - quantity

        db.collection("Inventory Items").document(item_id).update({
            "stock_quantity": new_stock
        })

        # Append processed item
        processed_items.append({
            "item_id": item_id,
            "item_name": item_name,
            "quantity": quantity,
            "price": price,
            "discount": discount,
            "tax": tax,
            "batch_number": batch_number
        })

    # Compose the order document
    timestamp = firestore.SERVER_TIMESTAMP
    order_doc = {
        "client_id": order_data.get("client_id"),
        "client_name": client_name,
        "supplier_id": supplier_id,
        "supplier_name": supplier_name,
        "order_type": order_data["order_type"],
        "order_date": timestamp,
        "status": status,
        "items": processed_items,
        "total_amount": order_data["total_amount"],
        "invoice_number": invoice_number,
        "remarks": remarks,
        "created_at": timestamp,
        "updated_at": timestamp,
        "updated_by": updated_by
    }

    # Add to Firestore
    order_ref = db.collection("Orders").add(order_doc)
    order_id = order_ref[1].id
    print(f"[✔] Order added with ID: {order_id} and Invoice: {invoice_number}")
    return order_id


def get_order_by_id(order_id: str) -> Optional[Dict]:
    doc = db.collection("Orders").document(order_id).get()
    return doc.to_dict() | {"id": doc.id} if doc.exists else None

def GetAllOrders():
    """Fetch all orders from Firestore."""
    orders_ref = db.collection("Orders").stream()
    orders = []
    for doc in orders_ref:
        data = doc.to_dict()
        data["id"] = doc.id
        orders.append(data)
    return orders



import firebase_admin
from firebase_admin import firestore

db = firestore.client()

def get_all_orders():
    orders_ref = db.collection('orders')
    docs = orders_ref.stream()

    orders = []
    for doc in docs:
        data = doc.to_dict()
        data['order_id'] = doc.id  # Optional: include Firestore doc ID
        orders.append(data)
    return orders

# ---------------- Filtering ----------------

def get_orders_by_client(client_id: str) -> List[Dict]:
    docs = db.collection("Orders").where(filter=FieldFilter("client_id", "==", client_id)).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_orders_by_supplier(supplier_id: str) -> List[Dict]:
    docs = db.collection("Orders").where(filter=FieldFilter("supplier_id", "==", supplier_id)).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_orders_by_status(status: str) -> List[Dict]:
    docs = db.collection("Orders").where(filter=FieldFilter("status", "==", status)).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_orders_by_date_range(start_date: datetime, end_date: datetime) -> List[Dict]:
    docs = db.collection("Orders")\
        .where(filter=FieldFilter("date", ">=", start_date))\
        .where(filter=FieldFilter("date", "<=", end_date))\
        .stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_total_sales_in_period(start_date: datetime, end_date: datetime) -> float:
    orders = get_orders_by_date_range(start_date, end_date)
    return sum(o.get("total_amount", 0) for o in orders)

# ---------------- Update/Delete ----------------

def update_order(order_id: str, update_data: Dict):
    update_data["updated_at"] = firestore.SERVER_TIMESTAMP
    db.collection("Orders").document(order_id).update(update_data)

def delete_order(order_id: str):
    db.collection("Orders").document(order_id).delete()

# ---------------- Invoice Support ----------------

def search_orders_by_invoice_number(invoice_number: str) -> List[Dict]:
    docs = db.collection("Orders").where(filter=FieldFilter("invoice_number", "==", invoice_number)).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]
