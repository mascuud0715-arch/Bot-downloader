import telebot
from telebot.types import ReplyKeyboardMarkup

from config import *
from database import *
from bot_manager import create_bot, stop_all_bots, start_all_bots

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# 🔒 FORCE JOIN CHECK
# =========================

def check_force_join(user_id):
    if not FORCE_JOIN_ON:
        return True

    chs = get_channels()

    for ch in chs:
        try:
            member = bot.get_chat_member(ch["channel_id"], user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False

    return True

# =========================
# 🚀 START MAIN BOT
# =========================

def start_main_bot():
    print("✅ Main Bot Running...")

    # =========================
    # /START
    # =========================
    @bot.message_handler(commands=['start'])
    def start(msg):
        user_id = msg.from_user.id
        add_user(user_id)

        # 🔒 Force Join
        if not check_force_join(user_id):
            channels = get_channels()

            text = "❗ You must join the channels first:\n\n"
            for ch in channels:
                text += f"{ch['channel_id']}\n"

            bot.send_message(msg.chat.id, text)
            return

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("➕ Add Bot", "🤖 My Bots")
        markup.row("❌ Remove Bot")

        if user_id == ADMIN_ID:
            markup.row("⚙️ Admin Panel")

        bot.send_message(
            msg.chat.id,
            "🚀 Welcome to Bot System\n\n"
            "Create and manage your bots easily.",
            reply_markup=markup
        )

    # =========================
    # ➕ ADD BOT
    # =========================
    @bot.message_handler(func=lambda m: m.text == "➕ Add Bot")
    def add_bot_step(msg):
        bot.send_message(msg.chat.id, "📩 Send your bot token:")
        bot.register_next_step_handler(msg, get_token)

    def get_token(msg):
        token = msg.text.strip()
        user_data = {"token": token}

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("🔥 ALL")
        markup.row("TikTok + Facebook")
        markup.row("X + Instagram")
        markup.row("YouTube + Snapchat")
        markup.row("Pinterest")

        bot.send_message(msg.chat.id, "Choose bot mode:", reply_markup=markup)
        bot.register_next_step_handler(msg, lambda m: save_bot(m, user_data))

    def save_bot(msg, user_data):
        token = user_data["token"]
        mode = msg.text
        user_id = msg.from_user.id

        ok, text = create_bot(user_id, token)

        if ok:
            bots.update_one(
                {"token": token},
                {"$set": {"mode": mode}}
            )

        bot.send_message(msg.chat.id, text)

    # =========================
    # 🤖 MY BOTS
    # =========================
    @bot.message_handler(func=lambda m: m.text == "🤖 My Bots")
    def my_bots(msg):
        user_bots = get_user_bots(msg.from_user.id)

        if not user_bots:
            bot.send_message(msg.chat.id, "❌ No bots found.")
            return

        text = "🤖 Your Bots:\n\n"
        for b in user_bots:
            text += f"• @{b.get('username')} | {b.get('mode','N/A')}\n"

        bot.send_message(msg.chat.id, text)

    # =========================
    # ❌ REMOVE BOT
    # =========================
    @bot.message_handler(func=lambda m: m.text == "❌ Remove Bot")
    def remove_bot_step(msg):
        bot.send_message(msg.chat.id, "Send bot username:")
        bot.register_next_step_handler(msg, remove_bot)

    def remove_bot(msg):
        username = msg.text.replace("@", "")
        b = bots.find_one({"username": username})

        if not b:
            bot.send_message(msg.chat.id, "❌ Bot not found.")
            return

        delete_bot(b["token"])
        bot.send_message(msg.chat.id, "✅ Bot removed.")

    # =========================
    # ⚙️ ADMIN PANEL
    # =========================
    @bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
    def admin_panel(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📊 Stats", "🤖 Bots")
        markup.row("📢 Broadcast")
        markup.row("➕ Add Channel", "❌ Remove Channel")
        markup.row("🔴 Stop Bots", "🟢 Start Bots")

        bot.send_message(msg.chat.id, "Admin Panel:", reply_markup=markup)

    # =========================
    # 📊 STATS
    # =========================
    @bot.message_handler(func=lambda m: m.text == "📊 Stats")
    def stats(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        total = len(get_all_bots())
        bot.send_message(msg.chat.id, f"Total Bots: {total}")

    # =========================
    # 🤖 ALL BOTS
    # =========================
    @bot.message_handler(func=lambda m: m.text == "🤖 Bots")
    def all_bots(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        allbots = get_all_bots()

        text = "Bots:\n\n"
        for b in allbots:
            text += f"• @{b.get('username')}\n"

        bot.send_message(msg.chat.id, text)

    # =========================
    # 📢 BROADCAST
    # =========================
    @bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
    def broadcast(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        bot.send_message(msg.chat.id, "Send message:")
        bot.register_next_step_handler(msg, send_broadcast)

    def send_broadcast(msg):
        text = msg.text
        for b in get_all_bots():
            try:
                telebot.TeleBot(b["token"]).send_message(msg.chat.id, text)
            except:
                pass

        bot.send_message(msg.chat.id, "✅ Sent.")

    # =========================
    # 📢 CHANNELS
    # =========================
    @bot.message_handler(func=lambda m: m.text == "➕ Add Channel")
    def add_channel_step(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        bot.send_message(msg.chat.id, "Send channel ID or @username:")
        bot.register_next_step_handler(msg, save_channel)

    def save_channel(msg):
        add_channel(msg.text.strip())
        bot.send_message(msg.chat.id, "✅ Channel added.")

    @bot.message_handler(func=lambda m: m.text == "❌ Remove Channel")
    def remove_channel_step(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        bot.send_message(msg.chat.id, "Send channel ID:")
        bot.register_next_step_handler(msg, delete_channel)

    def delete_channel(msg):
        remove_channel(msg.text.strip())
        bot.send_message(msg.chat.id, "❌ Channel removed.")

    # =========================
    # 🔴 STOP ALL
    # =========================
    @bot.message_handler(func=lambda m: m.text == "🔴 Stop Bots")
    def stop(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        stop_all_bots()
        bot.send_message(msg.chat.id, "Stopped all bots.")

    # =========================
    # 🟢 START ALL
    # =========================
    @bot.message_handler(func=lambda m: m.text == "🟢 Start Bots")
    def start_all(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        start_all_bots(get_all_bots())
        bot.send_message(msg.chat.id, "Started all bots.")

    # =========================
    # ▶️ RUN
    # =========================
    bot.infinity_polling()
