import telebot
import threading
import requests
import yt_dlp
import os

from database import *

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
# 📥 DOWNLOAD FUNCTION
# =========================

def download_media(url):
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except:
        return None

# =========================
# 🤖 START USER BOT
# =========================

def start_user_bot(token, owner_id):
    if token in running_bots:
        return

    bot = telebot.TeleBot(token)

    # =========================
    # 🏁 START
    # =========================
    @bot.message_handler(commands=['start'])
    def start(msg):
        inc_users(token)

        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📥 Download", "📊 Stats")
        markup.row("⚙️ Admin Panel")

        bot.send_message(
            msg.chat.id,
            "🤖 Welcome!\n\n"
            "Send any video or photo link.\n"
            "Supported:\n"
            "• TikTok\n• Instagram\n• X (Twitter)\n• YouTube\n• Facebook\n• Pinterest\n\n"
            "Use Download button to begin.",
            reply_markup=markup
        )

    # =========================
    # 📥 DOWNLOAD MENU
    # =========================
    @bot.message_handler(func=lambda m: m.text == "📥 Download")
    def download_menu(msg):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        markup.row("🔥 ALL")
        markup.row("TikTok + Facebook")
        markup.row("X + Instagram")
        markup.row("YouTube + Snapchat")
        markup.row("Pinterest")

        bot.send_message(msg.chat.id, "Choose mode:", reply_markup=markup)

    # =========================
    # 🎯 MODE SELECT
    # =========================
    user_modes = {}

    @bot.message_handler(func=lambda m: m.text in [
        "🔥 ALL", "TikTok + Facebook",
        "X + Instagram", "YouTube + Snapchat", "Pinterest"
    ])
    def set_mode(msg):
        user_modes[msg.chat.id] = msg.text
        bot.send_message(msg.chat.id, "📩 Send link now:")

    # =========================
    # 🔗 HANDLE LINK
    # =========================
    @bot.message_handler(func=lambda m: m.text.startswith("http"))
    def handle_link(msg):
        bot.send_message(msg.chat.id, "⏳ Downloading...")

        file_path = download_media(msg.text)

        if not file_path:
            bot.send_message(msg.chat.id, "❌ Failed to download.")
            return

        try:
            with open(file_path, "rb") as f:
                bot.send_document(msg.chat.id, f)

            inc_videos(token)

        except:
            bot.send_message(msg.chat.id, "❌ Error sending file.")

        # delete file after send
        try:
            os.remove(file_path)
        except:
            pass

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
            f"📊 Bot Stats\n\n"
            f"👥 Users: {s.get('users',0)}\n"
            f"🎬 Videos: {s.get('videos',0)}\n"
            f"🖼️ Images: {s.get('images',0)}"
        )

        bot.send_message(msg.chat.id, text)

    # =========================
    # ⚙️ OWNER ADMIN PANEL
    # =========================
    @bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
    def admin_panel(msg):
        if msg.from_user.id != owner_id:
            bot.send_message(msg.chat.id, "❌ You are not owner.")
            return

        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📢 Broadcast", "📊 Stats")

        bot.send_message(msg.chat.id, "Owner Panel:", reply_markup=markup)

    # =========================
    # 📢 BROADCAST (OWNER)
    # =========================
    @bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
    def owner_broadcast(msg):
        if msg.from_user.id != owner_id:
            return

        bot.send_message(msg.chat.id, "Send message:")
        bot.register_next_step_handler(msg, send_owner_broadcast)

    def send_owner_broadcast(msg):
        users = users_col.find()

        for u in users:
            try:
                bot.send_message(u["user_id"], msg.text)
            except:
                pass

        bot.send_message(msg.chat.id, "✅ Broadcast sent.")

    # =========================
    # ▶️ RUN BOT
    # =========================
    t = threading.Thread(target=bot.infinity_polling)
    t.start()

    running_bots[token] = bot
    print(f"✅ Bot started: {token}")

# =========================
# ➕ CREATE BOT
# =========================

def create_bot(user_id, token):
    valid, username = check_token(token)

    if not valid:
        return False, "❌ Invalid token"

    add_bot(user_id, token, username)
    add_user_bot(user_id, token)
    add_stats(token)

    start_user_bot(token, user_id)

    return True, f"✅ Bot created: @{username}"

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
# 🔴 STOP ALL
# =========================

def stop_all_bots():
    for token in list(running_bots.keys()):
        stop_bot(token)

# =========================
# 🟢 START ALL
# =========================

def start_all_bots(bots_list):
    for b in bots_list:
        start_user_bot(b["token"], b["owner_id"])
