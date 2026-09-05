const { Telegraf } = require('telegraf');
const fs = require('fs');
const path = require('path');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
if (!BOT_TOKEN) {
    console.error('⚠️ សូមកំណត់ TELEGRAM_BOT_TOKEN ក្នុង Environment Variables!');
    process.exit(1);
}

const bot = new Telegraf(BOT_TOKEN);
const STOCK_FILE = path.join(__dirname, 'stock.json');

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
        "សួស្តី! Bot គ្រប់គ្រងស្តុក Oneday Clothing បានដំណើរការជោគជ័យហើយ!\n\n" +
        "បញ្ជី Commands:\n" +
        "👉 `/stock` - មើលបញ្ជីស្តុក\n" +
        "👉 `/add [កូដ] [ខ្នាត] [ចំនួន]` (ឧ: `/add 182 m 5`)\n" +
        "👉 `/sell [កូដ] [ខ្នាត] [ចំនួន]` (ឧ: `/sell 182 m 2`)"
    );
});

bot.command(['stock', 'list'], (ctx) => {
    const stock = loadStock();
    if (Object.keys(stock).length === 0) {
        return ctx.reply("📦 គ្មានទំនិញក្នុងស្តុកទេ។");
    }
    let resp = "📦 **បញ្ជីស្តុក Oneday Clothing:**\n";
    for (const [code, sizes] of Object.entries(stock)) {
        resp += `- \`${code}\`: ${JSON.stringify(sizes)}\n`;
    }
    ctx.reply(resp, { parse_mode: 'Markdown' });
});

bot.command('add', (ctx) => {
    const args = ctx.message.text.split(' ').slice(1);
    if (args.length < 3) {
        return ctx.reply("⚠️ ទម្រង់ខុស! ប្រើប្រាស់: `/add [កូដ] [ខ្នាត] [ចំនួន]` (ឧ: `/add 182 m 5`)", { parse_mode: 'Markdown' });
    }

    const itemCode = args[0];
    const size = args[1].toUpperCase();
    const qty = parseInt(args[2]);

    if (isNaN(qty)) {
        return ctx.reply("⚠️ ចំនួនត្រូវតែជាតួលេខ!");
    }

    const stock = loadStock();
    if (!stock[itemCode]) {
        stock[itemCode] = { "S": 0, "M": 0, "L": 0, "XL": 0, "XXL": 0 };
    }
    if (!(size in stock[itemCode])) {
        stock[itemCode][size] = 0;
    }

    stock[itemCode][size] += qty;
    saveStock(stock);

    ctx.reply(`✅ បានបន្ថែម ${qty} ទៅកូដ \`${itemCode}\` (ខ្នាត ${size})! ស្តុកសរុប: ${stock[itemCode][size]}`, { parse_mode: 'Markdown' });
});

bot.command('sell', (ctx) => {
    const args = ctx.message.text.split(' ').slice(1);
    if (args.length < 3) {
        return ctx.reply("⚠️ ទម្រង់ខុស! ប្រើប្រាស់: `/sell [កូដ] [ខ្នាត] [ចំនួន]` (ឧ: `/sell 182 m 2`)", { parse_mode: 'Markdown' });
    }

    const itemCode = args[0];
    const size = args[1].toUpperCase();
    const qty = parseInt(args[2]);

    if (isNaN(qty)) {
        return ctx.reply("⚠️ ចំនួនត្រូវតែជាតួលេខ!");
    }

    const stock = loadStock();
    if (!stock[itemCode] || stock[itemCode][size] < qty) {
        const currentQty = stock[itemCode] ? stock[itemCode][size] || 0 : 0;
        return ctx.reply(`❌ ស្តុកកូដ \`${itemCode}\` ខ្នាត ${size} មិនគ្រាន់ទេ។ សល់ត្រឹមតែ: ${currentQty}`, { parse_mode: 'Markdown' });
    }

    stock[itemCode][size] -= qty;
    saveStock(stock);

    ctx.reply(`📉 បានលក់ចេញ ${qty} ពីកូដ \`${itemCode}\` (ខ្នាត ${size})! នៅសល់: ${stock[itemCode][size]}`, { parse_mode: 'Markdown' });
});

bot.launch();
console.log('🤖 Telegram Bot (Node.js) is running...');

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
