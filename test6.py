import os
from google.cloud import firestore
from google.oauth2 import service_account
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# --- FIRESTORE SETUP ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./firebase_config/firebase_key.json"

# if you want credentials explicitly (not needed if env var is set)
# credentials = service_account.Credentials.from_service_account_file(
#     "./firebase_config/firebase_key.json"
# )
# db = firestore.Client(credentials=credentials, project="ai-business-a-a129b")

db = firestore.Client()

try:
    clients_ref = db.collection("Clients")
    docs = list(clients_ref.stream())

    if not docs:
        print("✅ Connected to Firestore, but no documents found in 'clients'.")
        exit()
    else:
        print(f"✅ Connected to Firestore. Found {len(docs)} documents.")

        texts = []
        payloads = []
        for doc in docs:
            data = doc.to_dict()
            if "name" in data:
                texts.append(data["name"])
                payloads.append(data)
            else:
                print(f"⚠ Skipping doc {doc.id} due to missing 'name' field.")

except Exception as e:
    print("❌ Firestore error:", e)
    exit()

# --- EMBEDDINGS SETUP ---
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts)

# --- QDRANT SETUP ---
QDRANT_URL = os.getenv("QDRANT_URL") or "https://your-qdrant-host.qdrant.cloud"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or "your_api_key"

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

collection_name = "clients_collection"  # change if u want another name

client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# --- UPLOAD TO QDRANT ---
points = [
    PointStruct(id=i, vector=embeddings[i].tolist(), payload=payloads[i])
    for i in range(len(embeddings))
]

client.upsert(collection_name=collection_name, points=points)

print("✅ Upload to Qdrant complete.")

# --- OPTIONAL: SEARCH TEST ---
search_result = client.search(
    collection_name=collection_name,
    query_vector=model.encode("Harshit Singh").tolist(),
    limit=3
)

for i, result in enumerate(search_result):
    print(f"\n🔎 Result {i+1}:")
    print("Score:", result.score)
    print("Payload:", result.payload)