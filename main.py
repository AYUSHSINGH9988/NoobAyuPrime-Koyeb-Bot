import telebot
import requests
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pymongo import MongoClient

# --- 1. CONFIGURATION ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGO_URL = os.getenv('MONGO_URL')  # Mongo Connection String
ADMIN_ID = 1234567890  # <--- APNI TELEGRAM ID YAHAN DALEIN

# --- 2. MONGODB CONNECTION ---
try:
    client = MongoClient(MONGO_URL)
    db = client['koyeb_manager']
    collection = db['services'] # Is collection me data save hoga
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

bot = telebot.TeleBot(BOT_TOKEN)

# --- 3. HEALTH CHECK SERVER (Bot ko zinda rakhne ke liye) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# --- 4. HELPER FUNCTION ---
def is_admin(message):
    if message.from_user.id != ADMIN_ID:
        # Agar admin nahi hai to ignore karein
        return False
    return True

# --- 5. BOT COMMANDS ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_admin(message): return
    help_text = (
        "🗄️ **MongoDB Powered Koyeb Manager**\n\n"
        "Commands:\n"
        "1️⃣ `/add name api_key service_id`\n"
        "   (Save Service - Permanent)\n"
        "2️⃣ `/list`\n"
        "   (Saved Services dekhein)\n"
        "3️⃣ `/redeploy name`\n"
        "   (Service Restart karein)\n"
        "4️⃣ `/del name`\n"
        "   (Service Remove karein)"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

# --- SAVE DATA TO MONGODB ---
@bot.message_handler(commands=['add'])
def add_service(message):
    if not is_admin(message): return
    try:
        parts = message.text.split()
        if len(parts) != 4:
            bot.reply_to(message, "⚠️ Format: `/add name api_key service_id`")
            return
        
        name = parts[1]
        api_key = parts[2]
        service_id = parts[3]
        
        # MongoDB me update ya insert karein (Upsert)
        collection.update_one(
            {"name": name},
            {"$set": {"api_key": api_key, "service_id": service_id}},
            upsert=True
        )
        
        bot.reply_to(message, f"✅ **{name}** database me save ho gaya!", parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error saving to DB: {e}")

# --- LIST FROM MONGODB ---
@bot.message_handler(commands=['list'])
def list_services(message):
    if not is_admin(message): return
    
    services = collection.find()
    count = collection.count_documents({})
    
    if count == 0:
        bot.reply_to(message, "📭 Database khali hai.")
        return
    
    response = "📋 **Saved Services:**\n"
    for service in services:
        response += f"- `{service['name']}`\n"
        
    bot.reply_to(message, response, parse_mode="Markdown")

# --- REDEPLOY LOGIC ---
@bot.message_handler(commands=['redeploy'])
def redeploy_service(message):
    if not is_admin(message): return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "⚠️ Use: `/redeploy name`")
            return
        
        name = parts[1]
        # Database se details nikalein
        data = collection.find_one({"name": name})
        
        if not data:
            bot.reply_to(message, f"❌ '{name}' database me nahi mila.")
            return
        
        api_key = data['api_key']
        service_id = data['service_id']
        
        # Koyeb API Request
        headers = {
            'Authorization': f"Bearer {api_key}",
            'Content-Type': 'application/json',
        }
        url = f"https://app.koyeb.com/v1/services/{service_id}/redeploy"
        
        status_msg = bot.reply_to(message, f"🔄 **{name}** redeploy ho raha hai...", parse_mode="Markdown")
        
        response = requests.post(url, headers=headers, json={"use_cache": False})
        
        if response.status_code in [200, 201]:
            bot.edit_message_text(f"✅ Success! **{name}** restart ho gaya.", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text(f"❌ Failed! Code: {response.status_code}\n{response.text}", chat_id=message.chat.id, message_id=status_msg.message_id)
            
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# --- DELETE COMMAND ---
@bot.message_handler(commands=['del'])
def delete_service(message):
    if not is_admin(message): return
    try:
        name = message.text.split()[1]
        result = collection.delete_one({"name": name})
        
        if result.deleted_count > 0:
            bot.reply_to(message, f"🗑️ **{name}** delete kar diya gaya.", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"⚠️ **{name}** nahi mila.", parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ Use: `/del name`")

print("MongoDB Bot Started...")
bot.polling()
