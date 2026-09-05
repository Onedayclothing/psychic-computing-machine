bot.command(['stock', 'list'], (ctx) => {
    const stock = loadStock();
    if (Object.keys(stock).length === 0) {
        return ctx.reply("📦 គ្មានទំនិញក្នុងស្តុកទេ។");
    }

    let resp = "📦 **បញ្ជីស្តុក Oneday Clothing:**\n\n";
    resp += "🔹 **ផ្នែក បុរស**\n";
    resp += "• **អាវ**\n\n";

    const productNames = {
        "182": "T-Shirt Polo Collab OneDay",
        "183": "Olive Green Mandarin Collar Long-Sleeve Shirt"
    };

    for (const [code, sizes] of Object.entries(stock)) {
        let name = productNames[code] || `Product Ref:${code}`;
        let s = sizes["S"] ?? 0;
        let m = sizes["M"] ?? 0;
        let l = sizes["L"] ?? 0;
        let xl = sizes["XL"] ?? 0;
        let xxl = sizes["XXL"] ?? 0;

        resp += `${name}\n`;
        resp += `SIZE : S:${s} | M:${m} | L:${l} | XL:${xl} | XXL:${xxl}\n\n`;
    }

    ctx.reply(resp, { parse_mode: 'Markdown' });
});
