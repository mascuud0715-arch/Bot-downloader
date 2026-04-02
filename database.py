from pymongo import MongoClient
from config import MONGO_URI

# =========================
# 🔗 CONNECT DATABASE
# =========================

client = MongoClient(MONGO_URI)
db = client["telegram_bot_system"]

# =========================
# 📂 COLLECTIONS
# =========================

users_col = db["users"]
bots_col = db["bots"]
channels_col = db["channels"]
stats_col = db["stats"]

# =========================
# 👤 USERS FUNCTIONS
# =========================

def add_user(user_id):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({
            "user_id": user_id,
            "bots": [],
            "joined": True
        })

def get_user(user_id):
    return users_col.find_one({"user_id": user_id})

def add_user_bot(user_id, bot_token):
    users_col.update_one(
        {"user_id": user_id},
        {"$addToSet": {"bots": bot_token}}
    )

def remove_user_bot(user_id, bot_token):
    users_col.update_one(
        {"user_id": user_id},
        {"$pull": {"bots": bot_token}}
    )

# =========================
# 🤖 BOTS FUNCTIONS
# =========================

def add_bot(owner_id, token, username):
    bots_col.insert_one({
        "owner_id": owner_id,
        "token": token,
        "username": username,
        "status": True,
        "users": 0,
        "videos": 0,
        "images": 0
    })

def get_user_bots(owner_id):
    return list(bots_col.find({"owner_id": owner_id}))

def delete_bot(token):
    bots_col.delete_one({"token": token})

def get_all_bots():
    return list(bots_col.find())

def update_bot_status(token, status):
    bots_col.update_one(
        {"token": token},
        {"$set": {"status": status}}
    )

# =========================
# 📢 CHANNELS (Force Join)
# =========================

def add_channel(channel_id):
    channels_col.insert_one({
        "channel_id": channel_id,
        "status": True
    })

def get_channels():
    return list(channels_col.find({"status": True}))

def remove_channel(channel_id):
    channels_col.delete_one({"channel_id": channel_id})

# =========================
# 📊 STATS SYSTEM
# =========================

def increase_stat(bot_token, field):
    stats_col.update_one(
        {"bot_token": bot_token},
        {"$inc": {field: 1}},
        upsert=True
    )

def get_stats(bot_token):
    return stats_col.find_one({"bot_token": bot_token})
