# from llama_index.core import Settings
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# # Use Hugging Face for embeddings
# Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# # Optionally disable LLM to avoid OpenAI completely
# Settings.llm = None

import os
import logging
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__file__)

# Load environment variables
load_dotenv()

# Qdrant client configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

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

# Set embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1")
Settings.llm = None

# Global vector store for clients
client_vector_store = QdrantVectorStore(client=qdrant_client, collection_name="clients")

def global_settings():
    return {
        "embed_model": Settings.embed_model,
        "client_vector_store": client_vector_store
    }
