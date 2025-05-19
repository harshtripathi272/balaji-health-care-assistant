import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from firebase_config.config import db
def get_orders():
    order_ref = db.collection("orders")
    docs = order_ref.stream()
    return [doc.to_dict() for doc in docs]


def add_orders(order_data):
    db.collection("orders").add(order_data)

def update_orders(order_id, updated_data):
    db.collection("orders").document(order_id).update(updated_data)
    
