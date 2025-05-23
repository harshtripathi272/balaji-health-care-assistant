# test_firebase.py
from firebase_config.config import db



# Test: Read clients collection
def test_read_clients():
    clients = db.collection("clients").get()
    for client in clients:
        print(f"{client.id} => {client.to_dict()}")

# Run test
if __name__ == "__main__":
    test_read_clients()
