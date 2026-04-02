import telebot
import threading
import requests

from database import add_bot, add_user_bot, add_stats, inc_users, inc_videos, inc_images, get_stats
from config import MAX_BOTS_PER_USER

# Running bots (RAM)
running_bots = {}

# =========================
# 🔍 CHECK TOKEN
# =========================

def check_token(token):
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        res = requests.get(url).json()

        if res.get("ok"):
            return True, res["result"]["username"]
        else:
            return False, None
    except:
        return False, None

# =========================
# 🤖 START USER BOT
# =========================

def start_user_bot(token, owner_id):
    if token in running_bots:
        return

    try:
        bot = telebot.TeleBot(token)

        # =========================
        # 🏁 START
        # =========================
        @bot.message_handler(commands=['start'])
        def start(msg):
            inc_users(token)

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("🎬 Download Video", "🖼️ Download Image")
            markup.row("📊 Stats")

            bot.send_message(
                msg.chat.id,
                "🤖 Kusoo dhawoow bot-kaaga!",
                reply_markup=markup
            )

        # =========================
        # 🎬 VIDEO (FAKE TRACK)
        # =========================
        @bot.message_handler(func=lambda m: m.text == "🎬 Download Video")
        def video(msg):
            inc_videos(token)
            bot.send_message(msg.chat.id, "📥 Video la diiwaan geliyay!")

        # =========================
        # 🖼️ IMAGE (FAKE TRACK)
        # =========================
        @bot.message_handler(func=lambda m: m.text == "🖼️ Download Image")
        def image(msg):
            inc_images(token)
            bot.send_message(msg.chat.id, "📥 Image la diiwaan geliyay!")

        # =========================
        # 📊 STATS
        # =========================
        @bot.message_handler(func=lambda m: m.text == "📊 Stats")
        def stats(msg):
            s = get_stats(token)

            if not s:
                bot.send_message(msg.chat.id, "No stats yet")
                return

            text = (
                f"📊 Stats Bot\n\n"
                f"👥 Users: {s.get('users',0)}\n"
                f"🎬 Videos: {s.get('videos',0)}\n"
                f"🖼️ Images: {s.get('images',0)}"
            )

            bot.send_message(msg.chat.id, text)

        # Run bot
        t = threading.Thread(target=bot.infinity_polling)
        t.start()

        running_bots[token] = bot
        print(f"✅ Bot started: {token}")

    except Exception as e:
        print(f"❌ Error bot: {e}")

# =========================
# ➕ CREATE BOT
# =========================

def create_bot(user_id, token):
    valid, username = check_token(token)

    if not valid:
        return False, "❌ Token sax ma aha!"

    # Save DB
    add_bot(user_id, token, username)
    add_user_bot(user_id, token)
    add_stats(token)

    # Start bot
    start_user_bot(token, user_id)

    return True, f"✅ Bot waa la sameeyay: @{username}"

# =========================
# 🔴 STOP BOT
# =========================

def stop_bot(token):
    bot = running_bots.get(token)

    if bot:
        try:
            bot.stop_polling()
        except:
            pass

        del running_bots[token]
        return True

    return False

# =========================
# 🟢 START ALL / STOP ALL
# =========================

def stop_all_bots():
    for token in list(running_bots.keys()):
        stop_bot(token)

def start_all_bots(bots_list):
    for b in bots_list:
        start_user_bot(b["token"], b["owner_id"])
