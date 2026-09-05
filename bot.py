import os
import json
import requests

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

def main():
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
                "👉 `/stock` - មើលបញ្ជីស្តុក\n"
                "👉 `/add [កូដ] [ខ្នាត] [ចំនួន]` (ឧ: `/add 182 m 5`)\n"
                "👉 `/sell [កូដ] [ខ្នាត] [ចំនួន]` (ឧ: `/sell 182 m 2`)"
            )
            send_message(chat_id, msg)

        elif text in ["/stock", "/list"]:
            stock = load_stock()
            if not stock:
                send_message(chat_id, "📦 គ្មានទំនិញក្នុងស្តុកទេ។")
            else:
                resp = "📦 **បញ្ជីស្តុក Oneday Clothing:**\n"
                for code, sizes in stock.items():
                    resp += f"- `{code}`: {sizes}\n"
                send_message(chat_id, resp)

        elif text.startswith("/add") or text.startswith("/sell"):
            parts = text.split()
            if len(parts) < 4:
                send_message(chat_id, "⚠️ ទម្រង់ខុស! ប្រើប្រាស់: `/add [កូដ] [ខ្នាត] [ចំនួន]` (ឧ: `/add 182 m 5`)")
                continue
            
            action = parts[0]
            item_code = parts[1]
            size = parts[2].upper()
            try:
                qty = int(parts[3])
            except ValueError:
                send_message(chat_id, "⚠️ ចំនួនត្រូវតែជាតួលេខ!")
                continue

            stock = load_stock()
            if item_code not in stock:
                stock[item_code] = {"S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0}
            
            if size not in stock[item_code]:
                stock[item_code][size] = 0

            if action == "/add":
                stock[item_code][size] += qty
                save_stock(stock)
                send_message(chat_id, f"✅ បានបន្ថែម {qty} ទៅកូដ `{item_code}` (ខ្នាត {size})! សល់សរុប: {stock[item_code][size]}")
            elif action == "/sell":
                if stock[item_code][size] < qty:
                    send_message(chat_id, f"❌ ស្តុកកូដ `{item_code}` ខ្នាត {size} មិនគ្រាន់ទេ។ សល់ត្រឹមតែ: {stock[item_code][size]}")
                else:
                    stock[item_code][size] -= qty
                    save_stock(stock)
                    send_message(chat_id, f"📉 បានលក់ចេញ {qty} ពីកូដ `{item_code}` (ខ្នាត {size})! នៅសល់: {stock[item_code][size]}")

if __name__ == "__main__":
    main()
