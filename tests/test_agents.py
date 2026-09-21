from app.agents.coordinator_agent import coordinator_agent


test_messages = [
    ("I spent 200 on lunch today", "EXPENSE"),
    ("Show my recent expenses", "EXPENSE"),
    ("Set a budget of 5000 for food this month", "BUDGET"),
    ("Am I over budget?", "BUDGET"),
    ("How can I save money?", "INSIGHTS"),
    ("What is the 50/30/20 rule?", "INSIGHTS"),
]

print("Testing Coordinator Agent routing:\n")

for message, expected in test_messages:
    result = coordinator_agent(message)
    status = "PASS" if expected in result else "FAIL"
    print(f"[{status}] \"{message}\"")
    print(f"  Expected: {expected} | Got: {result}\n")
