import os 
from dotenv import load_dotenv
from firebase_config.tools import query_clients_semantic
from qdrant_client import QdrantClient
import logging
from qdrant_client.http.models import VectorParams, Distance
from dotenv import load_dotenv
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__file__)
if not QDRANT_URL or not QDRANT_API_KEY:
    logger.error("Qdrant URL or API Key not set. Please configure environment variables.")
    raise ValueError("Qdrant URL and API Key are required.")

try:
    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    # Test connection
    qdrant_client.get_collections()
    logger.info("Successfully connected to Qdrant Cloud")
except Exception as e:
    logger.error(f"Failed to connect to Qdrant Cloud: {e}")
    raise


# collections = qdrant_client.get_collections()
# print([c.name for c in collections.collections])

# qdrant_client.recreate_collection(
#     collection_name="clients",
#     vectors_config=VectorParams(size=384, distance=Distance.COSINE)
# )
ount = qdrant_client.count(collection_name="clients").count
# print(query_clients_semantic("Total number of clients"))


# from qdrant_client import QdrantClient
# from qdrant_client.http.models import VectorParams, Distance



# collection_name = "clients"

# if not qdrant_client.collection_exists(collection_name=collection_name):
#     qdrant_client.create_collection(
#         collection_name=collection_name,
#         vectors_config=VectorParams(size=384, distance=Distance.COSINE)
#     )
#     print(f"✅ Created '{collection_name}' collection in Qdrant Cloud")
# else:
#     print(f"ℹ️ Collection '{collection_name}' already exists.")
