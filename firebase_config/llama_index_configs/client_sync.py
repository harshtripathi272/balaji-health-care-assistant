import logging
import os
from google.cloud import firestore
from google.oauth2 import service_account
from llama_index.core import Document
from firebase_config.llama_index_configs.global_settings import global_settings
from firebase_config.llama_index_configs.client_index2 import load_clients_index
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def create_document(client_data: dict, client_id: str) -> Document:
    """Create a LlamaIndex Document from client data."""
    text = f"""
    Name: {client_data.get("name")}
    Price List: {client_data.get("price_list")}
    Due amount: {client_data.get("due_amount")}
    Address: {client_data.get("address")}
    """.strip()
    return Document(
        text=text,
        doc_id=client_id,
        metadata={"client_id": client_id, "name": client_data.get("name")}
    )

def sync_client_to_qdrant(event: firestore.DocumentSnapshot):
    """Sync Firestore client changes to Qdrant."""
    try:
        client_id = event.id
        settings = global_settings()
        qdrant_client = settings["client_vector_store"].client
        index = load_clients_index()

        if not event.exists:
            # Document deleted
            try:
                qdrant_client.delete(
                    collection_name="clients",
                    points_selector=[client_id]
                )
                logger.info(f"Deleted client {client_id} from Qdrant")
            except Exception as e:
                logger.error(f"Error deleting client {client_id} from Qdrant: {e}")
            return

        # Document created or updated
        client_data = event.to_dict()
        document = create_document(client_data, client_id)

        # Upsert to Qdrant
        index.insert([document])
        logger.info(f"Synced client {client_id} to Qdrant")

    except Exception as e:
        logger.error(f"Error syncing client {client_id} to Qdrant: {e}")

def listen_for_client_changes():
    """Listen for Firestore client collection changes."""
    try:
        # Initialize Firestore client with service account
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path or not os.path.exists(credentials_path):
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set or file not found")
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        db = firestore.Client(credentials=credentials, project=os.getenv("FIRESTORE_PROJECT_ID"))

        clients_ref = db.collection("clients")

        # Initialize Qdrant collection if not exists
        settings = global_settings()
        qdrant_client = settings["client_vector_store"].client
        try:
            qdrant_client.get_collection("clients")
        except Exception:
            qdrant_client.create_collection(
                collection_name="clients",
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            logger.info("Created Qdrant clients collection")

        # Set up Firestore listener
        clients_ref.on_snapshot(sync_client_to_qdrant)
        logger.info("Started Firestore client sync listener")

        # Keep the script running
        import time
        while True:
            time.sleep(1)

    except Exception as e:
        logger.error(f"Error in client sync listener: {e}")
        raise

if __name__ == "__main__":
    listen_for_client_changes()