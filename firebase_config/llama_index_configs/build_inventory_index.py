import os
from llama_index.core import Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from firebase_config.llama_index_configs import global_settings
from firebase_config.inventory import get_all_inventory_items
from .item_index import build_items_index

# Set embedding model globally
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_item_documents():
    items = get_all_inventory_items()
    docs =[]
    for item in items:
        text = f"""
        Name: {item.get("name")}
        Stock Quantity: {item.get("stock_quantity")}
        Batch Info: {item.get("batch_info")}
        Base Price: {item.get("base_price")}
        Threshold: {item.get("low_stock_threshold")}
        """
        docs.append(Document(text=text.strip()))
    return docs

if __name__ == "__main__":
    docs = build_item_documents()
    if not docs:
        print("❌ No Clients found. Index not built.")
    else:
        build_items_index(docs)
        print("✅ Clients index built and saved.")