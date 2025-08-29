import os
import uuid
import requests
from flask import Flask, request, Response, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI
from dotenv import load_dotenv
from collections import deque

app = Flask(__name__)
load_dotenv()

# API Keys
OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # Default voice

# Directory for generated TTS files
OUTPUT_DIR = "static"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Conversation memory (keep last 6 exchanges max)
conversation_history = deque(maxlen=6)

@app.route("/voice", methods=["POST"])
def voice():
    print("➡️ /voice called")
    print("Headers:", dict(request.headers))
    print("Form:", request.form.to_dict())

    # Reset memory for each new call
    conversation_history.clear()

    vr = VoiceResponse()
    vr.say("Hello! I am your AI agent. Please say something after the beep.")

    gather = Gather(
        input="speech",
        action="/process_speech",
        method="POST",
        timeout=5,
        speechTimeout="auto",
        finishOnKey="*"
    )
    vr.append(gather)

    vr.say("I didn't catch that. Goodbye.")
    return Response(str(vr), content_type="text/xml")

@app.route("/process_speech", methods=["POST"])
def process_speech():
    user_text = request.form.get("SpeechResult")
    print(f"👂 User said (raw transcript): {user_text}")

    if user_text:
        # Add user message to memory
        conversation_history.append({"role": "user", "content": user_text})

        # 1. Build GPT messages with memory
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful AI voice assistant on a phone call. "
                    "The user’s speech may be messy or incomplete, so interpret carefully. "
                    "Always stay on the user’s topic and avoid changing the subject. "
                    "If unclear, ask politely for clarification. "
                    "Respond in short, natural spoken sentences (10–15 words)."
                )
            }
        ]
        messages.extend(list(conversation_history))

        # 2. Get GPT reply
        resp = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        gpt_reply = resp.choices[0].message.content.strip()
        print(f"🤖 GPT reply: {gpt_reply}")

        # Add GPT reply to memory
        conversation_history.append({"role": "assistant", "content": gpt_reply})

        # 3. Send GPT reply to ElevenLabs TTS
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
        headers = {"xi-api-key": ELEVEN_API_KEY, "Content-Type": "application/json"}
        payload = {
            "text": gpt_reply,
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
        }

        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            print("❌ ElevenLabs error:", r.text)
            vr = VoiceResponse()
            vr.say("Sorry, there was an error generating audio.")
            return Response(str(vr), content_type="text/xml")

        # 4. Save TTS audio
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(r.content)

        base_url = request.url_root.rstrip("/")
        audio_url = f"{base_url}/static/{filename}"
        print(f"🔊 Generated TTS file: {audio_url}")

        # 5. Play reply + new Gather
        vr = VoiceResponse()
        vr.play(audio_url)

        gather = Gather(
            input="speech",
            action="/process_speech",
            method="POST",
            timeout=5,
            speechTimeout="auto",
            finishOnKey="*"
        )
        vr.append(gather)

        vr.say("I didn't catch that. Goodbye.")

        print("➡️ Returning TwiML with <Play> + <Gather>")
        print(str(vr))

        return Response(str(vr), content_type="text/xml")

    # If no speech
    vr = VoiceResponse()
    vr.say("Sorry, I didn't hear anything. Goodbye.")
    return Response(str(vr), content_type="text/xml")

# Serve static TTS audio
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route("/", methods=["GET"])
def index():
    return "✅ Flask AI Voice Agent is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
