from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def find_similar_tickets(new_ticket, previous_tickets, top_n=3):

    if not previous_tickets:
        return []

    ticket_texts = []

    for ticket in previous_tickets:
        ticket_texts.append(
            ticket["title"] + " " + ticket["description"]
        )

    all_tickets = ticket_texts + [new_ticket]

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(all_tickets)

    similarity_scores = cosine_similarity(
        vectors[-1],
        vectors[:-1]
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