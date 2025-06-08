from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Use Hugging Face for embeddings
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Optionally disable LLM to avoid OpenAI completely
Settings.llm = None
