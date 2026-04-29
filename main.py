import os, asyncio, datetime, threading, time, pygame, edge_tts
import speech_recognition as sr
from flask import Flask, render_template
from flask_socketio import SocketIO
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = Flask(__name__)
socketio = SocketIO(app)
pygame.mixer.init()

def push_ui(msg, msg_type="text"):
    socketio.emit('ui_update', {'msg': msg, 'type': msg_type})

def speak(text):
    push_ui(text, "text")
    temp = "v.mp3"
    async def gen():
        await edge_tts.Communicate(text, "en-GB-RyanNeural", rate='+12%', pitch='-3Hz').save(temp)
    asyncio.run(gen())
    pygame.mixer.music.load(temp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy(): time.sleep(0.1)
    pygame.mixer.music.unload()
    if os.path.exists(temp): os.remove(temp)

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        push_ui("Listening", "status")
        r.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=6)
            return r.recognize_google(audio).lower()
        except: return "none"

def jarvis_brain():
    speak("System active. How may I assist you?")
    while True:
        query = listen()
        if query == "none": continue
        
        if "exit" in query or "shutdown" in query:
            speak("Systems offline. Goodbye.")
            break
            
        push_ui("Processing", "status")
        # PURE ASSISTANT PROMPT
        chat = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are a professional AI assistant. You are helpful, polite, and concise. Do not talk about politics, superheroes, or movies. Focus only on the user's tasks."},
                      {"role": "user", "content": query}]
        )
        speak(chat.choices[0].message.content)

@app.route('/')
def home(): return render_template('index.html')

if __name__ == "__main__":
    threading.Thread(target=jarvis_brain, daemon=True).start()
    socketio.run(app, port=5000, debug=False)