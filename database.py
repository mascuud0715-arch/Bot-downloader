from pymongo import MongoClient
from config import MONGO_URI

# =========================
# 🔗 CONNECT MONGODB
# =========================

client = MongoClient(MONGO_URI)
db = client["bot_system"]

# Collections
users = db["users"]
bots = db["bots"]
channels = db["channels"]
stats = db["stats"]

# =========================
# 👤 USERS
# =========================

def add_user(user_id):
    if not users.find_one({"user_id": user_id}):
        users.insert_one({
            "user_id": user_id,
            "bots": []
        })

def get_user(user_id):
    return users.find_one({"user_id": user_id})

def add_user_bot(user_id, token):
    users.update_one(
        {"user_id": user_id},
        {"$addToSet": {"bots": token}}
    )

def remove_user_bot(user_id, token):
    users.update_one(
        {"user_id": user_id},
        {"$pull": {"bots": token}}
    )

# =========================
# 🤖 BOTS
# =========================

def add_bot(owner_id, token, username):
    bots.insert_one({
        "owner_id": owner_id,
        "token": token,
        "username": username,
        "status": True
    })

def get_all_bots():
    return list(bots.find())

def get_user_bots(owner_id):
    return list(bots.find({"owner_id": owner_id}))

def delete_bot(token):
    bots.delete_one({"token": token})

def update_bot_status(token, status):
    bots.update_one(
        {"token": token},
        {"$set": {"status": status}}
    )

# =========================
# 📢 CHANNELS (Force Join)
# =========================

def add_channel(channel_id):
    channels.insert_one({
        "channel_id": channel_id
    })

def get_channels():
    return list(channels.find())

def remove_channel(channel_id):
    channels.delete_one({"channel_id": channel_id})

# =========================
# 📊 STATS
# =========================

def add_stats(token):
    if not stats.find_one({"token": token}):
        stats.insert_one({
            "token": token,
            "users": 0,
            "videos": 0,
            "images": 0
        })

def inc_users(token):
    stats.update_one({"token": token}, {"$inc": {"users": 1}})

def inc_videos(token):
    stats.update_one({"token": token}, {"$inc": {"videos": 1}})

def inc_images(token):
    stats.update_one({"token": token}, {"$inc": {"images": 1}})

def get_stats(token):
    return stats.find_one({"token": token})
