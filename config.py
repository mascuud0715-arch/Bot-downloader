import os

# =========================
# 🔐 ENV VARIABLES (Railway)
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Main Bot Token
MONGO_URI = os.getenv("MONGO_URI")  # MongoDB URI
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # Your Telegram ID

# =========================
# ⚙️ SYSTEM SETTINGS
# =========================

# Main bot ON/OFF
MAIN_BOT_STATUS = True

# All bots ON/OFF
ALL_BOTS_STATUS = True

# Force Join ON/OFF
FORCE_JOIN = False

# =========================
# 📊 DEFAULT SETTINGS
# =========================

START_MESSAGE = "🚀 Kusoo dhawoow Bot System-ka PRO!"

# Buttons (User Menu)
USER_BUTTONS = [
    "➕ Create Bot",
    "🤖 My Bots",
    "ℹ️ Help"
]

# Admin button
ADMIN_BUTTON = "⚙️ Admin Panel"
