from firebase_config.config import db

def add_expense(expense_data):
    db.collection("expenses").add(expense_data)

def get_expenses_by_category(category):
    docs = db.collection("expenses").where("category", "==", category).stream()
    return [doc.to_dict() for doc in docs]

def get_expenses_by_date_range(start_date, end_date):
    docs = db.collection("expenses").where("date", ">=", start_date).where("date", "<=", end_date).stream()
    return [doc.to_dict() for doc in docs]

def get_all_expenses():
    docs = db.collection("expenses").stream()
    return [doc.to_dict() for doc in docs]

def delete_expense(expense_id):
    db.collection("expenses").document(expense_id).delete()
