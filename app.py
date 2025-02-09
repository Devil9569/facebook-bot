import os
import time
import threading
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload folder exists

FACEBOOK_API_VERSION = "v17.0"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # File Upload Handling
        for file_key in ["tokennum", "NP", "convo", "time"]:
            if file_key in request.files:
                file = request.files[file_key]
                if file.filename != "":
                    file.save(os.path.join(UPLOAD_FOLDER, file_key + ".txt"))
        
        return "Files Uploaded Successfully! <a href='/'>Go Back</a>"
    
    return render_template("index.html")

def read_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            return [line.strip() for line in file.readlines()]
    return []

def send_messages():
    convo_id = read_file("convo.txt")[0] if read_file("convo.txt") else None
    messages = read_file("NP.txt")
    tokens = read_file("tokennum.txt")
    speed = int(read_file("time.txt")[0]) if read_file("time.txt") else 5

    if not convo_id or not messages or not tokens:
        print("[ERROR] Missing Required Files")
        return

    while True:
        try:
            for i, message in enumerate(messages):
                token = tokens[i % len(tokens)]
                url = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}/t_{convo_id}/"
                params = {"access_token": token, "message": message}
                response = requests.post(url, json=params)

                if response.ok:
                    print(f"[✔] Sent: {message}")
                else:
                    print(f"[x] Failed: {message}")

                time.sleep(speed)
        except Exception as e:
            print(f"[!] Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=send_messages, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
