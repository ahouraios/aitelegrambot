import os
import logging
import telegram
from flask import Flask, request
import google.generativeai as genai

# --- پیکربندی‌ها ---
# خواندن توکن‌ها از متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# تنظیم لاگین برای دیباگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تنظیم مدل Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("مدل Gemini با موفقیت پیکربندی شد.")
except Exception as e:
    logger.error(f"خطا در پیکربندی Gemini: {e}")
    model = None

# راه‌اندازی ربات تلگرام و فلسک
bot = telegram.Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# --- توابع اصلی ربات ---
def start(update, context):
    """پاسخ به دستور /start"""
    welcome_message = "سلام! من یک ربات هوشمند هستم. می‌توانید سوال خود را بپرسید."
    update.message.reply_text(welcome_message)

def generate_response(update, context):
    """پردازش پیام کاربر و تولید پاسخ با Gemini"""
    if not model:
        update.message.reply_text("متاسفانه سرویس هوش مصنوعی در حال حاضر در دسترس نیست.")
        return

    user_text = update.message.text
    logger.info(f"پیام دریافتی از کاربر: {user_text}")
    
    try:
        # ارسال پیام "در حال پردازش..."
        processing_message = update.message.reply_text("⏳ در حال پردازش...")
        
        response = model.generate_content(user_text)
        
        # ویرایش پیام و جایگزینی با پاسخ نهایی
        context.bot.edit_message_text(
            chat_id=update.message.chat_id,
            message_id=processing_message.message_id,
            text=response.text
        )
        logger.info("پاسخ با موفقیت تولید و ارسال شد.")
    except Exception as e:
        logger.error(f"خطا در تولید پاسخ: {e}")
        update.message.reply_text("خطایی در پردازش درخواست شما رخ داد. لطفاً دوباره تلاش کنید.")

# --- وب‌سرور فلسک برای وبهوک ---
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook_handler():
    """این تابع وبهوک را مدیریت می‌کند"""
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    
    # اینجا می‌توانید دستورات را مدیریت کنید
    if update.message.text and update.message.text.startswith('/start'):
        start(update, {})
    elif update.message.text:
        generate_response(update, {'bot': bot})
        
    return 'ok'

@app.route('/')
def index():
    """یک صفحه ساده برای اطمینان از بالا بودن سرور"""
    return 'Bot is running!'

if __name__ == "__main__":
    # این بخش فقط برای تست محلی است و روی Render اجرا نمی‌شود
    app.run(debug=True)
