import telebot
import requests

# --- Apni Details Yaha Dalein ---
BOT_TOKEN = 'YAHAN_APNA_TELEGRAM_BOT_TOKEN_DALEIN'
KOYEB_API_KEY = 'droo03gphbsabo2uq36dafi97qtkv72zslbe1cnwj6henenu8i5j8b0giagnepqs'
SERVICE_ID = '5f48e7b9-e008-4975-a1e6-6d6d9faa613b'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot ready hai! Naya commit karne ke baad /redeploy likhein.")

@bot.message_handler(commands=['redeploy'])
def redeploy_service(message):
    headers = {
        'Authorization': f'Bearer {KOYEB_API_KEY}',
        'Content-Type': 'application/json',
    }
    
    url = f'https://app.koyeb.com/v1/services/{SERVICE_ID}/redeploy'
    
    bot.reply_to(message, "🔄 Koyeb ko redeploy signal bhej raha hu...")
    
    try:
        # 'use_cache': False karne se fresh build hota hai
        response = requests.post(url, headers=headers, json={"use_cache": False})
        
        if response.status_code in [200, 201]:
            bot.reply_to(message, "✅ Success! Koyeb ne naya build start kar diya hai. Dashboard check karein.")
        else:
            bot.reply_to(message, f"❌ Kuch gadbad hui!\nStatus Code: {response.status_code}\nResponse: {response.text}")
            
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

print("Redeployer Bot chal raha hai...")
bot.polling()
