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
    from firebase_config.config import db
    from google.cloud import firestore
    from google.cloud.firestore_v1.base_query import FieldFilter

    # Extract core fields
    client_id = order_data.get("client_id", "")
    client_name = order_data.get("client_name", "")
    supplier_id = order_data.get("supplier_id", "")
    supplier_name = order_data.get("supplier_name", "")

    order_type = order_data.get("order_type")
    status = order_data.get("status", "pending")
    updated_by = order_data.get("updated_by", "system")
    created_by = order_data.get("created_by", updated_by)
    total_amount = order_data.get("total_amount", 0.0)
    payment_method = order_data.get("payment_method", "unpaid")
    amount_paid = order_data.get("amount_paid", 0.0)
    remarks = order_data.get("remarks", "")
    draft = order_data.get("draft", False)
    amount_collected_by = order_data.get("amount_collected_by", "")
    payment_status = order_data.get("payment_status", "unpaid")

    invoice_number = order_data.get("invoice_number") if order_type != "delivery_challan" else None
    challan_number = order_data.get("challan_number") if order_type == "delivery_challan" else None

    processed_items = []
    total_quantity = 0
    total_tax = 0

    for item in order_data["items"]:
        item_name = item["item_name"]
        quantity = item["quantity"]
        price = item["price"]
        tax = item.get("tax", 0)
        discount = item.get("discount", 0)
        batch_number = item.get("batch_number", "")
        expiry = item.get("expiry", "")

        # Lookup item by name
        query = db.collection("Inventory Items").where(filter=FieldFilter("name", "==", item_name)).limit(1).stream()
        item_doc = next(query, None)
        if not item_doc:
            raise ValueError(f"❌ Inventory item '{item_name}' not found.")

        item_id = item_doc.id
        item_data = item_doc.to_dict()
        batches = item_data.get("batches", [])
        updated_batches = []
        batch_found = False

        # Modify quantity of the specific batch
        quantity = float(quantity)  # Ensure it's numeric

        for batch in batches:
            # Convert batch quantity safely
            batch_qty = float(batch.get("quantity", 0))
            if batch.get("batch_number") == batch_number:
                batch_found = True
                if order_type == "purchase":
                    batch["quantity"] = batch_qty + quantity
                elif order_type in ["sales", "delivery_challan"]:
                    if batch_qty < quantity:
                        raise ValueError(f"❌ Not enough stock in batch {batch_number} of item '{item_name}'.")
                    batch["quantity"] = batch_qty - quantity
            updated_batches.append(batch)


        if not batch_found:
            if order_type == "purchase":
                # Add new batch if it doesn’t exist (for purchase only)
                updated_batches.append({
                    "batch_number": batch_number,
                    "Expiry": expiry,
                    "quantity": quantity
                })
            else:
                raise ValueError(f"❌ Batch {batch_number} not found for item '{item_name}'.")

        # Update total item-level quantity
        total_item_quantity = sum(batch["quantity"] for batch in updated_batches)

        # Update inventory item doc with new stock and batches
        db.collection("Inventory Items").document(item_id).update({
            "stock_quantity": total_item_quantity,
            "batches": updated_batches
        })

        # Record processed item
        processed_items.append({
            "item_id": item_id,
            "item_name": item_name,
            "quantity": quantity,
            "price": price,
            "discount": discount,
            "tax": tax,
            "batch_number": batch_number,
            "expiry": expiry
        })

        total_quantity += quantity
        total_tax += tax

    # Timestamp
    timestamp = firestore.SERVER_TIMESTAMP

    # Final Order Document
    order_doc = {
        "client_id": client_id,
        "client_name": client_name,
        "supplier_id": supplier_id,
        "supplier_name": supplier_name,
        "order_type": order_type,
        "order_date": timestamp,
        "status": status,
        "items": processed_items,
        "total_quantity": total_quantity,
        "total_tax": total_tax,
        "total_amount": total_amount,
        "invoice_number": invoice_number,
        "challan_number": challan_number,
        "payment_method": payment_method,
        "amount_paid": amount_paid,
        "payment_status": payment_status,
        "remarks": remarks,
        "draft": draft,
        "amount_collected_by": amount_collected_by,
        "created_by": created_by,
        "updated_by": updated_by,
        "created_at": timestamp,
        "updated_at": timestamp
    }

    # Save to Firestore
    order_ref = db.collection("Orders").add(order_doc)
    order_id = order_ref[1].id
    print(f"[✔] Order added with ID: {order_id} (type: {order_type})")
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
        if data:  # Ensure the doc is not empty
            data['order_id'] = doc.id  # Add Firestore doc ID if needed
            orders.append(data)
    return orders
def get_all_orders():
    docs = db.collection("Orders").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

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

def get_invoice_by_order_id(order_id: str) -> Optional[Dict]:
    doc = db.collection("Orders").document(order_id).get()
    if doc.exists:
        data = doc.to_dict()
        return {
            "invoice_number": data.get("invoice_number"),
            "due_date": data.get("due_date"),
            "payment_status": data.get("payment_status"),
            "amount_paid": data.get("amount_paid"),
            "total_amount": data.get("total_amount"),
            "client_id": data.get("client_id"),
            "client_name": data.get("client_name"),
            "items": data.get("items", []),
            "order_id": doc.id
        }
    return None

def search_orders_by_invoice_number(invoice_number: str) -> List[Dict]:
    docs = db.collection("Orders").where(filter=FieldFilter("invoice_number", "==", invoice_number)).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

