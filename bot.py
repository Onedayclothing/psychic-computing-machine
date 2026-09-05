import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
STOCK_FILE = "stock.json"

# អានស្តុកពី JSON
def load_stock():
    if not os.path.exists(STOCK_FILE):
        return {}
    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# រក្សាទុកស្តុកចូល JSON
def save_stock(data):
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "សួស្តី! Bot គ្រប់គ្រងស្តុក Oneday Clothing បានដំណើរការជោគជ័យហើយ!\n\n"
        "បញ្ជី Commands ដែលអាចប្រើបាន:\n"
        "👉 /stock - មើលបញ្ជីទំនិញទាំងអស់\n"
        "👉 /check [ឈ្មោះ] - ឆែកស្តុកទំនិញជាក់លាក់\n"
        "👉 /add [ឈ្មោះ] [ចំនួន] - បន្ថែមចំនួនស្តុក\n"
        "👉 /sell [ឈ្មោះ] [ចំនួន] - កាត់បន្ថយស្តុកពេលលក់ចេញ"
    )
    await update.message.reply_text(msg)

async def show_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stock = load_stock()
    if not stock:
        await update.message.reply_text("📦 គ្មានទំនិញក្នុងស្តុកទេនាពេលនេះ។")
        return
    
    response = "📦 **បញ្ជីស្តុក Oneday Clothing:**\n"
    for item, qty in stock.items():
        response += f"- {item}: {qty} ដំ/ឈុត\n"
    await update.message.reply_text(response)

async def check_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ សូមបញ្ចូលឈ្មោះទំនិញផង (ឧទាហរណ៍: /check shirt)")
        return
    
    item_name = context.args[0].lower()
    stock = load_stock()
    
    if item_name in stock:
        await update.message.reply_text(- f"🔍 ទំនិញ **{item_name}** សល់ចំនួន: **{stock[item_name]}**")
    else:
        await update.message.reply_text(f"❌ រកមិនឃើញទំនិញ '{item_name}' ក្នុងប្រព័ន្ធទេ។")

async def add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ ទម្រង់ខុស! ប្រើប្រាស់: `/add [ឈ្មោះ] [ចំនួន]` (ឧ: `/add shirt 10`)")
        return
    
    item_name = context.args[0].lower()
    try:
        qty = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ ចំនួនទឹកប្រាក់ ឬចំនួនស្តុកត្រូវតែជាតួលេខ!")
        return

    stock = load_stock()
    stock[item_name] = stock.get(item_name, 0) + qty
    save_stock(stock)
    
    await update.message.reply_text(f"✅ បានបន្ថែម {qty} ទៅលើ **{item_name}** ជាជោគជ័យ! ស្តុកសរុប: {stock[item_name]}")

async def sell_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ ទម្រង់ខុស! ប្រើប្រាស់: `/sell [ឈ្មោះ] [ចំនួន]` (ឧ: `/sell shirt 2`)")
        return
    
    item_name = context.args[0].lower()
    try:
        qty = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ ចំនួនត្រូវតែជាតួលេខ!")
        return

    stock = load_stock()
    if item_name not in stock or stock[item_name] < qty:
        current_qty = stock.get(item_name, 0)
        await update.message.reply_text(f"❌ ស្តុកទំនិញ **{item_name}** មិនគ្រាន់ទេ។ សល់ក្នុងស្តុកត្រឹមតែ: {current_qty}")
        return
    
    stock[item_name] -= qty
    save_stock(stock)
    
    await update.message.reply_text(f"📉 បានកាត់កងលក់ចេញ {qty} ពី **{item_name}**! ស្តុកនៅសល់: {stock[item_name]}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stock', show_stock))
    application.add_handler(CommandHandler('list', show_stock))
    application.add_handler(CommandHandler('check', check_item))
    application.add_handler(CommandHandler('add', add_stock))
    application.add_handler(CommandHandler('sell', sell_item))
    
    print("Bot កំពុងរត់...")
    application.run_polling()
