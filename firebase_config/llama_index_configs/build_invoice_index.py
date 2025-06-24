# import os
# from llama_index.core import Document, Settings
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from firebase_config.llama_index_configs import global_settings 
# from firebase_config.invoices import get_all_invoices
# from .invoice_index import build_invoices_index

# # Set embedding model globally
# Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# def build_invoice_documents():
#     invoices = get_all_invoices()
#     docs = []
#     for invoice in invoices:
#         text = f"""
#         Client ID: {invoice.get("client_id")}
#         Invoice Date: {invoice.get("invoice_date")}
#         Invoice No.: {invoice.get("invoice_number")}
#         Items: {invoice.get("items")}
#         Order ID: {invoice.get("order_id")}
#         Payment Status: {invoice.get("payment_status")}
#         Total Amount: {invoice.get("total_amount")}
#         Amount Paid: {invoice.get("amount_paid")}
#         Amount Due: {invoice.get("due_amount")}

#         """
#         docs.append(Document(text=text.strip()))
#     return docs


# if __name__ == "__main__":
#     docs = build_invoice_documents()
#     if not docs:
#         print("❌ No invoice found. Index not built.")
#     else:
#         build_invoices_index(docs)
#         print("✅ Invoices index built and saved.")
