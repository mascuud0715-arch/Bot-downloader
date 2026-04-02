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
        res = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
        if res.get("ok"):
            return True, res["result"]["username"]
        return False, None
    except:
        return False, None

# =========================
# 📥 DOWNLOAD
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
# 🔒 FORCE JOIN CHECK (USER BOT)
# =========================
def check_force_join(bot, user_id):
    channels = get_channels()

    for ch in channels:
        try:
            member = bot.get_chat_member(ch["channel_id"], user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False

    return True

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
        user_id = msg.from_user.id

        # Save user (IMPORTANT)
        add_user(user_id)

        # Force Join
        if not check_force_join(bot, user_id):
            bot.send_message(msg.chat.id, "❗ Please join required channels first.")
            return

        inc_users(token)

        bot.send_message(
            msg.chat.id,
            "🤖 Welcome to Downloader Bot!\n\n"
            "Send any link from:\n"
            "TikTok, Instagram, Facebook, X, YouTube, Pinterest\n\n"
            "I will download video/photo for you."
        )

    # =========================
    # 🔗 HANDLE LINKS
    # =========================
    @bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
    def handle_link(msg):
        user_id = msg.from_user.id

        # Force Join
        if not check_force_join(bot, user_id):
            bot.send_message(msg.chat.id, "❗ Join channels first.")
            return

        # Get bot mode
        bot_data = bots.find_one({"token": token})
        mode = bot_data.get("mode", "🔥 ALL")

        url = msg.text.lower()

        # =========================
        # 🎯 MODE FILTER
        # =========================
        if mode != "🔥 ALL":
            if "tiktok" in mode.lower() and "tiktok.com" not in url:
                bot.send_message(msg.chat.id, "❌ Only TikTok allowed.")
                return
            if "facebook" in mode.lower() and "facebook.com" not in url:
                bot.send_message(msg.chat.id, "❌ Only Facebook allowed.")
                return
            if "instagram" in mode.lower() and "instagram.com" not in url:
                bot.send_message(msg.chat.id, "❌ Only Instagram allowed.")
                return
            if "x" in mode.lower() and "twitter.com" not in url:
                bot.send_message(msg.chat.id, "❌ Only X allowed.")
                return

        bot.send_message(msg.chat.id, "⏳ Downloading...")

        file_path = download_media(msg.text)

        if not file_path:
            bot.send_message(msg.chat.id, "❌ Failed.")
            return

        try:
            username = bot.get_me().username

            caption = f"Via: @{username}"

            with open(file_path, "rb") as f:
                bot.send_document(msg.chat.id, f, caption=caption)

            bot.send_message(
                msg.chat.id,
                "Created: @Create_Your_via_downloader_bot"
            )

            inc_videos(token)

        except:
            bot.send_message(msg.chat.id, "❌ Send error")

        try:
            os.remove(file_path)
        except:
            pass

    # =========================
    # ⚙️ OWNER ADMIN PANEL (PRIVATE)
    # =========================
    @bot.message_handler(commands=['admin'])
    def admin_panel(msg):
        if msg.from_user.id != owner_id:
            return

        bot.send_message(
            msg.chat.id,
            "⚙️ Owner Panel\n\n"
            "/broadcast - Send message\n"
            "/stats - View stats"
        )

    # =========================
    # 📊 STATS
    # =========================
    @bot.message_handler(commands=['stats'])
    def stats(msg):
        if msg.from_user.id != owner_id:
            return

        s = get_stats(token)

        text = (
            f"📊 Stats\n\n"
            f"Users: {s.get('users',0)}\n"
            f"Videos: {s.get('videos',0)}\n"
            f"Images: {s.get('images',0)}"
        )

        bot.send_message(msg.chat.id, text)

    # =========================
    # 📢 BROADCAST
    # =========================
    @bot.message_handler(commands=['broadcast'])
    def broadcast(msg):
        if msg.from_user.id != owner_id:
            return

        bot.send_message(msg.chat.id, "Send message:")
        bot.register_next_step_handler(msg, send_bc)

    def send_bc(msg):
        users = users.find()

        for u in users:
            try:
                bot.send_message(u["user_id"], msg.text)
            except:
                pass

        bot.send_message(msg.chat.id, "✅ Done")

    # =========================
    # ▶️ RUN
    # =========================
    t = threading.Thread(target=bot.infinity_polling)
    t.start()

    running_bots[token] = bot

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
# 🔴 STOP ALL
# =========================
def stop_all_bots():
    for token in list(running_bots.keys()):
        try:
            running_bots[token].stop_polling()
        except:
            pass
        del running_bots[token]

# =========================
# 🟢 START ALL
# =========================
def start_all_bots(bots_list):
    for b in bots_list:
        start_user_bot(b["token"], b["owner_id"])
