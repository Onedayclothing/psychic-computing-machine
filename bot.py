import os
import json
import requests
import time

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
STOCK_FILE = "stock.json"
OFFSET_FILE = "offset.txt"

def load_stock():
    if not os.path.exists(STOCK_FILE):
        return {}
    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_stock(data):
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_last_offset():
    if not os.path.exists(OFFSET_FILE):
        return 0
    with open(OFFSET_FILE, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def save_last_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def process_messages():
    offset = get_last_offset()
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=2"
    response = requests.get(url).json()
    
    if not response.get("ok"):
        return

    updates = response.get("result", [])
    for update in updates:
        update_id = update["update_id"]
        save_last_offset(update_id + 1)

        if "message" not in update:
            continue
            
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        if text == "/start":
            msg = (
                "សួស្តី! Bot គ្រប់គ្រងស្តុក Oneday Clothing បានដំណើរការជោគជ័យហើយ!\n\n"
                "បញ្ជី Commands:\n"
                "👉 /stock - មើលបញ្ជីទំនិញ\n"
                "👉 /check [ឈ្មោះ] - ឆែកស្តុកទំនិញ\n"
                "👉 /add [ឈ្មោះ] [ចំនួន] - បន្ថែមស្តុក\n"
                "👉 /sell [ឈ្មោះ] [ចំនួន] - លក់ចេញ"
            )
            send_message(chat_id, msg)

        elif text in ["/stock", "/list"]:
            stock = load_stock()
            if not stock:
                send_message(chat_id, "📦 គ្មានទំនិញក្នុងស្តុកទេនាពេលនេះ។")
            else:
                resp = "📦 **បញ្ជីស្តុក Oneday Clothing:**\n"
                for item, qty in stock.items():
                    resp += f"- {item}: {qty}\n"
                send_message(chat_id, resp)

        elif text.startswith("/check"):
            parts = text.split()
            if len(parts) < 2:
                send_message(chat_id, "⚠️ សូមបញ្ចូលឈ្មោះទំនិញ (ឧ: `/check shirt`)")
            else:
                item_name = parts[1].lower()
                stock = load_stock()
                if item_name in stock:
                    send_message(chat_id, f"🔍 ទំនិញ **{item_name}** សល់: **{stock[item_name]}**")
                else:
                    send_message(chat_id, f"❌ រកមិនឃើញទំនិញ '{item_name}' ទេ។")

        elif text.startswith("/add"):
            parts = text.split()
            if len(parts) < 3:
                send_message(chat_id, "⚠️ ទម្រង់ខុស! ប្រើប្រាស់: `/add [ឈ្មោះ] [ចំនួន]`")
            else:
                item_name = parts[1].lower()
                try:
                    qty = int(parts[2])
                    stock = load_stock()
                    stock[item_name] = stock.get(item_name, 0) + qty
                    save_stock(stock)
                    send_message(chat_id, f"✅ បានបន្ថែម {qty} ទៅលើ **{item_name}**! ស្តុកសរុប: {stock[item_name]}")
                except ValueError:
                    send_message(chat_id, "⚠️ ចំនួនត្រូវតែជាតួលេខ!")

        elif text.startswith("/sell"):
            parts = text.split()
            if len(parts) < 3:
                send_message(chat_id, "⚠️ ទម្រង់ខុស! ប្រើប្រាស់: `/sell [ឈ្មោះ] [ចំនួន]`")
            else:
                item_name = parts[1].lower()
                try:
                    qty = int(parts[2])
                    stock = load_stock()
                    if item_name not in stock or stock[item_name] < qty:
                        curr = stock.get(item_name, 0)
                        send_message(chat_id, f"❌ ស្តុក **{item_name}** មិនគ្រាន់ទេ។ សល់ត្រឹមតែ: {curr}")
                    else:
                        stock[item_name] -= qty
                        save_stock(stock)
                        send_message(chat_id, f"📉 បានលក់ចេញ {qty} ពី **{item_name}**! ស្តុកនៅសល់: {stock[item_name]}")
                except ValueError:
                    send_message(chat_id, "⚠️ ចំនួនត្រូវតែជាតួលេខ!")

if __name__ == "__main__":
    start_time = time.time()
    while time.time() - start_time < 45:
        process_messages()
        time.sleep(2)
