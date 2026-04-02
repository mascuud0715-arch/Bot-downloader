import telebot
from telebot.types import ReplyKeyboardMarkup
from bot_manager import send_join_buttons
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

    for ch in get_channels():
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

        
       if not check_force_join(user_id):
           send_join_buttons(bot, msg.chat.id)
           return

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("➕ Add Bot", "🤖 My Bots")
        markup.row("❌ Remove Bot")

        if user_id == ADMIN_ID:
            markup.row("⚙️ Admin Panel")

        bot.send_message(
            msg.chat.id,
            "🚀 Bot Management System\n\nCreate & control your bots easily.",
            reply_markup=markup
        )

    # =========================
    # ➕ ADD BOT
    # =========================
    @bot.message_handler(func=lambda m: m.text == "➕ Add Bot")
    def add_bot_step(msg):
        bot.send_message(msg.chat.id, "Send your bot token:")
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
        data = get_user_bots(msg.from_user.id)

        if not data:
            bot.send_message(msg.chat.id, "No bots found.")
            return

        text = "Your Bots:\n\n"
        for b in data:
            text += f"• @{b['username']} | {b.get('mode','N/A')}\n"

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
            bot.send_message(msg.chat.id, "Bot not found.")
            return

        delete_bot(b["token"])
        bot.send_message(msg.chat.id, "Bot removed.")

    # =========================
    # ⚙️ ADMIN PANEL
    # =========================
    @bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
    def admin_panel(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📊 Stats", "🤖 Bots")
        markup.row("📢 Broadcast ALL USERS")
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

        bot.send_message(
            msg.chat.id,
            f"Total Bots: {len(get_all_bots())}"
        )

    # =========================
    # 🤖 ALL BOTS
    # =========================
    @bot.message_handler(func=lambda m: m.text == "🤖 Bots")
    def all_bots(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        text = "All Bots:\n\n"
        for b in get_all_bots():
            text += f"• @{b['username']}\n"

        bot.send_message(msg.chat.id, text)

    # =========================
    # 📢 GLOBAL BROADCAST
    # =========================
    @bot.message_handler(func=lambda m: m.text == "📢 Broadcast ALL USERS")
    def broadcast_all(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        bot.send_message(msg.chat.id, "Send message:")
        bot.register_next_step_handler(msg, send_global)

    def send_global(msg):
        text = msg.text

        sent = 0

        for b in get_all_bots():
            try:
                tb = telebot.TeleBot(b["token"])

                # users collection
                for u in users.find():
                    try:
                        tb.send_message(u["user_id"], text)
                        sent += 1
                    except:
                        pass
            except:
                pass

        bot.send_message(msg.chat.id, f"✅ Sent to {sent} users")

    # =========================
    # 📢 CHANNELS
    # =========================
    @bot.message_handler(func=lambda m: m.text == "➕ Add Channel")
    def add_channel_step(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        bot.send_message(msg.chat.id, "Send @channel or ID:")
        bot.register_next_step_handler(msg, save_channel)

    def save_channel(msg):
        add_channel(msg.text.strip())
        bot.send_message(msg.chat.id, "Channel added.")

    @bot.message_handler(func=lambda m: m.text == "❌ Remove Channel")
    def remove_channel_step(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        bot.send_message(msg.chat.id, "Send channel:")
        bot.register_next_step_handler(msg, delete_channel)

    def delete_channel(msg):
        remove_channel(msg.text.strip())
        bot.send_message(msg.chat.id, "Channel removed.")

    # =========================
    # 🔴 STOP ALL
    # =========================
    @bot.message_handler(func=lambda m: m.text == "🔴 Stop Bots")
    def stop(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        stop_all_bots()
        bot.send_message(msg.chat.id, "All bots stopped.")

    # =========================
    # 🟢 START ALL
    # =========================
    @bot.message_handler(func=lambda m: m.text == "🟢 Start Bots")
    def start_all(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        start_all_bots(get_all_bots())
        bot.send_message(msg.chat.id, "All bots started.")

    # =========================
    # ▶️ RUN
    # =========================
    bot.infinity_polling()
