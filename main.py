from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import ollama
import json
import os
import re

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


SYSTEM_PROMPT = """
You are VAIV, a friendly and helpful local AI assistant.

Your name is VAIV.
You run locally on the user's computer using Ollama.

Rules:
- Be helpful, friendly, and natural.
- Give clear and easy-to-understand answers.
- Keep answers reasonably concise unless the user asks for detail.
- Use the conversation history when relevant.
- Use saved memory when it is provided to you.
- Do not falsely claim that you cannot remember information that is provided in your memory.
- If you do not know something, say so honestly.
"""


MEMORY_FILE = "memory.json"


# -----------------------------
# MEMORY FUNCTIONS
# -----------------------------

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

                if isinstance(data, list):
                    return data

        except (json.JSONDecodeError, OSError):
            pass

    return []


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4, ensure_ascii=False)


saved_memory = load_memory()


def remember_user_fact(message):
    """
    Detect a few simple personal facts locally.
    This avoids sending an extra request to Ollama.
    """

    text = message.strip()

    # Favorite color
    match = re.search(
        r"(?:my\s+)?favorite\s+color\s+(?:is|=)\s+(.+)",
        text,
        re.IGNORECASE
    )

    if match:
        color = match.group(1).strip().rstrip(".!?")

        memory = f"User's favorite color is {color}."

        if not any(item.get("memory") == memory for item in saved_memory):
            saved_memory.append({"memory": memory})
            save_memory(saved_memory)

        return

    # User's name
    match = re.search(
        r"(?:my\s+name\s+is|i(?:'m| am)\s+called)\s+(.+)",
        text,
        re.IGNORECASE
    )

    if match:
        name = match.group(1).strip().rstrip(".!?")

        memory = f"User's name is {name}."

        if not any(item.get("memory") == memory for item in saved_memory):
            saved_memory.append({"memory": memory})
            save_memory(saved_memory)

        return


def build_memory_context():

    if not saved_memory:
        return ""

    memory_text = "\n".join(
        f"- {item['memory']}"
        for item in saved_memory
        if "memory" in item
    )

    if not memory_text:
        return ""

    return f"""
Here is information VAIV remembers about the user:

{memory_text}

Use this information only when it is relevant.
"""


# -----------------------------
# CURRENT CONVERSATION
# -----------------------------

conversation_history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


# -----------------------------
# HOME PAGE
# -----------------------------

@app.get("/")
def home():
    return FileResponse("static/index.html")


# -----------------------------
# NEW CHAT
# -----------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        # Check whether the user shared something worth remembering
        remember_user_fact(request.message)

        # Build messages for Ollama
        messages = conversation_history.copy()

        memory_context = build_memory_context()

        if memory_context:
            messages.append({
                "role": "system",
                "content": memory_context
            })

        messages.append({
            "role": "user",
            "content": request.message
        })

        # Ask Ollama
        response = ollama.chat(
            model="llama3.2:3b",
            messages=messages
        )

        bot_message = response["message"]["content"]

        # Save current conversation context
        conversation_history.append({
            "role": "user",
            "content": request.message
        })

        conversation_history.append({
            "role": "assistant",
            "content": bot_message
        })

        return {
            "user": request.message,
            "bot": bot_message
        }

    except Exception as error:

        print("VAIV ERROR:", error)

        return {
            "user": request.message,
            "bot": "⚠️ VAIV is currently unavailable. Please make sure Ollama is running and try again."
        }