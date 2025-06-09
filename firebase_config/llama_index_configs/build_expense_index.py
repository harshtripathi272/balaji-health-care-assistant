import os
from llama_index.core import Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from firebase_config.llama_index_configs import global_settings 
from firebase_config.finance import get_expenses
from .expense_index import build_expenses_index

# Set embedding model globally
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_expense_documents():
    items = get_expenses()
    docs =[]
    for item in items:
        text = f"""
        Paid By: {item.get("paid_by")}
        Category: {item.get("category")}
        Expense Date: {item.get("expense_date")}
        Amount: {item.get("amount")}
        Created At: {item.get("created_at")}
        Remarks: {item.get("reamarks")}
        """
        docs.append(Document(text=text.strip()))
    return docs

if __name__ == "__main__":
    docs = build_expense_documents()
    if not docs:
        print("❌ No Clients found. Index not built.")
    else:
        build_expenses_index(docs)
        print("✅ Clients index built and saved.")