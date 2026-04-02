import telebot
from telebot.types import ReplyKeyboardMarkup
from config import BOT_TOKEN, ADMIN_ID, USER_BUTTONS, ADMIN_BUTTON
from database import add_user, get_user_bots

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# 🏁 START COMMAND
# =========================

@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id

    # Save user
    add_user(user_id)

    # Keyboard
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(USER_BUTTONS[0], USER_BUTTONS[1])
    markup.row(USER_BUTTONS[2])

    # Admin button
    if user_id == ADMIN_ID:
        markup.row(ADMIN_BUTTON)

    bot.send_message(
        msg.chat.id,
        "🚀 Kusoo dhawoow Bot System-ka PRO!\n\nDooro option:",
        reply_markup=markup
    )

# =========================
# ➕ CREATE BOT
# =========================

@bot.message_handler(func=lambda m: m.text == "➕ Create Bot")
def create_bot(msg):
    bot.send_message(
        msg.chat.id,
        "🤖 Fadlan ii soo dir BOT TOKEN-ka aad rabto inaad ku darto:"
    )

    bot.register_next_step_handler(msg, save_bot_token)


def save_bot_token(msg):
    token = msg.text.strip()

    # Temporary save (real logic next files)
    bot.send_message(
        msg.chat.id,
        f"✅ Token waa la helay:\n{token}\n\n(Processing system coming next...)"
    )

# =========================
# 🤖 MY BOTS
# =========================

@bot.message_handler(func=lambda m: m.text == "🤖 My Bots")
def my_bots(msg):
    user_id = msg.from_user.id
    bots = get_user_bots(user_id)

    if not bots:
        bot.send_message(msg.chat.id, "❌ Wax bot ah ma lihid.")
        return

    text = "🤖 Bots-kaaga:\n\n"
    for b in bots:
        text += f"• @{b.get('username', 'NoUsername')}\n"

    bot.send_message(msg.chat.id, text)

# =========================
# ℹ️ HELP
# =========================

@bot.message_handler(func=lambda m: m.text == "ℹ️ Help")
def help_menu(msg):
    bot.send_message(
        msg.chat.id,
        "📌 Isticmaal bot-kan si aad u abuurto bots kale oo PRO ah.\n\n"
        "➕ Create Bot - Ku dar bot cusub\n"
        "🤖 My Bots - Arag bots-kaaga"
    )

# =========================
# ⚙️ ADMIN PANEL (TEMP)
# =========================

@bot.message_handler(func=lambda m: m.text == ADMIN_BUTTON)
def admin_panel(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        msg.chat.id,
        "⚙️ Admin Panel (coming next files...)"
    )

# =========================
# 🚀 RUN BOT
# =========================

print("✅ Main Bot is Running...")
bot.infinity_polling()
