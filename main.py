from fastapi import FastAPI, HTTPException

from models.request_models import UserInput, NotificationRequest
from models.response_models import IntentResponse, ActionType
from services.llm_service import summarize_notifications, client 
from services.intent_service import parse_command


app = FastAPI()


def rule_based_parser(command: str) -> IntentResponse:

    try:

        # -------------------------------
        # 🔥 SPECIFIC APPS FIRST
        # -------------------------------
        if "whatsapp" in command or "wa" in command:
            return IntentResponse(
            action="SEND_WHATSAPP",
            parameters={},
            confidence=0.9,
            requires_input=True,
            missing_fields=["contact_name", "message"]
        )
        if "send email" in command or "write email" in command or "email" in command:
            return IntentResponse(
                action= ActionType.SEND_EMAIL,
                parameters={},
                confidence=0.9,
                requires_input = True,
                missing_fields=["recipient", "subject", "message"]
            )

        if "open gmail" in command:
            return IntentResponse(
                action=ActionType.OPEN_APP,
                parameters={"app_name": "gmail"},
                confidence=0.9
            )
        if "youtube" in command or "yt" in command:
            return IntentResponse(
                action=ActionType.OPEN_APP,
                parameters={"app_name": "youtube"},
                confidence=0.9
            )
        # -------------------------------
        # NOTES
        # -------------------------------

        if "note" in command:
            return IntentResponse(
                action="CREATE_NOTE",
                parameters={"note_content": ""},
                missing_fields=["note_content"],
                requires_input=True,
                confidence=0.7
            )

        if "show notes" in command:
            return IntentResponse(
                action="GET_NOTES",
                parameters={},
                confidence=0.9
            )

        if "search note" in command:
            return IntentResponse(
                action="SEARCH_NOTES",
                parameters={"query": ""},
                missing_fields=["query"],
                requires_input=True,
                confidence=0.7
            )

        # -------------------------------
        # 🎧 SPOTIFY (specific before generic)
        # -------------------------------
        if "playlist" in command:
            return IntentResponse(
                action=ActionType.SPOTIFY_PLAY_PLAYLIST,
                parameters={
                    "spotify_id": "placeholder",
                    "playlist_name": "playlist_name",
                    "play_type": "shuffle"
                },
                confidence=0.7
            )

        if "next" in command:
            return IntentResponse(
                action=ActionType.SPOTIFY_NEXT,
                parameters={"spotify_id": "placeholder"},
                confidence=0.7
            )

        if "previous" in command:
            return IntentResponse(
                action=ActionType.SPOTIFY_PREVIOUS,
                parameters={"spotify_id": "placeholder"},
                confidence=0.7
            )

        if "pause" in command:
            return IntentResponse(
                action=ActionType.SPOTIFY_PAUSE,
                parameters={"spotify_id": "placeholder"},
                confidence=0.7
            )

        if "play" in command:
            return IntentResponse(
                action=ActionType.SPOTIFY_PLAY,
                parameters={
                    "spotify_id": "placeholder",
                    "song_name": "unknown"
                },
                confidence=0.7
            )

        # -------------------------------
        # 📱 COMMUNICATION
        # -------------------------------
        if "sms" in command or "message" in command:
            return IntentResponse(
                action=ActionType.SEND_SMS,
                parameters={},
                confidence=0.9,
                requires_input=True,
                missing_fields=["contact_name", "message"]
            )
        
        if "call" in command:
            return IntentResponse(
                action=ActionType.MAKE_CALL,
                parameters={},
                confidence=0.9,
                missing_fields=["contact_name"],
                requires_input=True
            )

        # -------------------------------
        # 🧠 PRODUCTIVITY
        # -------------------------------
        if "reminder" in command:
            return IntentResponse(
                action=ActionType.SET_REMINDER,
                parameters={
                    "reminder_content": "",
                    "reminder_date": "",
                    "reminder_time": ""
                },
                missing_fields=["reminder_content","reminder_date", "reminder_time"],
                confidence=0.7
            )


        # -------------------------------
        # 🌐 URL
        # -------------------------------
        if ".com" in command or "dot com" in command:
            return IntentResponse(
                action=ActionType.OPEN_URL,
                parameters={"website": "placeholder.com"},
                confidence=0.7
            )
        # -------------------------------
        # SYSTEM INTENTS
        # -------------------------------

        if "flashlight on" in command or " on flashlight" in command or "lumos" in command:
            return IntentResponse(
                action="FLASHLIGHT_ON", 
                parameters={}, 
                confidence=0.9
            )

        if "flashlight off" in command or " off flashlight" in command or "knox" in command:    
            return IntentResponse(
                action="FLASHLIGHT_OFF", 
                parameters={}, 
                confidence=0.9
            )

        if "increase volume" in command or "volume up" in command:
            return IntentResponse(
                action="VOLUME_UP",
                parameters={},
                confidence=0.9
            )

        if "decrease volume" in command or "volume down" in command:
            return IntentResponse(
                action="VOLUME_DOWN",
                parameters={},
                confidence=0.9
            )


        if "max volume" in command or "full volume" in command:
            return IntentResponse(
                action="VOLUME_MAX", 
                parameters={}, 
                confidence=0.9
                )

        if "mute" in command or "min volume" in command:
            return IntentResponse(
                action="VOLUME_MIN", 
                parameters={}, 
                confidence=0.9
                )

        if "wifi" in command:
            return IntentResponse(
                action="OPEN_SETTINGS",
                parameters={"setting": "wifi"},
                confidence=0.8
            )

        if "bluetooth" in command:
            return IntentResponse(
                action="OPEN_SETTINGS",
                parameters={"setting": "bluetooth"},
                confidence=0.8
            )    
        if "display" in command:
            return IntentResponse(
                action="OPEN_SETTINGS",
                parameters={"setting": "display"},
                confidence=0.8
            )   


        # -------------------------------
        # 🔴 GENERIC (LAST)
        # -------------------------------
        if command.startswith("open"):
            return IntentResponse(
                action=ActionType.OPEN_APP,
                parameters={"app_name": command.replace("open", "").replace("the","").replace("app","").strip()},
                confidence=0.6
            )

        if "notification" in command:

            return IntentResponse(
                action="READ_NOTIFICATIONS",
                parameters={"app": "unknown"},
                confidence=0.7
            )
        
        if "summarize notifications" in command or "important notifications" in command:
            return IntentResponse(
                action="SUMMARIZE_NOTIFICATIONS",
                parameters={},
                confidence=0.9
            )
        
    except Exception as e:
        print("FALLBACK ERROR:", str(e))

        return IntentResponse(
        action="UNKNOWN",
        parameters={},
        confidence=0.3,
        requires_confirmation=True
    )
# -------------------------------
# Main Endpoint
# -------------------------------

@app.post("/summarize-notifications")
def summarize_notifications_api(req: NotificationRequest):
    print("endpoint hit")    
    try:
        summary = summarize_notifications(client, req.text)

        return {
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Summarization failed: {str(e)}"
        )
@app.post("/parse-intent")
def parse_intent(user_input: UserInput):

    print("endpoint hit")

    command = user_input.user_command

    try:
        intent = parse_command(command)  # now returns SINGLE intent

        # 🔥 MAKE_CALL FIX
        if intent.action == "MAKE_CALL":
            if not intent.parameters.get("contact_name"):
                intent.parameters = {}
                intent.missing_fields = ["contact_name"]
                intent.requires_input = True

        # 🔥 SEND_SMS FIX
        if intent.action == "SEND_SMS":
            missing = []

            if not intent.parameters.get("contact_name"):
                missing.append("contact_name")

            if not intent.parameters.get("message"):
                missing.append("message")

            if missing:
                intent.parameters = {}
                intent.missing_fields = missing
                intent.requires_input = True

        return intent

    except Exception as e:
        print("LLM failed:", str(e))
        import traceback
        traceback.print_exc()

        fallback = rule_based_parser(command)

        if fallback is None:
            return {
                "action": "UNKNOWN",
                "parameters": {},
                "confidence": 0.0,
                "requires_input": False,
                "missing_fields": []
            }

        return fallback