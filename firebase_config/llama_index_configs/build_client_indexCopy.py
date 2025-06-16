import os
import logging
from llama_index.core import Document, Settings
from firebase_config.llama_index_configs.global_settings import global_settings

from firebase_config.clients import get_all_clients
from firebase_config.llama_index_configs.client_index2 import build_clients_index

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def build_client_documents():
    try:
        clients = get_all_clients()
        docs = []
        for client in clients:
            text = f"""
            Name: {client.get("name")}
            Price List: {client.get("price_list")}
            Due amount: {client.get("due_amount")}
            Address: {client.get("address")}
            """.strip()
            docs.append(Document(
                text=text,
                doc_id=client.get("id"),
                metadata={"client_id": client.get("id"), "name": client.get("name")}
            ))
        logger.info(f"Built {len(docs)} client documents")
        return docs
    except Exception as e:
        logger.error(f"Error building client documents: {e}")
        return []

if __name__ == "__main__":
    try:
        # Apply global settings
        settings = global_settings()
        Settings.embed_model = settings["embed_model"]
        docs = build_client_documents()
        if not docs:
            logger.error("❌ No Clients found. Index not built.")
            print("❌ No Clients found. Index not built.")
        else:
            build_clients_index(docs)
            logger.info("✅ Clients index built and saved to Qdrant Cloud.")
            print("✅ Clients index built and saved to Qdrant Cloud.")
    except Exception as e:
        logger.error(f"❌ Error building index: {e}")
        print(f"❌ Error building index: {e}")