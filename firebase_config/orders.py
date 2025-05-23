from firebase_config.config import db
from google.cloud import firestore

from google.cloud.firestore_v1 import ArrayRemove, ArrayUnion

def add_order(order_data):
    """
    order_data = {
        "client_name": str,
        "items": list of item names (str),
        "total_amount": float,
        "order_type": "purchase" or "sell"
    }
    """
    # Build items list with quantity = 1
    items_list = [{"item_name": name, "quantity": 1} for name in order_data["items"]]

    # Prepare order document
    order_doc = {
        "client_name": order_data["client_name"],
        "items": items_list,
        "total_amount": order_data["total_amount"],
        "order_type": order_data["order_type"],
        "date": firestore.SERVER_TIMESTAMP
    }

    # Add order to Firestore
    order_ref = db.collection("orders").add(order_doc)

    # Update inventory stock accordingly
    for item in items_list:
        # Fetch inventory item doc by name
        docs = db.collection("inventory_items").where("name", "==", item["item_name"]).stream()
        doc_list = list(docs)
        if not doc_list:
            print(f"Item '{item['item_name']}' not found in inventory!")
            continue

        doc = doc_list[0]
        current_stock = doc.to_dict().get("stock_quantity", 0)
        new_stock = current_stock + item["quantity"] if order_data["order_type"] == "purchase" else current_stock - item["quantity"]

        # Update stock quantity in inventory
        db.collection("inventory_items").document(doc.id).update({"stock_quantity": new_stock})

    print("Order added and inventory updated.")

def get_order_by_id(order_id):
    """Fetch order by Firestore document ID."""
    doc = db.collection("orders").document(order_id).get()
    return doc.to_dict() if doc.exists else None

def get_orders_by_client(client_id):
    """Get all orders for a specific client."""
    docs = db.collection("orders").where("client_id", "==", client_id).stream()
    return [doc.to_dict() for doc in docs]

def get_orders_by_supplier(supplier_id):
    """Get all purchase orders from a specific supplier."""
    docs = db.collection("orders").where("supplier_id", "==", supplier_id).stream()
    return [doc.to_dict() for doc in docs]

def get_orders_by_date_range(start_date, end_date):
    """Get orders placed between start_date and end_date."""
    docs = db.collection("orders")\
        .where("order_date", ">=", start_date)\
        .where("order_date", "<=", end_date)\
        .stream()
    return [doc.to_dict() for doc in docs]

def update_order(order_id, update_data):
    """Update specific fields in an order."""
    db.collection("orders").document(order_id).update(update_data)

def delete_order(order_id):
    """Delete an order."""
    db.collection("orders").document(order_id).delete()

def get_all_orders():
    """Return all orders in the system."""
    docs = db.collection("orders").stream()
    return [doc.to_dict() for doc in docs]

def get_orders_by_status(status):
    """Fetch orders filtered by status (e.g., pending, completed)."""
    docs = db.collection("orders").where("status", "==", status).stream()
    return [doc.to_dict() for doc in docs]

def search_orders_by_invoice_number(invoice_number):
    """Search orders by invoice number (exact match)."""
    docs = db.collection("orders").where("invoice_number", "==", invoice_number).stream()
    return [doc.to_dict() for doc in docs]

# Optional: Partial search for invoice number (Firestore doesn't support partial string match natively)
# You may need to implement client-side filtering or integrate a full-text search service.


def get_total_sales_in_period(start_date, end_date):
    docs = get_orders_by_date_range(start_date, end_date)
    return sum(doc.get("total_amount", 0) for doc in docs)
