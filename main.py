import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# إعداد السجلات لمراقبة أداء البوت
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# قراءة المفاتيح السرية من بيئة السيرفر المتغيرة (Environment Variables)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# تهيئة ذكاء جوجل الاصطناعي
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر البدء /start"""
    await update.message.reply_text('أهلاً بك يا غالي! أنا هرمز، مساعدك الذكي المربوط بسيرفر Render السحابي. أرسل لي أي سؤال وسأجيبك فوراً.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الرسائل القادمة من المستخدم وإرسالها لجوجل"""
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # إرسال النص إلى Gemini واستقبال الإجابة
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Error while generating content: {e}")
        await update.message.reply_text("عذراً، حدث خطأ أثناء معالجة طلبك. تأكد من صحة المفاتيح السرية بالسيرفر.")

def main() -> None:
    """تشغيل البوت"""
    if not TELEGRAM_TOKEN or not GOOGLE_API_KEY:
        logger.error("المفاتيح السرية TELEGRAM_TOKEN أو GOOGLE_API_KEY غير مضافة في السيرفر!")
        return

    # بناء التطبيق واستقبال البيانات من تليجرام تلقائياً
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # بدء تشغيل البوت بنظام Polling المناسب لسيرفرات الـ Web Service
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
