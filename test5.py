import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.ingestion import IngestionPipeline

# ---------------------- Config ---------------------- #
load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH")


# ---------------------- Logging ---------------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------- Firebase Init ---------------------- #

docs = db.collection("Clients").stream()
documents = []

for doc in docs:
    data = doc.to_dict()
    if "text" in data and data["text"].strip():
        documents.append(Document(text=data["text"].strip()))
logger.info(f"✅ Pulled {len(documents)} documents from Firebase")

# ---------------------- Load SentenceTransformer directly ---------------------- #
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.bridge.pydantic import PrivateAttr

class CustomEmbedding(HuggingFaceEmbedding):
    _model: SentenceTransformer = PrivateAttr()

    def _init_(self, model: SentenceTransformer):
        super()._init_(model_name=None)  # model_name not needed
        self._model = model

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()

# Inject manual model
manual_model = SentenceTransformer("all-MiniLM-L6-v2")
embed_model = CustomEmbedding(model=manual_model)
Settings.embed_model = embed_model
Settings.llm = None

# ---------------------- Ingestion & Parsing ---------------------- #
parser = SimpleNodeParser.from_defaults(chunk_size=512, chunk_overlap=50)
pipeline = IngestionPipeline(transformations=[parser, embed_model])
nodes = pipeline.run(documents)

if not nodes:
    raise ValueError("⚠ No valid nodes extracted/embedded.")

# ---------------------- Qdrant Setup ---------------------- #
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
collection_name = "firebase_collection_upload"
qdrant_client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)
vector_store = QdrantVectorStore(client=qdrant_client, collection_name=collection_name)
vector_store.add(nodes)

logger.info(f"✅ Uploaded {len(nodes)} chunks to Qdrant collection '{collection_name}'")