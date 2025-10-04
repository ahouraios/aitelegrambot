# === بخش ۱: وارد کردن کتابخانه‌ها ===
import os
import logging
import requests
import telegram
from flask import Flask, request

# === بخش ۲: تنظیمات اولیه و متغیرها ===

# تنظیم لاگ‌ها برای نمایش بهتر خطاها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن توکن ربات از متغیرهای محیطی Render
# مطمئن شوید که در Render یک Environment Variable به نام TELEGRAM_BOT_TOKEN ساخته‌اید
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    logger.error("متغیر TELEGRAM_BOT_TOKEN پیدا نشد!")
    # در صورت نبود توکن، برنامه متوقف می‌شود
    exit()

# ساخت نمونه‌های اولیه از فلسک و ربات تلگرام
app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


# === بخش ۳: توابع اصلی ربات (منطق شما) ===
# این توابع باید مطابق با منطق ربات شما تکمیل شوند

def start(update, context):
    """تابع مربوط به دستور /start"""
    try:
        user_name = update.message.from_user.first_name
        welcome_message = f"سلام {user_name}! به ربات اهورایی خوش آمدید."
        update.message.reply_text(welcome_message)
    except Exception as e:
        logger.error(f"خطا در تابع start: {e}")

def generate_response(update, context):
    """تابع اصلی برای پاسخ به پیام‌های کاربر"""
    try:
        user_text = update.message.text
        # در اینجا می‌توانید منطق پاسخ‌دهی هوش مصنوعی یا هر منطق دیگری را اضافه کنید
        response_text = f"شما گفتید: '{user_text}'. من در حال توسعه هستم."
        update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"خطا در تولید پاسخ: {e}")
        update.message.reply_text("خطایی در پردازش پیام شما رخ داد. لطفاً دوباره تلاش کنید.")


# === بخش ۴: مسیرهای وب (Endpoints) ===

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook_handler():
    """این تابع، آپدیت‌های تلگرام را از طریق وبهوک دریافت می‌کند"""
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # مدیریت دستورات و پیام‌ها
        if update.message and update.message.text:
            if update.message.text.startswith('/start'):
                start(update, {})
            else:
                generate_response(update, {'bot': bot})
        
        return 'ok', 200

    except Exception as e:
        logger.error(f"خطا در وبهوک هندلر: {e}")
        return 'error', 500

@app.route('/')
def index():
    """یک صفحه ساده برای اطمینان از بالا بودن سرور"""
    return 'Bot is running!'


# --- این تابع جدید است برای تنظیم وبهوک از داخل سرور ---
@app.route('/setup_webhook_internally')
def setup_webhook_internally():
    """
    این مسیر را یک بار در مرورگر باز کنید تا وبهوک به صورت خودکار تنظیم شود.
    این کار نیاز به VPN یا curl را از بین می‌برد.
    """
    # آدرس کامل وبهوک شما که تلگرام باید به آن پیام بفرستد
    WEBHOOK_URL = f'https://aitelegrambot-vm0v.onrender.com/{TELEGRAM_BOT_TOKEN}'
    # API تلگرام برای تنظیم وبهوک
    TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook'
    
    try:
        response = requests.post(TELEGRAM_API_URL, data={'url': WEBHOOK_URL})
        response.raise_for_status() # اگر خطا بود، exception ایجاد می‌کند
        
        if response.json().get('ok'):
            return "Webhook setup was successful! ربات شما اکنون فعال است.", 200
        else:
            return f"Failed to set webhook. Telegram API response: {response.text}", 500
            
    except requests.exceptions.RequestException as e:
        logger.error(f"خطا در برقراری ارتباط با API تلگرام: {e}")
        return f"An error occurred while communicating with Telegram: {str(e)}", 500
    except Exception as e:
        logger.error(f"یک خطای پیش‌بینی نشده در تنظیم وبهوک: {e}")
        return f"An unexpected error occurred: {str(e)}", 500
# --- پایان تابع جدید ---


# === بخش ۵: اجرای برنامه (فقط برای تست محلی) ===
if __name__ == "__main__":
    # Render این بخش را اجرا نمی‌کند و از دستور gunicorn استفاده می‌کند
    # این بخش فقط برای تست روی کامپیوتر شخصی شماست
    app.run(debug=True)
