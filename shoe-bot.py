import logging
import os

from flask import Flask, request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, ContextTypes, filters

# Flask አፕሊኬሽን መክፈቻ
app_flask = Flask(__name__)
PORT = int(os.environ.get("PORT", "10000"))
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ሎጊንግ ማስተካከል
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# የውይይት ደረጃዎች (Conversation States)
(
    MENU,
    GALLERY,
    SELECT_SIZE,
    SELECT_QTY,
    GET_PHONE,
    GET_ADDRESS,
    SELECT_PAYMENT,
    GET_RECEIPT,
) = range(8)


# 1. /start ትዕዛዝ እና ዋናው ሜኑ (Step 1)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    welcome_text = (
        f"ሰላም {user.first_name}! 👋✨\n"
        "እንኳን ወደ [የጫማ ብራንዱ ስም] የመስመር ላይ ሱቅ በደህና መጡ! 👟\n\n"
        "የእርስዎን ስታይል የሚገልጹ ጥራት ያላቸው ጫማዎችን በጥሩ ዋጋ ያግኙ።\n"
        "ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
    )

    keyboard = [
        [InlineKeyboardButton("👟 ጫማዎችን ይመልከቱ", callback_data="view_shoes")],
        [InlineKeyboardButton("📐 የሳይዝ መለኪያ Guide", callback_data="size_guide")],
        [InlineKeyboardButton("⭐️ የደንበኞች ምስክርነት", callback_data="reviews")],
        [InlineKeyboardButton("📍 አድራሻ እና ስልክ", callback_data="location")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.answer()
        # መልእክት ሳያጠፋ አዲስ መልእክት ይልካል
        await update.callback_query.message.reply_text(welcome_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    return MENU
@app_flask.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "OK", 200

@app_flask.route("/")
def index():
    return "Shoe Bot is alive and running!"


# 2. የጫማ ማሳያ ጋለሪ (Step 2)
async def view_shoes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    caption = (
        "<b>Nike Air Jordan 4 Retro</b> 👟\n\n"
        "💵 <b>ዋጋ፦</b> 3,900 ETB\n"
        "📐 <b>አቫይለብል Size፦</b> 40, 41, 42, 43, 44\n"
        "🎨 <b>Color:</b> White / Black\n"
        "🆔 <b>Product Code:</b> #SH-102"
    )

    keyboard = [
        [InlineKeyboardButton("🛒 አሁኑኑ ይዘዙ", callback_data="order_now")],
        [InlineKeyboardButton("🔙 ወደ ዋና ሜኑ", callback_data="back_to_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # ፎቶ ከመላክ ይልቅ በጽሁፍ መልክ ይልካል
    await query.message.reply_text(
        caption,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
    return GALLERY

# 3. ሳይዝ መምረጫ (Step 3 - Part A)
async def select_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("40", callback_data="size_40"),
            InlineKeyboardButton("41", callback_data="size_41"),
            InlineKeyboardButton("42", callback_data="size_42"),
        ],
        [
            InlineKeyboardButton("43", callback_data="size_43"),
            InlineKeyboardButton("44", callback_data="size_44"),
        ],
        [InlineKeyboardButton("🔙 ተመለስ", callback_data="view_shoes")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        "እባክዎን የሚፈልጉትን <b>የጫማ ሳይዝ (Size)</b> ይምረጡ፦",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
    return SELECT_SIZE


# 4. ብዛት መምረጫ (Step 3 - Part B)
async def select_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    size = query.data.split("_")[1]
    context.user_data["selected_size"] = size

    keyboard = [
        [
            InlineKeyboardButton("1 ጥንድ", callback_data="qty_1"),
            InlineKeyboardButton("2 ጥንድ", callback_data="qty_2"),
            InlineKeyboardButton("3+ ጥንድ", callback_data="qty_3"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        f"መረጡት ሳይዝ፦ <b>{size}</b>\nስንት ጥንድ መገዛት ይፈልጋሉ?",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
    return SELECT_QTY


# 5. ስልክ ቁጥር መጠየቂያ (Step 4 - Form 1)
async def request_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    qty = query.data.split("_")[1]
    context.user_data["selected_qty"] = qty

    contact_button = KeyboardButton(
        text="📱 ስልክ ቁጥር አጋራ (Share Contact)", request_contact=True
    )
    reply_markup = ReplyKeyboardMarkup(
        [[contact_button]], one_time_keyboard=True, resize_keyboard=True
    )

    await query.message.reply_text(
        "ትዕዛዝዎን ለመከታተል እባክዎን ከታች ያለውን አዝራር በመጫን ስልክ ቁጥርዎን ያጋሩን፦",
        reply_markup=reply_markup,
    )
    return GET_PHONE


# 6. አድራሻ መጠየቂያ (Step 4 - Form 2)
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    contact = update.message.contact
    if contact:
        context.user_data["phone"] = contact.phone_number
    else:
        context.user_data["phone"] = update.message.text

    await update.message.reply_text(
        "📍 ጫማው የሚላክበትን <b>አድራሻ/ሰፈር</b> በጽሁፍ ይላኩልን (ለምሳሌ፦ ቦሌ፣ መድኃኔዓለም ህንፃ አጠገብ)፦",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    return GET_ADDRESS


# 7. የክፍያ አማራጭ መምረጫ (Step 4 - Form 3)
async def select_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["address"] = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("📱 Telebirr", callback_data="pay_telebirr"),
            InlineKeyboardButton("🏦 CBE (ንግድ ባንክ)", callback_data="pay_cbe"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "💳 ክፍያ የሚፈጽሙበትን ባንክ/አማራጭ ይምረጡ፦", reply_markup=reply_markup
    )
    return SELECT_PAYMENT


# 8. የባንክ ዝርዝር ማሳያ እና የደረሰኝ ጥያቄ (Step 4 - Final)
async def request_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    payment_method = query.data

    if payment_method == "pay_telebirr":
        pay_info = (
            "📱 <b>Telebirr ቁጥር፦</b> 0911XXXXXX\n"
            "👤 <b>ስም፦</b> [የሱቁ ስም]\n"
            "💵 <b>መጠን፦</b> 3,900 ETB"
        )
    else:
        pay_info = (
            "🏦 <b>ንግድ ባንክ (CBE)፦</b> 1000XXXXXXXXX\n"
            "👤 <b>ስም፦</b> [የሱቁ ስም]\n"
            "💵 <b>መጠን፦</b> 3,900 ETB"
        )

    text = (
        f"ተጨማሪ መረጃ፦\n{pay_info}\n\n"
        "🧾 <b>መጨረሻ፦</b> ክፍያ ፈጽመው ሲጨርሱ <b>የደረሰኙን ፎቶ (Screenshot)</b> እዚህ ይላኩልን።"
    )
    await query.message.reply_text(text, parse_mode="HTML")
    return GET_RECEIPT


# 9. የክፍያ ማረጋገጫ እና ትዕዛዝ ማጠናቀቂያ (Step 5)
async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user

    confirmation_text = (
        f"እናመሰግናለን <b>{user.first_name}</b>! 👟🙏\n"
        "የክፍያ ደረሰኝዎ ደርሶናል።\n\n"
        "⏳ <b>ሂደት፦</b> የክፍያ መረጃዎን አረጋግጠን በ <b>15-30 ደቂቃ</b> ውስጥ እንደውልልዎታለን።\n"
        "🚚 <b>ዴሊቨሪ፦</b> ትዕዛዝዎ እንደተረጋገጠ በ 24 ሰዓት ውስጥ ባሉበት አድራሻ እናደርሳለን!\n\n"
        "📞 ለተጨማሪ ጥያቄ፦ 0911-XX-XX-XX"
    )

    keyboard = [
        [InlineKeyboardButton("🏠 ወደ ዋና ሜኑ መመለስ", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        confirmation_text, parse_mode="HTML", reply_markup=reply_markup
    )
    return MENU


# ተጨማሪ አጋዥ ገጾች (Size Guide, Location, Reviews)
async def size_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "📐 <b>ትክክለኛ የጫማ ሳይዝዎን ለማወቅ፦</b>\n"
        "• 40 Size: 25 cm (የእግር ርዝመት)\n"
        "• 41 Size: 26 cm\n"
        "• 42 Size: 26.5 cm\n"
        "• 43 Size: 27.5 cm\n"
        "• 44 Size: 28 cm\n\n"
        "💡 <b>ምክር፦</b> ጫማው ጠበብ የሚያደርግ ከሆነ ከለመዱት 1 ሳይዝ ከፍ አድርገው ቢያዙ ይመረጣል።"
    )
    keyboard = [
        [InlineKeyboardButton("👟 ጫማዎችን ይመልከቱ", callback_data="view_shoes")],
        [InlineKeyboardButton("🔙 ወደ ዋና ሜኑ", callback_data="back_to_menu")],
    ]
    await query.message.reply_text(
        text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MENU


async def shop_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = (
        "📍 <b>የሱቁ አድራሻ፦</b>\n"
        "🏢 ቦታ፦ አዲስ አበባ፣ 22 ማዞሪያ፣ ሰንሻይን ህንፃ 1ኛ ፎቅ ሱቅ ቁጥር 12\n"
        "📞 ስልክ፦ 0911-XX-XX-XX\n"
        "⏰ የስራ ሰዓት፦ ከሰኞ - እሁድ (ከጠዋቱ 2:30 እስከ ማታ 2:30)\n"
        "🚚 ዴሊቨሪ፦ አዲስ አበባ ውስጥ በራሳችን ሞተር ባሉበት ቦታ እናደርሳለን!"
    )
    keyboard = [
        [InlineKeyboardButton("🔙 ወደ ዋና ሜኑ", callback_data="back_to_menu")]
    ]
    await query.message.reply_text(
        text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("ግዢው ተሰርዟል። /start በመጫን እንደገና መጀመር ይችላሉ።")
    return ConversationHandler.END


def main():
    # የእርስዎን የቦት ቶከን (Bot Token) እዚህ ያስገቡ
    TOKEN = "8686401024:AAHR6jGeCvFuWwgDHlJGODnQ6qQS0IGA470"
    Application.builder()
        application = Application.builder().token(TOKEN).build()
        .connect_timeout(60.0)
        .read_timeout(60.0)
        .write_timeout(60.0)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                CallbackQueryHandler(view_shoes, pattern="^view_shoes$"),
                CallbackQueryHandler(size_guide, pattern="^size_guide$"),
                CallbackQueryHandler(shop_location, pattern="^location$"),
                CallbackQueryHandler(start, pattern="^back_to_menu$"),
            ],
            GALLERY: [
                CallbackQueryHandler(select_size, pattern="^order_now$"),
                CallbackQueryHandler(start, pattern="^back_to_menu$"),
            ],
            SELECT_SIZE: [
                CallbackQueryHandler(select_quantity, pattern="^size_"),
                CallbackQueryHandler(view_shoes, pattern="^view_shoes$"),
            ],
            SELECT_QTY: [CallbackQueryHandler(request_phone, pattern="^qty_")],
            GET_PHONE: [
                MessageHandler(filters.CONTACT | filters.TEXT & ~filters.COMMAND, get_address)
            ],
            GET_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_payment)
            ],
            SELECT_PAYMENT: [
                CallbackQueryHandler(request_receipt, pattern="^pay_")
            ],
            GET_RECEIPT: [
                MessageHandler(filters.PHOTO, confirm_order),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    application.add_handler(conv_handler)
   if __name__ == "__main__":
    application.initialize()
    application.bot.set_webhook(url="https://shoe-telegram-bot.onrender.com/8686401024:AAHR6jGeCvFuWwgDHlJGODnQ6qQS0IGA470")
    app_flask.run(host="0.0.0.0", port=PORT)
