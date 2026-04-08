from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPT


load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

client = InferenceClient(
    model="Qwen/Qwen2.5-7B-Instruct",
    token=HF_API_KEY
)



def classify_intent(command: str) -> str:
    command = command.lower()

    system_prompt = SYSTEM_PROMPT

    if any(x in command for x in ["email", "mail", "gmail"]):
        user_prompt = f"""
User command:
{command}

You are an intent classification system.

Return ONLY valid JSON.

---

If the command contains "email" or "mail", action MUST be "SEND_EMAIL".

---

Extract parameters:

- recipient:
  Extract the name after:
  - "to"
  - OR directly after "email"
  - IF NO NAME IS CLEAR, JUST ADDRESS AS Sir/Ma'am
  
  Examples:
  "email laks" → "laks"
  "email to john" → "john"

- subject:
  Generate a short subject from context
  Example: "run sleep discussion"

- message:
  Leave empty ("") unless user clearly provides full message

- use_llm:
  - If user says "professional", "draft", "write" → true
  - If user says "send as is", "raw" → false
  - Otherwise → null

---

Rules:

- NEVER return empty parameters
- ALWAYS extract recipient if possible
- ALWAYS generate a subject
- DO NOT return UNKNOWN for email commands

---

Example:

Input: email laks about the run sleep, make it professional

Output:
{{
  "action": "SEND_EMAIL",
"parameters": {{ 
    "recipient": "laks",
    "subject": "Run Sleep Discussion",
    "message": "",
    "use_llm": true
  }},
  "confidence": 0.95
}}

---

Return ONLY JSON.
"""
    else:
        user_prompt = command

    response = client.chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=250,
        temperature=0.1,
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def call_llm_text(prompt: str, temperature: float = 0.7, max_tokens: int = 300) -> str:
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You generate natural human-like responses."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )

    output = response.choices[0].message.content.strip()
    print("LLM:", output)

    return output

def is_complex_query(command: str) -> bool:
    keywords = [
        "explain", "why", "how", "describe",
        "tell me about", "what is", "difference",
        "guide", "details"
    ]
    return any(k in command.lower() for k in keywords)


def summarize_notifications(client, text: str) -> str:
    prompt = f"""
You are an assistant that summarizes notifications.

Input:
{text}

Instructions:
- Extract only important information
- Ignore spam/promotions
- Keep it short (3–5 bullet points)
- Focus on actionable or important messages

Output format:
- Point 1
- Point 2
- Point 3
"""

    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You summarize notifications."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

chat_memory = []
MAX_MEMORY = 6


def generate_chat_response(command: str) -> str:

    global chat_memory

    # 🧠 store user input
    chat_memory.append({"role": "user", "content": command})
    chat_memory = chat_memory[-MAX_MEMORY:]

    # 🎯 SYSTEM PROMPT
    system_prompt = "You are Kika, a smart, human-like AI assistant."

    if is_complex_query(command):
        system_prompt += """
Give clear, well-explained responses.
Be natural and detailed.
"""
        max_tokens = 800
        temperature = 0.75

    else:
        system_prompt += """
You are Kika, a smart, confident, human-like AI assistant.

You speak naturally, like a real person.
You are concise when needed, and detailed when required.
You NEVER sound robotic.
You adapt your tone based on the user.

Avoid generic answers.
Be specific, helpful, and engaging.
"""
        max_tokens = 400
        temperature = 0.7

    # 🧠 BUILD CHAT CONTEXT
    messages = [{"role": "system", "content": system_prompt}] + chat_memory

    # 🤖 CALL MODEL
    reply = call_llm_text(messages, temperature, max_tokens)

    # 🧠 store response
    chat_memory.append({"role": "assistant", "content": reply})

    return reply

if __name__ == '__main__':
    print(classify_intent("CALL JON"))  