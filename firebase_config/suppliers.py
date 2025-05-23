from firebase_config.config import db

def add_supplier(supplier_data):
    db.collection("suppliers").add(supplier_data)

def get_supplier_by_name(name):
    docs = db.collection("suppliers").where("name", "==", name).stream()
    return [doc.to_dict() for doc in docs]

def get_all_suppliers():
    docs = db.collection("suppliers").stream()
    return [doc.to_dict() for doc in docs]

def update_supplier(supplier_id, updated_data):
    db.collection("suppliers").document(supplier_id).update(updated_data)

def delete_supplier(supplier_id):
    db.collection("suppliers").document(supplier_id).delete()


def get_supplier_items_summary(supplier_id):
    docs = db.collection("purchase_orders").where("supplier_id", "==", supplier_id).stream()
    item_summary = {}
    for doc in docs:
        for item in doc.to_dict().get("items", []):
            name = item["name"]
            qty = item["quantity"]
            item_summary[name] = item_summary.get(name, 0) + qty
    return item_summary
