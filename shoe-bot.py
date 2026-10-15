import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application

TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", "10000"))

app_flask = Flask(__name__)
application = Application.builder().token(TOKEN).connect_timeout(60.0).read_timeout(60.0).write_timeout(60.0).build()

@app_flask.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, application.bot)
    application.update_queue.put(update)
    return "OK", 200

@app_flask.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app_flask.run(host="0.0.0.0", port=PORT)
