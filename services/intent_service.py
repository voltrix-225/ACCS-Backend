import json
import re
from fastapi import HTTPException

from models.response_models import IntentResponse
from services.llm_service import classify_intent, call_llm_text, generate_chat_response
from services.datetime_parser import parse_natural_datetime


def extract_json(text: str) -> str:
    """
    Extract JSON block from LLM response.
    """

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise HTTPException(
            status_code=500,
            detail="No JSON found in LLM response"
        )

    return match.group(0)



def generate_email_body(command: str) -> str:

    prompt = f"""
Write a professional email based on the following request:

{command}

Requirements:
- Minimum 3 sentences
- Include greeting (e.g., Hi John)
- Include clear body
- Include closing (e.g., Regards)
- Keep it concise and professional
- DO NOT RETURN JSON
- Do not include action/parameters

Return ONLY the email body text.
"""

    response = call_llm_text(prompt)  # or your LLM call
    return response.strip()

def normalize_intent(data, command):

    intent = IntentResponse(
        action=data["action"],
        parameters=data.get("parameters", {}),
        confidence=float(data.get("confidence", 0.8))
    )

    # ---------------------------
    # SMS VALIDATION
    # ---------------------------

    if intent.action == "SEND_SMS":

        missing = []

        if not intent.parameters.get("contact_name"):
            missing.append("contact_name")

        if not intent.parameters.get("message"):
            missing.append("message")

        if missing:
            intent.requires_input = True
            intent.missing_fields = missing


# ---------------------------
# EMAIL VALIDATION (UPDATED)
# ---------------------------
# ---------------------------
# EMAIL HANDLER (FINAL - LLM ONLY)
# ---------------------------

    if intent.action == "SEND_EMAIL":

        import re

        missing = []

        # ---------------------------
        # EXTRACT / CLEAN PARAMETERS
        # ---------------------------

        recipient = intent.parameters.get("recipient", "").strip()
        subject = intent.parameters.get("subject", "").strip()

        # ---------------------------
        # FORCE EMAIL EXTRACTION (CRITICAL)
        # ---------------------------

        if not recipient:
            match = re.search(r'[\w\.-]+@[\w\.-]+', command)
            if match:
                recipient = match.group(0)

        # fallback → extract name after "email"
        if not recipient:
            words = command.lower().split()
            if "email" in words:
                idx = words.index("email")
                if idx + 1 < len(words):
                    recipient = words[idx + 1]

        # ---------------------------
        # SUBJECT FALLBACK
        # ---------------------------

        if not subject:
            if "about" in command.lower():
                subject = command.lower().split("about", 1)[1].strip().title()
            else:
                subject = "Regarding Your Request"

        # ---------------------------
        # GENERATE MESSAGE (ALWAYS)
        # ---------------------------

        try:
            message = generate_email_body(command)
        except Exception as e:
            print("EMAIL GEN ERROR:", str(e))
            message = "Hello,\n\nThis is regarding your request.\n\nRegards."

        # ---------------------------
        # ASSIGN FINAL VALUES
        # ---------------------------

        intent.parameters = {
            "recipient": recipient,
            "subject": subject,
            "message": message
        }

        # ---------------------------
        # VALIDATION
        # ---------------------------

        if not recipient:
            missing.append("recipient")

        if not subject:
            missing.append("subject")

        if missing:
            intent.requires_input = True
            intent.missing_fields = missing
        # ---------------------------
    # REMINDER FIX
    # ---------------------------
    if intent.action == "SET_REMINDER":

        params = intent.parameters

        # normalize keys
        if "note" in params:
            params["reminder_content"] = params.pop("note")

        if "time" in params:
            params["reminder_time"] = params.pop("time")

        if "date" in params:
            params["reminder_date"] = params.pop("date")

        if "reminder_text" in params:
            params["reminder_content"] = params.pop("reminder_text")

        parsed = parse_natural_datetime(command)

        raw_date = params.get("reminder_date", "").lower()

        if not raw_date or raw_date in ["today", "tomorrow"]:
            params["reminder_date"] = parsed["reminder_date"]

        if not params.get("reminder_time"):
            params["reminder_time"] = parsed["reminder_time"]

        missing = []

        if not params.get("reminder_content"):
            missing.append("reminder_content")

        if not params.get("reminder_date"):
            missing.append("reminder_date")

        if not params.get("reminder_time"):
            missing.append("reminder_time")

        if missing:
            intent.requires_input = True
            intent.missing_fields = missing

    #----------------------------
    # GENERAL CHAT
        #----------------------------
    if intent.action == "GENERAL_CHAT":

        if not intent.parameters.get("response"):
            intent.parameters["response"] = generate_chat_response(command)

    # ---------------------------
    # CONFIDENCE CONTROL
    # ---------------------------
    if intent.confidence < 0.5:
        raise HTTPException(
            status_code=400,
            detail="Low confidence"
        )

    if intent.confidence < 0.75:
        intent.requires_confirmation = True

    return intent


def parse_command(command: str):

    raw_output = classify_intent(command)

    try:
        json_str = extract_json(raw_output)
        data = json.loads(json_str)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Invalid JSON from LLM"
        )

    # 🔥 STRICT VALIDATION
    if "action" not in data:
        raise HTTPException(
            status_code=500,
            detail="No action returned by LLM"
        )

    intent = normalize_intent(data, command)

    return intent