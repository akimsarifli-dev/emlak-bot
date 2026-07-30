import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Render servisini diri saxlamaq üçün Web Server
app = Flask('')

@app.route('/')
def home():
    return "Bot aktivdir!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Telegram Bot Menyu Strukturu (SİZİN YENİ TOKENİNİZLƏ)
TOKEN = "8833074176:AAG7_zplqHPHAOjHNoQiDW5u42YZiXaqmLw"

def main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💰 Qiymət (Min)", callback_data="price_min"),
            InlineKeyboardButton("💰 Qiymət (Max)", callback_data="price_max")
        ],
        [
            InlineKeyboardButton("📐 Sahə (Min m²)", callback_data="area_min"),
            InlineKeyboardButton("📐 Sahə (Max m²)", callback_data="area_max")
        ],
        [
            InlineKeyboardButton("🚪 Otaq (Min)", callback_data="rooms_min"),
            InlineKeyboardButton("🚪 Otaq (Max)", callback_data="rooms_max")
        ],
        [
            InlineKeyboardButton("🚇 Metro", callback_data="loc_metro"),
            InlineKeyboardButton("📍 Rayon / Qəsəbə", callback_data="loc_district")
        ],
        [
            InlineKeyboardButton("🔍 Axtar (Saytlar)", callback_data="search_all"),
            InlineKeyboardButton("🔄 Sıfırla", callback_data="reset_filters")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Emlak Axtarış Botuna Xoş Gelmisiniz!**\n\n"
        "Elanları axtarmaq üçün aşağıdakı filtrləri təyin edin:",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "loc_metro":
        await query.edit_message_text("🚇 Lütfən axtardığınız **Metro** stansiyasını seçin və ya yazın:", reply_markup=main_keyboard())
    elif data == "loc_district":
        await query.edit_message_text("📍 Lütfən axtardığınız **Rayon və ya Qəsəbə** adını seçin:", reply_markup=main_keyboard())
    elif data == "search_all":
        await query.edit_message_text("🔎 **yeniemlak.az**, **tap.az** və **lalafo.az** saytlarında axtarış başlanılır...")
    else:
        await query.edit_message_text(f"⚙️ Seçim qəbul olundu: {data}", reply_markup=main_keyboard())

if __name__ == '__main__':
    # Flask-ı ayrı thread-də işə salırıq
    threading.Thread(target=run_flask).start()
    
    # Telegram Bot-u başladırıq
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    
    application.run_polling()
