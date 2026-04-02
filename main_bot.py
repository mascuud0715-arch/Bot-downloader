import telebot
from telebot.types import ReplyKeyboardMarkup

from config import *
from database import add_user, get_user_bots, delete_bot, get_all_bots, add_channel, get_channels, remove_channel
from bot_manager import create_bot, stop_all_bots, start_all_bots

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# 🏁 START
# =========================

def start_main_bot():
    print("✅ Main Bot Running...")

    @bot.message_handler(commands=['start'])
    def start(msg):
        user_id = msg.from_user.id
        add_user(user_id)

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(BTN_CREATE, BTN_MYBOTS)
        markup.row(BTN_HELP)

        if user_id == ADMIN_ID:
            markup.row(BTN_ADMIN)

        bot.send_message(msg.chat.id, START_TEXT, reply_markup=markup)

    # =========================
    # ➕ CREATE BOT
    # =========================

    @bot.message_handler(func=lambda m: m.text == BTN_CREATE)
    def create(msg):
        bot.send_message(msg.chat.id, "📩 Ii soo dir TOKEN:")

        bot.register_next_step_handler(msg, save_token)

    def save_token(msg):
        token = msg.text.strip()
        user_id = msg.from_user.id

        ok, text = create_bot(user_id, token)
        bot.send_message(msg.chat.id, text)

    # =========================
    # 🤖 MY BOTS
    # =========================

    @bot.message_handler(func=lambda m: m.text == BTN_MYBOTS)
    def mybots(msg):
        bots = get_user_bots(msg.from_user.id)

        if not bots:
            bot.send_message(msg.chat.id, "❌ Bot ma lihid")
            return

        text = "🤖 Bots-kaaga:\n\n"
        for b in bots:
            text += f"• @{b.get('username')}\n"

        bot.send_message(msg.chat.id, text)

    # =========================
    # ℹ️ HELP
    # =========================

    @bot.message_handler(func=lambda m: m.text == BTN_HELP)
    def help(msg):
        bot.send_message(msg.chat.id, HELP_TEXT)

    # =========================
    # ⚙️ ADMIN PANEL
    # =========================

    @bot.message_handler(func=lambda m: m.text == BTN_ADMIN)
    def admin(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(ADMIN_STATS, ADMIN_BOTS)
        markup.row(ADMIN_BROADCAST)
        markup.row(ADMIN_ADD_CHANNEL, ADMIN_DEL_CHANNEL)
        markup.row(ADMIN_CLOSE_ALL, ADMIN_OPEN_ALL)

        bot.send_message(msg.chat.id, "⚙️ Admin Panel", reply_markup=markup)

    # =========================
    # 📊 STATS
    # =========================

    @bot.message_handler(func=lambda m: m.text == ADMIN_STATS)
    def stats(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        total_users = len(get_all_bots())
        bot.send_message(msg.chat.id, f"📊 Total Bots: {total_users}")

    # =========================
    # 🤖 ALL BOTS
    # =========================

    @bot.message_handler(func=lambda m: m.text == ADMIN_BOTS)
    def bots_list(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        all_bots = get_all_bots()

        text = "🤖 Bots List:\n\n"
        for b in all_bots:
            text += f"• @{b.get('username')}\n"

        bot.send_message(msg.chat.id, text)

    # =========================
    # 📢 BROADCAST
    # =========================

    @bot.message_handler(func=lambda m: m.text == ADMIN_BROADCAST)
    def broadcast(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        bot.send_message(msg.chat.id, "📩 Dir fariinta:")
        bot.register_next_step_handler(msg, send_broadcast)

    def send_broadcast(msg):
        text = msg.text
        all_bots = get_all_bots()

        for b in all_bots:
            try:
                tb = telebot.TeleBot(b["token"])
                tb.send_message(msg.chat.id, text)
            except:
                pass

        bot.send_message(msg.chat.id, "✅ Broadcast done")

    # =========================
    # 📢 CHANNELS
    # =========================

    @bot.message_handler(func=lambda m: m.text == ADMIN_ADD_CHANNEL)
    def addch(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        bot.send_message(msg.chat.id, "📩 Dir channel id:")
        bot.register_next_step_handler(msg, save_channel)

    def save_channel(msg):
        add_channel(msg.text.strip())
        bot.send_message(msg.chat.id, "✅ Channel added")

    @bot.message_handler(func=lambda m: m.text == ADMIN_DEL_CHANNEL)
    def delch(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        bot.send_message(msg.chat.id, "📩 Dir channel id:")
        bot.register_next_step_handler(msg, del_channel)

    def del_channel(msg):
        remove_channel(msg.text.strip())
        bot.send_message(msg.chat.id, "❌ Channel removed")

    # =========================
    # 🔴 CLOSE ALL
    # =========================

    @bot.message_handler(func=lambda m: m.text == ADMIN_CLOSE_ALL)
    def close_all(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        stop_all_bots()
        bot.send_message(msg.chat.id, "🔴 All bots stopped")

    # =========================
    # 🟢 OPEN ALL
    # =========================

    @bot.message_handler(func=lambda m: m.text == ADMIN_OPEN_ALL)
    def open_all(msg):
        if msg.from_user.id != ADMIN_ID:
            return

        start_all_bots(get_all_bots())
        bot.send_message(msg.chat.id, "🟢 All bots started")

    # =========================
    # ▶️ RUN
    # =========================

    bot.infinity_polling()
