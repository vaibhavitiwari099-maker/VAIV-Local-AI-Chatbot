import random
import json
import os

responses = {
    "hello": [
        "Hey! 👋",
        "Hello! How can I help you?",
        "Hi there! 😊"
    ],

    "how_are_you": [
        "I'm doing great! Thanks for asking.",
        "I'm good! Ready to chat with you. 🤖"
    ],

    "name": [
        "I'm your AI chatbot!",
        "You can call me ChatBot. 🤖"
    ],

    "help": [
        "Sure! Tell me what you need help with.",
        "Of course! What can I help you with?"
    ]
}

MEMORY_FILE = "memory.json"


# Load previous conversation
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)

    return []


# Save conversation
def save_memory(history):
    with open(MEMORY_FILE, "w") as file:
        json.dump(history, file, indent=4)


conversation_history = load_memory()


def get_response(user_input):
    text = user_input.lower()

    if "hello" in text or "hi" in text or "hey" in text:
        return random.choice(responses["hello"])

    elif "how are you" in text:
        return random.choice(responses["how_are_you"])

    elif "your name" in text or "who are you" in text:
        return random.choice(responses["name"])

    elif "help" in text:
        return random.choice(responses["help"])

    elif "what did i say" in text:
        if conversation_history:
            return "You said: " + conversation_history[-1]["user"]
        return "You haven't said anything yet."

    elif "bye" in text or "goodbye" in text:
        return "Goodbye! 👋"

    else:
        return "I'm still learning. I don't understand that yet."


print("🤖 AI Chatbot Started!")
print("Type 'history' to see memory.")
print("Type 'bye' to exit.\n")


while True:

    user_input = input("You: ")

    if user_input.lower() == "history":

        print("\n📜 Conversation History:")

        if not conversation_history:
            print("No conversation yet.")
        else:
            for chat in conversation_history:
                print("You:", chat["user"])
                print("Bot:", chat["bot"])

        print()
        continue

    response = get_response(user_input)

    print("Bot:", response)

    conversation_history.append({
        "user": user_input,
        "bot": response
    })

    save_memory(conversation_history)

    if "bye" in user_input.lower() or "goodbye" in user_input.lower():
        break