import os
from llama_index.core import Document, Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from firebase_config.orders import get_all_orders
from .order_index import build_orders_index

# ✅ Set local embedding model (instead of OpenAI)
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_order_documents():
    orders = get_all_orders()
    docs = []
    for order in orders:
        text = f"""
        Order ID: {order.get('invoice_number')}
        Date: {order.get('date')}
        Client: {order.get('client_name')}
        Items: {order.get('items')}
        Total: ₹{order.get('total')}
        Status: {order.get('status')}
        Remarks: {order.get('remarks', '')}
        """
        docs.append(Document(text=text.strip()))
    return docs

if __name__ == "__main__":
    docs = build_order_documents()
    build_orders_index(docs)
    print("✅ Orders index built and saved.")
