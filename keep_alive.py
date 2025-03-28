from flask import Flask
import os

app = Flask(__name__)
port = int(os.getenv("PORT", 8000))  # Use Koyeb's expected port

@app.route('/')
def home():
    return "Bot Alive"

def run():
    app.run(host='0.0.0.0', port=port)  # Critical for Koyeb