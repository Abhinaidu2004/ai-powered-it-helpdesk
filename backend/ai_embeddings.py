from sklearn.metrics.pairwise import cosine_similarity


# Model is not loaded at startup
model = None


def get_embedding_model():

    global model

    if model is None:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")

    return model


def find_semantic_similarity(new_ticket, previous_tickets, top_n=3):

    if not previous_tickets:
        return []

    ticket_texts = []

    for ticket in previous_tickets:
        ticket_texts.append(
            ticket["title"] + " " + ticket["description"]
        )

    embedding_model = get_embedding_model()

    new_embedding = embedding_model.encode([new_ticket])

    previous_embeddings = embedding_model.encode(ticket_texts)

    similarity_scores = cosine_similarity(
        new_embedding,
        previous_embeddings
    )[0]

    results = []

    for index, score in enumerate(similarity_scores):

        ticket = previous_tickets[index]

        results.append({
            "ticket_id": ticket["id"],
            "title": ticket["title"],
            "description": ticket["description"],
            "priority": ticket["priority"],
            "category": ticket["category"],
            "resolution": ticket["resolution"],
            "similarity": round(float(score), 3)
        })

    results.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    return results[:top_n]


if __name__ == "__main__":

    tickets = [
        {
            "id": 1,
            "title": "Wi-Fi not working",
            "description": "Laptop cannot connect to office Wi-Fi",
            "priority": "High",
            "category": "Network",
            "resolution": "Restarted the Wi-Fi adapter"
        },
        {
            "id": 2,
            "title": "Password problem",
            "description": "User cannot login to account",
            "priority": "High",
            "category": "Account",
            "resolution": "Reset the user password"
        }
    ]

    new_ticket = (
        "My computer is unable to connect "
        "to the wireless network"
    )

    results = find_semantic_similarity(
        new_ticket,
        tickets
    )

    for result in results:
        print(result)