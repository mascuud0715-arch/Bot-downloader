from main_bot import start_main_bot
from bot_manager import start_user_bot
from database import get_all_bots

import threading
import time

# =========================
# 🚀 START USER BOTS
# =========================

def start_all_bots():
    bots = get_all_bots()

    if not bots:
        print("❌ No bots found")
        return

    for b in bots:
        token = b.get("token")
        owner_id = b.get("owner_id")

        if token:
            try:
                start_user_bot(token, owner_id)
                print(f"✅ Started bot: {token}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Error: {e}")

# =========================
# 🧠 MAIN SYSTEM
# =========================

def run():
    print("🚀 SYSTEM STARTING...\n")

    # Start all bots in background
    t = threading.Thread(target=start_all_bots)
    t.start()

    # Start main bot
    start_main_bot()

# =========================
# ▶️ RUN
# =========================

if __name__ == "__main__":
    run()
