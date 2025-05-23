from firebase_config.config import db

def add_employee(employee_data):
    db.collection("employees").add(employee_data)

def get_employee_by_name(name):
    docs = db.collection("employees").where("name", "==", name).stream()
    return [doc.to_dict() for doc in docs]

def get_all_employees():
    docs = db.collection("employees").stream()
    return [doc.to_dict() for doc in docs]

def update_employee(employee_id, updated_data):
    db.collection("employees").document(employee_id).update(updated_data)

def delete_employee(employee_id):
    db.collection("employees").document(employee_id).delete()
