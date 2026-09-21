from app.tools.pii_tools import redact_pii


text = """
My name is Virat Kohli.
My email is virat.kohli18@gmail.com.
My phone number is 9012345678.
I spent 500 on groceries today.
"""

result = redact_pii(text)

print("Original:")
print(text)

print("\nRedacted:")
print(result)
