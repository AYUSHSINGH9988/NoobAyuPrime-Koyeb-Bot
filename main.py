import os
import telebot
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. HEALTH CHECK SERVER (Koyeb ke liye) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    # Koyeb port 8000 check karta hai
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Health check server started on port {port}")
    server.serve_forever()

# Server ko alag thread mein chalayein
threading.Thread(target=run_health_server, daemon=True).start()

# --- 2. TELEGRAM BOT LOGIC ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
KOYEB_API_KEY = os.getenv('KOYEB_API_KEY')
SERVICE_ID = os.getenv('SERVICE_ID')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Redeployer Bot Active! 🚀\nUse /redeploy to restart your service.")

@bot.message_handler(commands=['redeploy'])
def redeploy_service(message):
    headers = {
        'Authorization': f'Bearer {KOYEB_API_KEY}',
        'Content-Type': 'application/json',
    }
    url = f'https://app.koyeb.com/v1/services/{SERVICE_ID}/redeploy'
    
    bot.reply_to(message, "🔄 Koyeb ko redeploy request bhej raha hoon...")
    
    try:
        response = requests.post(url, headers=headers, json={"use_cache": False})
        if response.status_code in [200, 201]:
            bot.reply_to(message, "✅ Success! Naya build start ho gaya hai.")
        else:
            bot.reply_to(message, f"❌ Error: {response.status_code}\n{response.text}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

print("Bot is polling...")
bot.polling()

    