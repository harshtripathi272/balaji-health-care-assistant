from firebase_config.config import db

def get_chatbot_logs():
    logs_ref = db.collection("chatbot_history")
    docs = logs_ref.stream()
    return [doc.to_dict() for doc in docs]

def add_chatbot_log(log_data):
    db.collection("chatbot_history").add(log_data)

def delete_chatbot_log(log_id):
    db.collection("chatbot_history").document(log_id).delete()

def get_chatbot_log_by_id(log_id):
    doc = db.collection("chatbot_history").document(log_id).get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
