import os
from llama_index.core import Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from firebase_config.llama_index_configs import global_settings 
from firebase_config.finance import get_payments
from .payment_index import build_payments_index

# Set embedding model globally
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_payment_documents():
    items = get_payments()
    docs =[]
    for item in items:
        text = f"""
        Client ID: {item.get("client_id")}
        Supplier ID: {item.get("supplier_id")}
        Invoice ID: {item.get("invoice_id")}
        Payment Mode: {item.get("payment_mode")}
        Reference No.: {item.get("reference_no")}
        Amount: {item.get("amount")}
        Remarks: {item.get("remarks")}
        Payment Date: {item.get("payment_date")}
        """
        docs.append(Document(text=text.strip()))
    return docs

if __name__ == "__main__":
    docs = build_payment_documents()
    if not docs:
        print("❌ No Clients found. Index not built.")
    else:
        build_payments_index(docs)
        print("✅ Clients index built and saved.")