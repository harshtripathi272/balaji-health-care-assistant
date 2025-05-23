from difflib import get_close_matches
from firebase_config.config import db

def fuzzy_search_by_name(collection_name, input_name, threshold=0.6):
    docs = db.collection(collection_name).stream()
    names = [(doc.id, doc.to_dict().get("name", "")) for doc in docs]
    name_list = [name for _, name in names]
    match = get_close_matches(input_name, name_list, n=1, cutoff=threshold)
    for doc_id, name in names:
        if name == match[0]:
            return doc_id
    return None

def search_entity_by_any_field(collection_name, search_term):
    search_term = search_term.lower()
    results = []
    docs = db.collection(collection_name).stream()
    for doc in docs:
        data = doc.to_dict()
        for value in data.values():
            if search_term in str(value).lower():
                results.append(data)
                break
    return results

def summarize_entity(collection_name, doc_id):
    doc = db.collection(collection_name).document(doc_id).get()
    if doc.exists:
        data = doc.to_dict()
        return {k: data[k] for k in list(data)[:5]}  # Top 5 key fields summary
    return {}
