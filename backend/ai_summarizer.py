from transformers import pipeline # type: ignore


# Load summarization model
summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)


def summarize_ticket(ticket_text):

    result = summarizer(
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
    
