# vector_indexes/orders_index.py

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
import os

# Ensure data is saved persistently
index_path = "indexes/orders"

def build_orders_index(documents):
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=index_path)

def load_orders_index():
    if not os.path.exists(index_path):
        raise FileNotFoundError("Orders index not found. Please build it first.")
    storage_context = StorageContext.from_defaults(persist_dir=index_path)
    return load_index_from_storage(storage_context)
