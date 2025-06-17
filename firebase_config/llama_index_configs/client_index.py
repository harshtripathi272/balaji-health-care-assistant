import os
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from firebase_config.llama_index_configs.global_settings import global_settings 

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, StorageContext

index_path = "indexes/clients"

def build_clients_index(documents):
    os.makedirs(index_path, exist_ok=True)

    # 🧠 Get embed_model + Qdrant client
    settings = global_settings()
    embed_model = settings["embed_model"]
    qdrant_client = settings["qdrant_client"]

    # 📦 Qdrant vector store setup (with collection name)
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name="clients",
    )

    # 🧠 Build index with Qdrant
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    # Optional: save local metadata (not vectors)
    index.storage_context.persist(persist_dir=index_path)


def load_clients_index():
    if not os.path.exists(index_path) or not os.listdir(index_path):
        raise FileNotFoundError("❌ Clients index not found or empty. Please build it first.")

    settings = global_settings()
    qdrant_client = settings["qdrant_client"]

    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name="clients",
    )
    storage_context = StorageContext.from_defaults(
        persist_dir=index_path,
        vector_store=vector_store
    )
    return load_index_from_storage(storage_context)

