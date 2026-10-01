def get_retriever(index, embeddings):

    def retrieve(question):

        query_embedding = embeddings.embed_query(question)

        results = index.query(
            vector=query_embedding,
            top_k=1,
            include_metadata=True
        )

        documents = []

        for match in results["matches"]:

            text = match["metadata"]["text"]

            documents.append({
                "text": text,
                "score": match["score"]
            })

        return documents

    return retrieve