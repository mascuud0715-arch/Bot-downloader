import os

# =========================
# 🔐 ENV VARIABLES (Railway)
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")   # Main bot token
MONGO_URI = os.getenv("MONGO_URI")   # MongoDB URI
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # Your Telegram ID

# =========================
# ⚙️ SYSTEM CONTROL
# =========================

MAIN_BOT_ON = True        # Main bot ON/OFF
ALL_BOTS_ON = True        # All user bots ON/OFF
FORCE_JOIN_ON = False     # Force join ON/OFF

# =========================
# 📢 BROADCAST SETTINGS
# =========================

BROADCAST_ON = True

# =========================
# 📊 STATS SETTINGS
# =========================

STATS_ON = True

# =========================
# 🔒 SECURITY
# =========================

MAX_BOTS_PER_USER = 5

# =========================
# 📱 USER BUTTONS
# =========================

BTN_CREATE = "➕ Create Bot"
BTN_MYBOTS = "🤖 My Bots"
BTN_HELP = "ℹ️ Help"

# =========================
# ⚙️ ADMIN BUTTON
# =========================

BTN_ADMIN = "⚙️ Admin Panel"

# =========================
# ⚙️ ADMIN MENU BUTTONS
# =========================

ADMIN_STATS = "📊 Stats"
ADMIN_BOTS = "🤖 Bots"
ADMIN_BROADCAST = "📢 Broadcast"
ADMIN_ADD_CHANNEL = "➕ Add Channel"
ADMIN_DEL_CHANNEL = "❌ Remove Channel"
ADMIN_CLOSE_ALL = "🔴 Close All Bots"
ADMIN_OPEN_ALL = "🟢 Open All Bots"

# =========================
# 📝 TEXT MESSAGES
# =========================

START_TEXT = "🚀 Kusoo dhawoow Bot System-ka PRO!\n\nDooro option hoose 👇"

HELP_TEXT = (
    "📌 Isticmaal bot-kan si aad u sameyso bots kale.\n\n"
    "➕ Create Bot → Ku dar bot cusub\n"
    "🤖 My Bots → Arag bots-kaaga\n"
)

FORCE_JOIN_TEXT = "❗ Fadlan ku biir channel-ka si aad u sii wadato."
