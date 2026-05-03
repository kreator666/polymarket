require("dotenv").config();
const { PolymarketTrader, Side, OrderType } = require("./polymarket_trader");

async function main() {
    console.log("========================================");
    console.log("Polymarket 交易示例");
    console.log("========================================");

    const trader = new PolymarketTrader();

    try {
        await trader.initialize();

        const args = process.argv.slice(2);
        const command = args[0];

        switch (command) {
            case "markets":
                await listMarkets(trader, args[1]);
                break;

            case "orderbook":
                await showOrderbook(trader, args[1]);
                break;

            case "buy":
                await placeBuyOrder(trader, args[1], parseFloat(args[2]), parseFloat(args[3]));
                break;

            case "sell":
                await placeSellOrder(trader, args[1], parseFloat(args[2]), parseFloat(args[3]));
                break;

            case "orders":
                await listOpenOrders(trader);
                break;

            case "trades":
                await listTrades(trader);
                break;

            case "cancel":
                await cancelOrder(trader, args[1]);
                break;

            case "invest":
                await investInFilteredMarkets(trader, args[1], parseFloat(args[2]), parseInt(args[3]));
                break;

            case "info":
                await showMarketInfo(trader, args[1]);
                break;

            default:
                showHelp();
        }

    } catch (error) {
        console.error("\n错误:", error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

function showHelp() {
    console.log(`
用法: node scripts/trading_example.js <command> [options]

命令:
  markets <json_file>              显示筛选结果中的市场列表
  orderbook <token_id>             显示指定代币的订单簿
  buy <token_id> <amount> <price>  创建买单 (限价单)
  sell <token_id> <shares> <price> 创建卖单 (限价单)
  orders                            列出所有未成交订单
  trades                            列出交易历史
  cancel <order_id>                 取消指定订单
  invest <json_file> [amount] [max] 从筛选结果投资
  info <token_id>                   显示市场详细信息

示例:
  # 查看筛选的市场
  node scripts/trading_example.js markets high_value_markets_20260502_214810.json

  # 查看订单簿
  node scripts/trading_example.js orderbook "123456..."

  # 创建买单 (买入 $100, 价格 $0.85)
  node scripts/trading_example.js buy "123456..." 100 0.85

  # 从筛选结果投资 (每个市场 $50, 最多 5 个市场)
  node scripts/trading_example.js invest high_value_markets_20260502_214810.json 50 5

配置:
  在 .env 文件中设置:
  - PRIVATE_KEY: 你的私钥
  - SIGNATURE_TYPE: 签名类型 (0=EOA, 1=POLY_PROXY, 2=GNOSIS_SAFE)
  - FUNDER_ADDRESS: 资金账户地址 (类型 1 或 2 时需要)

注意:
  - 下单前请确保你的资金账户有足够的 USDC.e 余额
  - 请确保已授权 Exchange 合约使用你的代币
  - 测试时请先在小金额上验证
    `);
}

async function listMarkets(trader, jsonFilePath) {
    if (!jsonFilePath) {
        console.error("请提供 JSON 文件路径");
        return;
    }

    const data = trader.readFilteredMarkets(jsonFilePath);
    const markets = data.top_by_liquidity;

    console.log(`\n========================================`);
    console.log(`筛选结果 - 流动性最高的 ${markets.length} 个市场`);
    console.log(`========================================`);

    markets.forEach((market, index) => {
        trader.displayMarketInfo(market, index);
    });
}

async function showOrderbook(trader, tokenId) {
    if (!tokenId) {
        console.error("请提供 Token ID");
        return;
    }

    console.log(`\n订单簿 - Token ID: ${tokenId}`);

    const book = await trader.getOrderbook(tokenId);
    const tickSize = await trader.getTickSize(tokenId);
    const negRisk = await trader.getNegRisk(tokenId);

    console.log(`\n市场信息:`);
    console.log(`  Tick Size: ${tickSize}`);
    console.log(`  Neg Risk: ${negRisk}`);

    if (book.bids && book.bids.length > 0) {
        console.log(`\n买单 (Bids):`);
        const topBids = book.bids.slice(-5).reverse();
        topBids.forEach((bid, i) => {
            console.log(`  ${i + 1}. 价格: ${bid.price}, 数量: ${bid.size}`);
        });
    }

    if (book.asks && book.asks.length > 0) {
        console.log(`\n卖单 (Asks):`);
        const topAsks = book.asks.slice(-5).reverse();
        topAsks.forEach((ask, i) => {
            console.log(`  ${i + 1}. 价格: ${ask.price}, 数量: ${ask.size}`);
        });
    }
}

async function placeBuyOrder(trader, tokenId, amount, price) {
    if (!tokenId || !amount || !price) {
        console.error("用法: buy <token_id> <amount> <price>");
        return;
    }

    const result = await trader.placeBuyOrder(tokenId, amount, price);
    console.log(`\n订单创建结果:`);
    console.log(JSON.stringify(result, null, 2));
}

async function placeSellOrder(trader, tokenId, shares, price) {
    if (!tokenId || !shares || !price) {
        console.error("用法: sell <token_id> <shares> <price>");
        return;
    }

    const result = await trader.placeSellOrder(tokenId, shares, price);
    console.log(`\n订单创建结果:`);
    console.log(JSON.stringify(result, null, 2));
}

async function listOpenOrders(trader) {
    const orders = await trader.getOpenOrders();

    if (orders.length === 0) {
        console.log("\n没有未成交订单");
        return;
    }

    console.log(`\n========================================`);
    console.log(`未成交订单 (${orders.length})`);
    console.log(`========================================`);

    orders.forEach((order, index) => {
        console.log(`\n[#${index + 1}]`);
        console.log(`  订单 ID: ${order.id}`);
        console.log(`  状态: ${order.status}`);
        console.log(`  方向: ${order.side}`);
        console.log(`  价格: ${order.price}`);
        console.log(`  原始数量: ${order.original_size}`);
        console.log(`  已成交: ${order.size_matched}`);
        console.log(`  市场 ID: ${order.market}`);
        console.log(`  Token ID: ${order.asset_id}`);
    });
}

async function listTrades(trader) {
    const trades = await trader.getTrades();

    if (trades.length === 0) {
        console.log("\n没有交易历史");
        return;
    }

    console.log(`\n========================================`);
    console.log(`交易历史 (${trades.length})`);
    console.log(`========================================`);

    trades.forEach((trade, index) => {
        console.log(`\n[#${index + 1}]`);
        console.log(`  交易 ID: ${trade.id}`);
        console.log(`  状态: ${trade.status}`);
        console.log(`  方向: ${trade.side}`);
        console.log(`  价格: ${trade.price}`);
        console.log(`  数量: ${trade.size}`);
        console.log(`  结果: ${trade.outcome}`);
        if (trade.transaction_hash) {
            console.log(`  交易哈希: ${trade.transaction_hash}`);
        }
    });
}

async function cancelOrder(trader, orderId) {
    if (!orderId) {
        console.error("请提供订单 ID");
        return;
    }

    await trader.cancelOrder(orderId);
}

async function investInFilteredMarkets(trader, jsonFilePath, amount, maxMarkets) {
    if (!jsonFilePath) {
        console.error("请提供 JSON 文件路径");
        return;
    }

    const investAmount = amount || 50;
    const max = maxMarkets || 5;

    console.log(`\n投资配置:`);
    console.log(`  单市场金额: $${investAmount}`);
    console.log(`  最大市场数: ${max}`);
    console.log(`  订单类型: 限价单`);

    const results = await trader.investInFilteredMarkets(
        jsonFilePath,
        investAmount,
        max,
        false
    );

    return results;
}

async function showMarketInfo(trader, tokenId) {
    if (!tokenId) {
        console.error("请提供 Token ID");
        return;
    }

    console.log(`\n市场信息 - Token ID: ${tokenId}`);

    const tickSize = await trader.getTickSize(tokenId);
    const negRisk = await trader.getNegRisk(tokenId);

    console.log(`\n基础信息:`);
    console.log(`  Tick Size: ${tickSize}`);
    console.log(`  Neg Risk: ${negRisk}`);

    await showOrderbook(trader, tokenId);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
