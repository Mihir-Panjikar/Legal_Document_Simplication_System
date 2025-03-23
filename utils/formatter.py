# Function to Format the Input Messages

def format_messages(messages):
    formatted = ""
    for msg in messages:
        formatted += f"{msg['role'].capitalize()}: {msg['content']}\n\n"
    return formatted