import logging
from llama_index.core import VectorStoreIndex, Settings
from firebase_config.llama_index_configs.global_settings import global_settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def build_clients_index(documents):
    try:
        settings = global_settings()
        Settings.embed_model = settings["embed_model"]
        vector_store = settings["client_vector_store"]
        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=vector_store,
            embed_model=Settings.embed_model
        )
        logger.info("Successfully built clients index in Qdrant Cloud")
        return index
    except Exception as e:
        logger.error(f"Error building clients index: {e}")
        raise

def load_clients_index():
    try:
        settings = global_settings()
        Settings.embed_model = settings["embed_model"]
        vector_store = settings["client_vector_store"]
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=Settings.embed_model
        )
        logger.info("Successfully loaded clients index from Qdrant Cloud")
        return index
    except Exception as e:
        logger.error(f"Error loading clients index: {e}")
        raise