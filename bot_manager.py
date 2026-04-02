import telebot
import threading
import requests
import yt_dlp
import os

from database import *

# Running bots
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
# 📥 DOWNLOAD MEDIA
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
# 🎵 CONVERT TO MP3
# =========================
def convert_to_mp3(file_path):
    try:
        mp3_path = file_path.rsplit(".", 1)[0] + ".mp3"

        os.system(f'ffmpeg -i "{file_path}" -q:a 0 -map a "{mp3_path}"')

        if os.path.exists(mp3_path):
            return mp3_path
        return None
    except:
        return None

# =========================
# 🔒 FORCE JOIN CHECK
# =========================
def check_force_join(bot, user_id):
    for ch in get_channels():
        try:
            member = bot.get_chat_member(ch["channel_id"], user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# =========================
# 🔘 JOIN BUTTONS
# =========================
def send_join_buttons(bot, chat_id):
    channels = get_channels()

    markup = telebot.types.InlineKeyboardMarkup()

    # JOIN BUTTONS
    for ch in channels:
        link = ch.get("link") or f"https://t.me/{ch['channel_id'].replace('@','')}"
        markup.add(
            telebot.types.InlineKeyboardButton("➕ JOIN CHANNEL", url=link)
        )

    # CONFIRM BUTTON
    markup.add(
        telebot.types.InlineKeyboardButton("✅ CONFIRM", callback_data="confirm_join")
    )

    bot.send_message(
        chat_id,
        "⚠️ You must join our channel to use this bot.",
        reply_markup=markup
    )

# =========================
# ✅ CONFIRM JOIN
# =========================
@bot.callback_query_handler(func=lambda call: call.data == "confirm_join")
def confirm_join(call):
    user_id = call.from_user.id

    if check_force_join(bot, user_id):
        bot.answer_callback_query(call.id, "✅ Joined successfully!")
        bot.send_message(call.message.chat.id, "✅ Join confirmed! Now send your link.")
    else:
        bot.answer_callback_query(call.id, "❌ Not joined!")
        bot.send_message(call.message.chat.id, "❗ Please join channels first.")

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

        add_user(user_id)
        inc_users(token)

        if not check_force_join(bot, user_id):
            send_join_buttons(bot, msg.chat.id)
            return

        bot.send_message(
            msg.chat.id,
            "🤖 Welcome!\n\n"
            "Send any video or photo link.\n\n"
            "Supported:\n"
            "• TikTok\n"
            "• Instagram\n"
            "• X (Twitter)\n"
            "• YouTube\n"
            "• Facebook\n"
            "• Pinterest"
        )

    # =========================
    # 🔗 HANDLE LINKS
    # =========================
    @bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
    def handle_link(msg):
        user_id = msg.from_user.id

        if not check_force_join(bot, user_id):
            bot.send_message(msg.chat.id, "❗ Join channels first.")
            return

        bot_data = bots.find_one({"token": token})
        mode = bot_data.get("mode", "🔥 ALL")

        url = msg.text.lower()

        # =========================
        # 🎯 MODE FILTER (IMPROVED)
        # =========================
        if mode != "🔥 ALL":
            allowed = False

            if "tiktok" in mode.lower() and "tiktok.com" in url:
                allowed = True
            if "facebook" in mode.lower() and "facebook.com" in url:
                allowed = True
            if "instagram" in mode.lower() and "instagram.com" in url:
                allowed = True
            if "x" in mode.lower() and ("twitter.com" in url or "x.com" in url):
                allowed = True
            if "youtube" in mode.lower() and ("youtube.com" in url or "youtu.be" in url):
                allowed = True
            if "pinterest" in mode.lower() and "pinterest.com" in url:
                allowed = True

            if not allowed:
                bot.send_message(msg.chat.id, "❌ This link is not allowed in this bot mode.")
                return

        # =========================
        # ⏳ DOWNLOADING
        # =========================
        loading = bot.send_message(msg.chat.id, "⏳ Downloading...")

        file_path = download_media(msg.text)

        # Delete loading message
        try:
            bot.delete_message(msg.chat.id, loading.message_id)
        except:
            pass

        if not file_path:
            bot.send_message(msg.chat.id, "❌ Download failed.")
            return

        # 👉 QAYBTA 2 ayaa halkaan ka sii socota

        try:
            username = bot.get_me().username

            # 🎵 INLINE BUTTON
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(
                telebot.types.InlineKeyboardButton(
                    "🎵 MUSIC",
                    callback_data=f"music|{file_path}"
                )
            )

            caption = f"Via: @{username}"

            with open(file_path, "rb") as f:
                bot.send_document(
                    msg.chat.id,
                    f,
                    caption=caption,
                    reply_markup=markup
                )

            # MESSAGE 2
            bot.send_message(
                msg.chat.id,
                "Created: @Create_Your_via_downloader_bot"
            )

            inc_videos(token)

            # DELETE FILE (IMPORTANT 🚀)
            try:
                os.remove(file_path)
            except:
                pass

        except Exception as e:
            bot.send_message(msg.chat.id, "❌ Send error")

    # =========================
    # 🎵 MUSIC BUTTON
    # =========================
    @bot.callback_query_handler(func=lambda call: call.data.startswith("music"))
    def music_handler(call):
        data = call.data.split("|")

        if len(data) < 2:
            return

        file_path = data[1]

        bot.answer_callback_query(call.id, "⏳ Converting...")

        mp3 = convert_to_mp3(file_path)

        if not mp3:
            bot.send_message(call.message.chat.id, "❌ Failed to convert.")
            return

        try:
            with open(mp3, "rb") as f:
                bot.send_audio(call.message.chat.id, f)

            os.remove(mp3)
        except:
            bot.send_message(call.message.chat.id, "❌ Error sending audio")

    # =========================
    # ⚙️ OWNER ADMIN PANEL
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
    # 📢 BROADCAST (FIXED DB)
    # =========================
    @bot.message_handler(commands=['broadcast'])
    def broadcast(msg):
        if msg.from_user.id != owner_id:
            return

        bot.send_message(msg.chat.id, "Send message:")
        bot.register_next_step_handler(msg, send_bc)

    def send_bc(msg):
        text = msg.text

        # FIX: use DB function
        for u in get_all_users():
            try:
                bot.send_message(u["user_id"], text)
            except:
                pass

        bot.send_message(msg.chat.id, "✅ Broadcast sent")

    # =========================
    # ▶️ RUN BOT
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
