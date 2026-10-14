import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# የቴሌግራም ቦት ቶከንዎን እዚህ ያስገቡ
TOKEN = os.getenv("BOT_TOKEN","8686401024:AAFhRDee5Oy8l0nibUOE2p4K8NYtSQmW-cY" )
PORT = int(os.environ.get("PORT", "10000"))

app = Flask(__name__)
bot = Bot(token=TOKEN)

# አፕሊኬሽኑን አስቀድመን እናዘጋጅ
telegram_app = Application.builder().token(TOKEN).updater(None).build()

# ትዕዛዞች (Handlers) እዚህ ይጨመራሉ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! እንኳን ወደ ጫማ ሱቁ በደህና መጡ! 👟")

telegram_app.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    return "Shoe Bot is running smoothly!", 200

if __name__ == "__main__":
    import asyncio
    async def main():
        await telegram_app.initialize()
        # ዌብሁክ ሊንክዎን ከ Render ዩአርኤል ጋር ማያያዝ
        RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
        if RENDER_EXTERNAL_URL:
            await bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{TOKEN}")
        
        app.run(host="0.0.0.0", port=PORT)

    asyncio.run(main())
