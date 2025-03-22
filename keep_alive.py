from flask import Flask
from threading import Thread
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

app = Flask('')

@app.route('/')
def home():
    return "Hello! I am alive!"

def run():
    try:
        logging.info("Starting Flask server...")
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        logging.error(f"Flask server error: {e}")

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()