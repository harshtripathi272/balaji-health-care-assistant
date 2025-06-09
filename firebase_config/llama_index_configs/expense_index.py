import os
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from firebase_config.llama_index_configs import global_settings 
index_path = "indexes/expenses"

def build_expenses_index(documents):
    os.makedirs(index_path, exist_ok=True)
    index = VectorStoreIndex.from_documents(documents)  # no service_context
    index.storage_context.persist(persist_dir=index_path)

def load_expenses_index():
    if not os.path.exists(index_path) or not os.listdir(index_path):
        raise FileNotFoundError("❌ Expenses index not found or empty. Please build it first.")
    storage_context = StorageContext.from_defaults(persist_dir=index_path)
    return load_index_from_storage(storage_context)  # no service_context
