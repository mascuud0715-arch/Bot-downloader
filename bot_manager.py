import telebot
import threading
import requests

from database import add_bot, add_user_bot
from config import ADMIN_ID

# Store running bots (RAM)
running_bots = {}

# =========================
# 🔍 CHECK TOKEN (BotFather API)
# =========================

def validate_token(token):
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
# 🚀 START USER BOT
# =========================

def start_user_bot(token, owner_id):
    if token in running_bots:
        return

    try:
        bot = telebot.TeleBot(token)

        # =========================
        # 🏁 START COMMAND (USER BOT)
        # =========================
        @bot.message_handler(commands=['start'])
        def start(msg):
            bot.send_message(
                msg.chat.id,
                "🤖 Kusoo dhawoow bot-kaaga!\n\n"
                "Isticmaal si aad u download garayso 🎬🖼️"
            )

        # =========================
        # 📥 SAMPLE DOWNLOAD TRACK
        # =========================
        @bot.message_handler(content_types=['text'])
        def track_usage(msg):
            # Placeholder (stats file later)
            pass

        # Run bot in thread
        t = threading.Thread(target=bot.infinity_polling)
        t.start()

        running_bots[token] = bot

        print(f"✅ Bot started: {token}")

    except Exception as e:
        print(f"❌ Error starting bot: {e}")

# =========================
# ➕ CREATE NEW BOT
# =========================

def create_bot_system(user_id, token):
    valid, username = validate_token(token)

    if not valid:
        return False, "❌ Token-ka sax ma aha!"

    # Save to DB
    add_bot(user_id, token, username)
    add_user_bot(user_id, token)

    # Start bot
    start_user_bot(token, user_id)

    return True, f"✅ Bot waa la abuuray: @{username}"

# =========================
# ❌ STOP BOT
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
# 🔄 RESTART ALL BOTS
# =========================

def restart_all_bots():
    for token in list(running_bots.keys()):
        stop_bot(token)

    print("♻️ All bots stopped")
