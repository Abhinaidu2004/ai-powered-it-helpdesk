import ollama


def generate_solution(ticket, context):

    if not context.strip():
        return {
            "status": "No relevant previous tickets found",
            "solution": "No reliable solution could be generated from previous resolved tickets."
        }

    prompt = f"""
You are an IT Help Desk AI assistant.

Your job is to help resolve IT support tickets.

CURRENT TICKET:
{ticket}

PREVIOUS RESOLVED TICKETS:
{context}

IMPORTANT RULES:

1. Use the previous resolved tickets as your primary source.
2. Do not invent a solution that is unrelated to the available context.
3. If the previous tickets do not provide enough information, clearly say that additional investigation is required.
4. Give practical troubleshooting steps.
5. Keep the response concise and professional.

Return the answer using exactly this structure:

Problem Summary:
<summary>

Recommended Solution:
<solution>

Troubleshooting Steps:
1. <step>
2. <step>
3. <step>

Additional Notes:
<important note if needed>
"""

    response = ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "status": "Solution generated",
        "solution": response["message"]["content"]
    }


if __name__ == "__main__":

    ticket = """
    My laptop cannot connect to the office Wi-Fi.
    I restarted the laptop but the problem still exists.
    """

    context = """
    Ticket ID: 1

    Title:
    Wi-Fi connection failed.

    Resolution:
    Restarted the Wi-Fi adapter and reconnected
    the laptop to the office network.
    """

    result = generate_solution(ticket, context)

    print("\nAI Generated Solution:\n")
    print(result["solution"])