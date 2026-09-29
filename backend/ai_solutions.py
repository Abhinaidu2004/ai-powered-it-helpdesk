solutions = [
    {
        "keywords": ["wifi", "wi-fi", "network", "internet"],
        "solution": (
            "Check that Wi-Fi is enabled and reconnect to the office network. "
            "Restart the network adapter and try connecting again. "
            "If the problem continues, restart the laptop and check whether "
            "other devices can connect to the same network."
        )
    },
    {
        "keywords": ["password", "login", "account", "locked"],
        "solution": (
            "Verify the username and password. If the account is locked, "
            "contact the IT administrator to unlock the account or reset "
            "the password."
        )
    },
    {
        "keywords": ["printer", "printing", "print"],
        "solution": (
            "Check that the printer is powered on and connected to the network. "
            "Verify that the correct printer is selected and try restarting "
            "the printer and print spooler."
        )
    },
    {
        "keywords": ["laptop", "keyboard", "screen", "overheating"],
        "solution": (
            "Restart the laptop and check for hardware problems. "
            "Make sure the device has proper ventilation and check whether "
            "the keyboard or display is physically damaged."
        )
    },
    {
        "keywords": ["software", "application", "app", "crash", "error"],
        "solution": (
            "Restart the application and check for available updates. "
            "If the problem continues, reinstall the application or contact "
            "the IT support team."
        )
    }
]


def recommend_solution(ticket_text):

    ticket_text = ticket_text.lower()

    best_solution = None
    best_score = 0

    for item in solutions:

        score = 0

        for keyword in item["keywords"]:

            if keyword in ticket_text:
                score += 1

        if score > best_score:
            best_score = score
            best_solution = item["solution"]

    if best_solution is None:
        return "No specific solution found. Please contact the IT support team."

    return best_solution

if __name__ == "__main__":

    ticket = "My laptop cannot connect to office Wi-Fi"

    solution = recommend_solution(ticket)

    print("Ticket:")
    print(ticket)

    print("\nRecommended Solution:")
    print(solution)