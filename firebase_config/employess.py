from firebase_config.config import db
from google.cloud import firestore
from typing import Dict, List

def get_next_id(prefix: str, counter_name: str) -> str:
    counter_ref = db.collection("doc_counters").document(counter_name)
    counter_doc = counter_ref.get()

    if not counter_doc.exists:
        counter_ref.set({"last_id": 1})
        next_id = 1
    else:
        counter_ref.update({"last_id": firestore.Increment(1)})
        next_id = counter_doc.to_dict()["last_id"] + 1

    return f"{prefix}{next_id:04d}"

def add_employee(employee_data: Dict) -> str:
    employee_id = get_next_id("E", "employees")
    employee_doc = {
        "id": employee_id,
        "name": employee_data.get("name", ""),
        "collected": 0,
        "phone": employee_data.get("phone"),
        "paid": 0,
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP
    }
    db.collection("Employees").document(employee_id).set(employee_doc)
    return employee_id

def get_employee_by_name(name):
    docs = db.collection("Employees").where("name", "==", name).stream()
    return [doc.to_dict() for doc in docs]

def get_all_employees():
    docs = db.collection("Employees").stream()
    return [doc.to_dict() for doc in docs]

def update_employee(employee_id, updated_data):
    db.collection("Employees").document(employee_id).update(updated_data)

def delete_employee(employee_id):
    db.collection("Employees").document(employee_id).delete()
