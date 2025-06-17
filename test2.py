# # # Run this in a script or shell
# from google.cloud import firestore
# from google.oauth2 import service_account
# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./firebase_config/firebase_key.json"

# credentials = service_account.Credentials.from_service_account_file(
#     "C:/Users/thebe/ML/Codes/Balaji Health Care Assisstant/balaji-health-care-assistant/firebase_config/firebase_key.json"
# )
# db = firestore.Client(credentials=credentials, project="ai-business-a-a129b")

# docs = db.collection("Clients").stream()
# for doc in docs:
#     print(doc.id, doc.to_dict())
# # import os
# # print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])




import os
from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./firebase_config/firebase_key.json"

db = firestore.Client()

# Try reading from a collection
try:
    clients_ref = db.collection("Clients")
    docs = list(clients_ref.stream())

    if not docs:
        print("✅ Connected to Firestore, but no documents found in 'clients'.")
    else:
        print(f"✅ Connected to Firestore. Found {len(docs)} documents.")
        for doc in docs:
            print(doc.id, doc.to_dict())

except Exception as e:
    print("❌ Error:", e)
