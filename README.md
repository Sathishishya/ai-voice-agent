# 🤖 AI Voice Agent (Twilio + OpenAI + ElevenLabs)

This project is a simple **AI-powered voice assistant** you can call on your phone.  

It uses:
- **Twilio** → Handles phone calls + speech input  
- **OpenAI GPT** → Generates AI responses  
- **ElevenLabs** → Converts text-to-speech (TTS)  
- **Flask** → Lightweight Python web server  

---

## 🚀 Features
- AI greets the caller once, then flows naturally  
- Caller speaks → GPT generates a response  
- Response is spoken aloud using ElevenLabs  
- Memory of last few exchanges (context-aware)  
- Works on **macOS** and **Windows**  

---

## ⚙️ Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/YOUR-USERNAME/ai-voice-agent.git
cd ai-voice-agent
2. Create Virtual Environment & Install Dependencies
🖥️ macOS/Linux
bash
Copy code
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
🪟 Windows (PowerShell)
powershell
Copy code
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
3. Configure Environment Variables
Copy .env.example → rename to .env

Fill in your API keys:

ini
Copy code
OPENAI_API_KEY=your-openai-api-key
ELEVEN_API_KEY=your-elevenlabs-api-key
ELEVEN_VOICE_ID=EXAVITQu4vr4xnSDxMaL
⚠️ Never commit .env to GitHub — it’s ignored by .gitignore.

4. Run the Flask Server
macOS/Linux
bash
Copy code
python3 app.py
Windows
powershell
Copy code
python app.py
Server runs at:

cpp
Copy code
http://127.0.0.1:5000
5. Expose Server with Ngrok
Twilio needs a public URL.

macOS/Linux/Windows
bash
Copy code
ngrok http 5000
Copy the HTTPS forwarding URL (e.g. https://abcd1234.ngrok-free.app).

6. Configure Twilio
Go to Twilio Console → Phone Numbers

Select your number

Under Voice & Fax → A Call Comes In, set webhook to:

bash
Copy code
https://abcd1234.ngrok-free.app/voice
Save changes ✅

Now call your Twilio number 📱 and test the AI agent.
