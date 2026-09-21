def validate_message(message: str):
    if not message:
        return False, "Message cannot be empty."

    message = message.strip()

    if len(message) > 1000:
        return False, "Message is too long."

    return True, message
