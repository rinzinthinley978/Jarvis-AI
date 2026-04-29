import os
from dotenv import load_dotenv
from groq import Groq

# Load the secret API key from your .env file
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

def test_jarvis():
    print("Testing Jarvis Brain...")
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": "Hello Jarvis, are you there?"}]
    )
    print("Jarvis says:", completion.choices[0].message.content)

if __name__ == "__main__":
    test_jarvis()