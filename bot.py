import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)

# 1. Render servisini diri saxlamaq üçün Web Server
app = Flask('')

@app.route('/')
def home():
    return "Bot aktivdir!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Telegram Bot Token
TOKEN = "8833074176:AAGbarsayQx2J9F_59YL4mGC1kLPTq-WTQ8"

# Bütün filtrlərin cari vəziyyətini göstərən menyu
def main_keyboard(user_data):
    p_min = user_data.get('price_min', '-')
    p_max = user_data.get('price_max', '-')
    
    a_min = user_data.get('area_min', '-')
    a_max = user_data.get('area_max', '-')
    
    r_min = user_data.get('rooms_min', '-')
    r_max = user_data.get('rooms_max', '-')
    
    f_min = user_data.get('floor_min', '-')
    f_max = user_data.get('floor_max', '-')
    
    metro = user_data.get('metro', '-')
    region = user_data.get('region', '-')
    settlement = user_data.get('settlement', '-')

    keyboard = [
        [
            InlineKeyboardButton(f"💰 Qiymət Min: {p_min}", callback_data="set_price_min"),
            InlineKeyboardButton(f"💰 Qiymət Max: {p_max}", callback_data="set_price_max")
        ],
        [
            InlineKeyboardButton(f"📐 Sahə Min: {a_min} m²", callback_data="set_area_min"),
            InlineKeyboardButton(f"📐 Sahə Max: {a_max} m²", callback_data="set_area_max")
        ],
        [
            InlineKeyboardButton(f"🚪 Otaq Min: {r_min}", callback_data="set_rooms_min"),
            InlineKeyboardButton(f"🚪 Otaq Max: {r_max}", callback_data="set_rooms_max")
        ],
        [
            InlineKeyboardButton(f"🏢 Mərtəbə Min: {f_min}", callback_data="set_floor_min"),
            InlineKeyboardButton(f"🏢 Mərtəbə Max: {f_max}", callback_data="set_floor_max")
        ],
        [
            InlineKeyboardButton(f"🚇 Metro: {metro}", callback_data="set_metro"),
            InlineKeyboardButton(f"📍 Rayon: {region}", callback_data="set_region")
        ],
        [
            InlineKeyboardButton(f"🏡 Qəsəbə: {settlement}", callback_data="set_settlement")
        ],
        [
            InlineKeyboardButton("🔍 Axtar (Saytlar)", callback_data="search_all"),
            InlineKeyboardButton("🔄 Sıfırla", callback_data="reset_filters")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['state'] = None
    await update.message.reply_text(
        "👋 **Emlak Axtarış Botuna Xoş Gelmisiniz!**\n\n"
        "Aşağıdakı düymələrə sıxaraq istədiyiniz filtrləri təyin edin:",
        reply_markup=main_keyboard(context.user_data),
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Düyməyə görə gözləmə vəziyyəti (state) təyin edirik
    states = {
        "set_price_min": ("WAITING_PRICE_MIN", "✍️ Lütfən **MINIMUM QİYMƏTİ** daxil edin (məs: 50000):"),
        "set_price_max": ("WAITING_PRICE_MAX", "✍️ Lütfən **MAKSİMUM QİYMƏTİ** daxil edin (məs: 120000):"),
        "set_area_min": ("WAITING_AREA_MIN", "✍️ Lütfən **MINIMUM SAHƏNİ (m²)** daxil edin (məs: 60):"),
        "set_area_max": ("WAITING_AREA_MAX", "✍️ Lütfən **MAKSİMUM SAHƏNİ (m²)** daxil edin (məs: 110):"),
        "set_rooms_min": ("WAITING_ROOMS_MIN", "✍️ Lütfən **MINIMUM OTAQ SAYINI** daxil edin (məs: 2):"),
        "set_rooms_max": ("WAITING_ROOMS_MAX", "✍️ Lütfən **MAKSİMUM OTAQ SAYINI** daxil edin (məs: 4):"),
        "set_floor_min": ("WAITING_FLOOR_MIN", "✍️ Lütfən **MINIMUM MƏRTƏBƏNİ** daxil edin (məs: 3):"),
        "set_floor_max": ("WAITING_FLOOR_MAX", "✍️ Lütfən **MAKSİMUM MƏRTƏBƏNİ** daxil edin (məs: 12):"),
        "set_metro": ("WAITING_METRO", "✍️ Lütfən **METRO STANSİYASINI** yazın (məs: Elmlər):"),
        "set_region": ("WAITING_REGION", "✍️ Lütfən **RAYON ADINI** yazın (məs: Yasamal):"),
        "set_settlement": ("WAITING_SETTLEMENT", "✍️ Lütfən **QƏSƏBƏ ADINI** yazın (məs: Xırdalan):")
    }

    if data in states:
        context.user_data['state'] = states[data][0]
        await query.edit_message_text(states[data][1], parse_mode="Markdown")

    elif data == "reset_filters":
        context.user_data.clear()
        await query.edit_message_text("🔄 Bütün filtrlər sıfırlandı!", reply_markup=main_keyboard(context.user_data))

    elif data == "search_all":
        await query.edit_message_text("🔎 Qeyd olunmuş filtrlər üzrə saytlardan elanlar axtarılır, lütfən gözləyin...")

# İstifadəçi çata mətnsəl mesaj (rəqəm və ya söz) yazanda daxil olunan informasiyanı tutur
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    text = update.message.text

    key_map = {
        'WAITING_PRICE_MIN': 'price_min',
        'WAITING_PRICE_MAX': 'price_max',
        'WAITING_AREA_MIN': 'area_min',
        'WAITING_AREA_MAX': 'area_max',
        'WAITING_ROOMS_MIN': 'rooms_min',
        'WAITING_ROOMS_MAX': 'rooms_max',
        'WAITING_FLOOR_MIN': 'floor_min',
        'WAITING_FLOOR_MAX': 'floor_max',
        'WAITING_METRO': 'metro',
        'WAITING_REGION': 'region',
        'WAITING_SETTLEMENT': 'settlement'
    }

    if state in key_map:
        context.user_data[key_map[state]] = text
        context.user_data['state'] = None
        await update.message.reply_text(
            f"✅ **{text}** qəbul olundu!\n\nYenilənmiş menyu:",
            reply_markup=main_keyboard(context.user_data),
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Lütfən menyudakı düymələrdən birini seçib mətni daxil edin.")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()
