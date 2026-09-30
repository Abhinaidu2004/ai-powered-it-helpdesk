from transformers import pipeline  # type: ignore


# Model is not loaded at startup
summarizer = None


def get_summarizer():

    global summarizer

    if summarizer is None:
        summarizer = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6"
        )

    return summarizer


def summarize_ticket(ticket_text):

    model = get_summarizer()

    result = model(
        ticket_text,
        max_length=50,
        min_length=10,
        do_sample=False
    )

    return result[0]["summary_text"]


# Test the summarizer
if __name__ == "__main__":

    ticket = """
    My laptop has been disconnecting from the office Wi-Fi
    frequently since yesterday. I restarted both my laptop
    and the router, but the problem continues. I am unable
    to access internal company applications.
    """

    summary = summarize_ticket(ticket)

    print("Original Ticket:")
    print(ticket)

    print("\nAI Summary:")
    print(summary)