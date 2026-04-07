import chromadb
import pandas as pd
from datasets import load_dataset
import json

print("Setting up ChromaDB...")

# Create a local persistent database folder called patient_db
client = chromadb.PersistentClient(path="./patient_db")

# Create a collection to store the clinical notes
collection = client.get_or_create_collection(
    name="clinical_notes",
    metadata={"hnsw:space": "cosine"}
)

print("Loading dataset...")
dataset = load_dataset("AGBonnet/augmented-clinical-notes", split="train[:200]")
df = dataset.to_pandas()

print("Storing notes into ChromaDB...")

success = 0
skipped = 0

for i, row in df.iterrows():
    try:
        # Parse the summary JSON for metadata
        summary = json.loads(row["summary"]) if isinstance(row["summary"], str) else row["summary"]

        # Pull useful metadata fields safely
        patient_info = summary.get("patient information", {})
        age = patient_info.get("age", "Unknown")
        sex = patient_info.get("sex", "Unknown")
        visit_motivation = summary.get("visit motivation", "Unknown")

        # Store the full note as the document
        # Store metadata alongside it for filtering later
        collection.add(
            documents=[row["full_note"]],
            metadatas=[{
                "idx": str(row["idx"]),
                "age": str(age),
                "sex": str(sex),
                "visit_motivation": str(visit_motivation)[:200]  # cap length
            }],
            ids=[str(row["idx"])]
        )
        success += 1

    except Exception as e:
        skipped += 1
        continue

print(f"\n✅ Successfully stored: {success} notes")
print(f"⚠️  Skipped: {skipped} rows")
print(f"\nTotal notes in ChromaDB: {collection.count()}")

# ── Retrieval Function ───────────────────────────────────────────

def retrieve_similar_notes(query: str, n_results: int = 3):
    """
    Given a transcript or query, find the most similar
    clinical notes stored in ChromaDB
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    notes = results["documents"][0]
    metadatas = results["metadatas"][0]

    print(f"\n🔍 Top {n_results} similar notes retrieved:")
    for i, (note, meta) in enumerate(zip(notes, metadatas)):
        print(f"\n[{i+1}] Age: {meta['age']} | Sex: {meta['sex']}")
        print(f"     Visit: {meta['visit_motivation'][:100]}")
        print(f"     Note preview: {note[:150]}...")

    return notes, metadatas


# Test the retrieval
if __name__ == "__main__":
    test_query = "Patient has neck pain and difficulty walking"
    retrieve_similar_notes(test_query)

