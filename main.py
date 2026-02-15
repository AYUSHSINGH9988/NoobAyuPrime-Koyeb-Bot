import os
import telebot
import requests

# Dashboard se variables uthayega
BOT_TOKEN = os.getenv('BOT_TOKEN')
KOYEB_API_KEY = os.getenv('KOYEB_API_KEY')
SERVICE_ID = os.getenv('SERVICE_ID')

# --- DEBUGGING LOGS ---
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN dashboard se nahi mil raha!")
else:
    print(f"✅ BOT_TOKEN mila (Length: {len(BOT_TOKEN)})")
    if ":" not in BOT_TOKEN:
        print("❌ ERROR: Token mein ':' missing hai! Dashboard check karein.")

if not KOYEB_API_KEY: print("❌ ERROR: KOYEB_API_KEY missing hai!")
if not SERVICE_ID: print("❌ ERROR: SERVICE_ID missing hai!")
# ----------------------

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Redeployer Bot Active! 🚀")

@bot.message_handler(commands=['redeploy'])
def redeploy_service(message):
    headers = {
        'Authorization': f'Bearer {KOYEB_API_KEY}',
        'Content-Type': 'application/json',
    }
    url = f'https://app.koyeb.com/v1/services/{SERVICE_ID}/redeploy'
    bot.reply_to(message, "🔄 Redeploying...")
    try:
        response = requests.post(url, headers=headers, json={"use_cache": False})
        if response.status_code in [200, 201]:
            bot.reply_to(message, "✅ Success! Naya build start ho gaya.")
        else:
            bot.reply_to(message, f"❌ Error: {response.status_code}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

print("Bot is starting...")
bot.polling()

    
    