import os
from llama_index.core import Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from firebase_config.llama_index_configs import global_settings 
from firebase_config.clients import get_all_clients
from .client_index import build_clients_index

# Set embedding model globally
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_client_documents():
    clients = get_all_clients()
    docs =[]
    for client in clients:
        text = f"""
        Name: {client.get("name")}
        Price List: {client.get("price_list")}
        Due amount: {client.get("due_amount")}
        """
        docs.append(Document(text=text.strip()))
    return docs

if __name__ == "__main__":
    docs = build_client_documents()
    if not docs:
        print("❌ No Clients found. Index not built.")
    else:
        build_clients_index(docs)
        print("✅ Clients index built and saved.")