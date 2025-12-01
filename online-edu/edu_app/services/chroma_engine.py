import chromadb


client = chromadb.Client()
collection = client.create_collection(name="edu_business_collection")


with open("edu_app/services/business_knowledge.txt", "r", encoding="utf-8") as f:
    content = f.readlines()


sentences = [line.strip() for line in content if line.strip()]


ids = [f"id{i}" for i in range(len(sentences))]


collection.add(
    ids=ids,
    documents=sentences,
)


def search(query: str):
    results = collection.query(
        query_texts=[query],
        n_results=1
    )

    best_match = results["documents"][0][0]

    return best_match


