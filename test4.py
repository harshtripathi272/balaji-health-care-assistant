import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Load from .env or just paste directly
QDRANT_URL = os.getenv("QDRANT_URL") or "https://your-qdrant-host.qdrant.cloud"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or "your_api_key"

# Init cloud Qdrant client
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# Init simple sentence-transformer
model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔤 Sample texts
texts = [
    "John Doe has hypertension.",
    "He also has Type 2 diabetes.",
    "The patient is on metformin."
]

# ⚡ Embed
embeddings = model.encode(texts)

# 📦 Create or recreate collection
collection_name = "test_collection_basic"
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# 🚀 Upload points
points = [
    PointStruct(id=i, vector=embeddings[i].tolist(), payload={"text": texts[i]})
    for i in range(len(texts))
]

client.upsert(collection_name=collection_name, points=points)

print("✅ Upload complete. Now testing search...")

# 🔍 Search
search_result = client.search(
    collection_name=collection_name,
    query_vector=model.encode("What does John Doe suffer from?").tolist(),
    limit=3
)

for i, result in enumerate(search_result):
    print(f"\n🔎 Result {i+1}:")
    print("Score:", result.score)
    print("Payload:", result.payload)