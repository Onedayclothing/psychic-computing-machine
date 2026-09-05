const { Telegraf } = require('telegraf');
const fs = require('fs');
const path = require('path');
const http = require('http');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
if (!BOT_TOKEN) {
    console.error('⚠️ សូមកំណត់ TELEGRAM_BOT_TOKEN!');
    process.exit(1);
}

const bot = new Telegraf(BOT_TOKEN);
const STOCK_FILE = path.join(__dirname, 'stock.json');

// បញ្ជីឈ្មោះផលិតផលទាំងអស់នៅលើ Website ស្របតាម Reference Code
const allProducts = {
    "182": "T-Shirt Polo Collab OneDay",
    "183": "Olive Green Mandarin Collar Long-Sleeve Shirt",
    "prod-2": "Outfit Smart Casual (Full Set)",
    "prod-3": "Elegant Women Dress"
};

function loadStock() {
    if (!fs.existsSync(STOCK_FILE)) return {};
    try {
        const data = fs.readFileSync(STOCK_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        return {};
    }
}

function saveStock(data) {
    fs.writeFileSync(STOCK_FILE, JSON.stringify(data, null, 4), 'utf8');
}

bot.start((ctx) => {
    ctx.reply(
        "សួស្តី! Bot គ្រប់គ្រងស្តុក Oneday Clothing បានតភ្ជាប់ជាមួយប្រព័ន្ធរៀបចំរួចរាល់!\n\n" +
        "បញ្ជី Commands:\n" +
        "👉 `/stock` - មើលបញ្ជីស្តុកផលិតផលទាំងអស់\n" +
        "👉 `/add [កូដ] [ខ្នាត] [ចំនួន]` (ឧ: `/add 182 m 5`)\n" +
        "👉 `/sell [កូដ] [ខ្នាត] [ចំនួន]` (ឧ: `/sell 182 m 2`)"
    );
});

// Command /stock នឹងបង្ហាញគ្រប់ផលិតផលទាំងអស់នៅលើ Website តែម្ដង
bot.command(['stock', 'list'], (ctx) => {
    const stock = loadStock();
    let resp = "📦 **បញ្ជីស្តុកផលិតផលទាំងអស់ (Oneday Clothing):**\n\n";

    for (const [code, name] of Object.entries(allProducts)) {
        let productStock = stock[code] || {};
        let s = productStock["S"] ?? 0;
        let m = productStock["M"] ?? 0;
        let l = productStock["L"] ?? 0;
        let xl = productStock["XL"] ?? 0;
        let xxl = productStock["XXL"] ?? 0;

        resp += `🔹 **${name}** (Ref: ${code})\n`;
        resp += `SIZE : S:${s} | M:${m} | L:${l} | XL:${xl} | XXL:${xxl}\n\n`;
    }

    ctx.reply(resp, { parse_mode: 'Markdown' });
});

bot.command('add', (ctx) => {
    const args = ctx.message.text.split(' ').slice(1);
    if (args.length < 3) {
        return ctx.reply("⚠️ ទម្រង់ខុស! ប្រើប្រាស់: `/add [កូដ] [ខ្នាត] [ចំនួន]`", { parse_mode: 'Markdown' });
    }

    const itemCode = args[0];
    const size = args[1].toUpperCase();
    const qty = parseInt(args[2]);

    if (isNaN(qty)) return ctx.reply("⚠️ ចំនួនត្រូវតែជាតួលេខ!");
    if (!allProducts[itemCode]) {
        return ctx.reply(`⚠️ មិនមានកូដទំនិញ '${itemCode}' ນີ້នៅលើ Website ទេ!`);
    }

    const stock = loadStock();
    if (!stock[itemCode]) {
        stock[itemCode] = { "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0 };
    }
    if (!(size in stock[itemCode])) stock[itemCode][size] = 0;

    stock[itemCode][size] += qty;
    saveStock(stock);

    ctx.reply(`✅ បានបន្ថែម ${qty} ទៅកូដ \`${itemCode}\` (${allProducts[itemCode]}) ខ្នាត ${size}!\nស្តុកសរុប: ${stock[itemCode][size]}`, { parse_mode: 'Markdown' });
});

bot.command('sell', (ctx) => {
    const args = ctx.message.text.split(' ').slice(1);
    if (args.length < 3) {
        return ctx.reply("⚠️ ទម្រង់ខុស! ប្រើប្រាស់: `/sell [កូដ] [ខ្នាត] [ចំនួន]`", { parse_mode: 'Markdown' });
    }

    const itemCode = args[0];
    const size = args[1].toUpperCase();
    const qty = parseInt(args[2]);

    if (isNaN(qty)) return ctx.reply("⚠️ ចំនួនត្រូវតែជាតួលេខ!");
    if (!allProducts[itemCode]) {
        return ctx.reply(`⚠️ មិនមានកូដទំនិញ '${itemCode}' នេះនៅលើ Website ទេ!`);
    }

    const stock = loadStock();
    if (!stock[itemCode] || stock[itemCode][size] < qty) {
        const currentQty = stock[itemCode] ? stock[itemCode][size] || 0 : 0;
        return ctx.reply(`❌ ស្តុកកូដ \`${itemCode}\` ខ្នាត ${size} មិនគ្រាន់ទេ។ សល់ត្រឹមតែ: ${currentQty}`, { parse_mode: 'Markdown' });
    }

    stock[itemCode][size] -= qty;
    saveStock(stock);

    ctx.reply(`📉 បានលក់ចេញ ${qty} ពីកូដ \`${itemCode}\` (${allProducts[itemCode]}) ខ្នាត ${size}!\nនៅសល់: ${stock[itemCode][size]}`, { parse_mode: 'Markdown' });
});

bot.launch();
console.log('🤖 Telegram Bot is running...');

const PORT = process.env.PORT || 3000;
http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Oneday Clothing Bot is running!\n');
}).listen(PORT, () => {
    console.log(`🌐 Server is listening on port ${PORT}`);
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
