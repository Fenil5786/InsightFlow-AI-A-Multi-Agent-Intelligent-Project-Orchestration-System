# rag/embedding_pipeline.py

import os
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# -----------------------------
# 1. Load Embedding Model
# -----------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# -----------------------------
# 2. Initialize ChromaDB
# -----------------------------
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="projects")

# -----------------------------
# 3. Load Data
# -----------------------------
DATA_PATH = os.path.join("data", "sharepoint_projects.csv")

df = pd.read_csv(DATA_PATH)

documents = []

for i, row in df.iterrows():
    text = f"""
    Project: {row['project_name']}
    Status: {row['status']}
    Progress: {row['progress']}
    Risk: {row['risk_level']}
    Owner: {row['owner']}
    Last Update: {row['last_update']}
    """
    documents.append(text.strip())

# -----------------------------
# 4. Generate Embeddings
# -----------------------------
embeddings = model.encode(documents).tolist()

# -----------------------------
# 5. Store in ChromaDB
# -----------------------------
# Reset collection safely
try:
    client.delete_collection(name="projects")
except:
    pass

collection = client.get_or_create_collection(name="projects")
for i, doc in enumerate(documents):
    collection.add(
        documents=[doc],
        embeddings=[embeddings[i]],
        ids=[str(i)]
    )

# -----------------------------
# 6. BM25 Setup (Keyword Search)
# -----------------------------
tokenized_docs = [doc.split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)

# -----------------------------
# 7. Semantic Search
# -----------------------------
def semantic_search(query, n_results=50):
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )

    return results['documents'][0]


# -----------------------------
# 8. Keyword Search
# -----------------------------
def keyword_search(query, n_results=3):
    tokenized_query = query.split()
    return bm25.get_top_n(tokenized_query, documents, n=n_results)


# -----------------------------
# 9. Hybrid Search
# -----------------------------
def hybrid_search(query):
    semantic_results = semantic_search(query)
    keyword_results = keyword_search(query)

    combined = list(set(semantic_results + keyword_results))
    return combined


# -----------------------------
# 10. Test Run
# -----------------------------
if __name__ == "__main__":
    query = "Which projects are high risk?"

    results = hybrid_search(query)

    print("\n🔍 Query:", query)
    print("\n📊 Results:\n")

    for r in results:
        print(r)
        print("-" * 50)