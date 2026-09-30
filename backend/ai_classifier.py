from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


# Training data
tickets = [
    "Wi-Fi is not working",
    "Cannot connect to office network",
    "Internet connection is slow",
    "Network keeps disconnecting",

    "Laptop screen is broken",
    "Keyboard is not working",
    "Laptop is overheating",
    "Computer will not turn on",

    "Microsoft Word is not opening",
    "Application keeps crashing",
    "Software installation failed",
    "Excel is showing an error",

    "I forgot my password",
    "Cannot login to my account",
    "Account is locked",
    "Unable to access my account"
]


# Category labels
categories = [
    "Network",
    "Network",
    "Network",
    "Network",

    "Hardware",
    "Hardware",
    "Hardware",
    "Hardware",

    "Software",
    "Software",
    "Software",
    "Software",

    "Account",
    "Account",
    "Account",
    "Account"
]


# Priority labels
priorities = [
    "High",
    "High",
    "Medium",
    "Medium",

    "High",
    "Medium",
    "High",
    "High",

    "Medium",
    "Medium",
    "Low",
    "Medium",

    "High",
    "High",
    "High"
]


# Models are not created at startup
vectorizer = None
category_model = None
priority_model = None


def get_models():

    global vectorizer
    global category_model
    global priority_model

    if vectorizer is None:

        vectorizer = TfidfVectorizer()

        X = vectorizer.fit_transform(tickets)

        category_model = LogisticRegression()
        category_model.fit(X, categories)

        priority_model = LogisticRegression()
        priority_model.fit(X, priorities)

    return vectorizer, category_model, priority_model


# Prediction function
def predict_ticket(ticket_text):

    vectorizer, category_model, priority_model = get_models()

    ticket_vector = vectorizer.transform([ticket_text])

    category = category_model.predict(ticket_vector)[0]

    priority = priority_model.predict(ticket_vector)[0]

    return category, priority


# Test the AI
if __name__ == "__main__":

    test_ticket = "My laptop cannot connect to Wi-Fi"

    category, priority = predict_ticket(test_ticket)

    print("Ticket:", test_ticket)
    print("Predicted Category:", category)
    print("Predicted Priority:", priority)