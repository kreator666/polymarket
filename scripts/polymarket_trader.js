require("dotenv").config();
const { ClobClient, Side, OrderType } = require("@polymarket/clob-client");
const { Wallet } = require("ethers");
const fs = require("fs");
const path = require("path");

const CLOB_API_URL = process.env.CLOB_API_URL || "https://clob.polymarket.com";
const GAMMA_API_URL = process.env.GAMMA_API_URL || "https://gamma-api.polymarket.com";
const CHAIN_ID = parseInt(process.env.CHAIN_ID) || 137;
const SIGNATURE_TYPE = parseInt(process.env.SIGNATURE_TYPE) || 2;
const FUNDER_ADDRESS = process.env.FUNDER_ADDRESS;
const DEFAULT_TRADE_AMOUNT = parseFloat(process.env.DEFAULT_TRADE_AMOUNT) || 100;
const DEFAULT_SLIPPAGE = parseFloat(process.env.DEFAULT_SLIPPAGE) || 0.05;

class PolymarketTrader {
    constructor() {
        this.client = null;
        this.signer = null;
        this.apiCreds = null;
    }

    async initialize() {
        const privateKey = process.env.PRIVATE_KEY;
        if (!privateKey) {
            throw new Error("PRIVATE_KEY 环境变量未设置");
        }

        this.signer = new Wallet(privateKey);
        console.log(`使用钱包地址: ${this.signer.address}`);

        const tempClient = new ClobClient(
            CLOB_API_URL,
            CHAIN_ID,
            this.signer
        );

        console.log("派生 API 凭证...");
        this.apiCreds = await tempClient.createOrDeriveApiKey();
        console.log("API 凭证创建成功");

        const funder = FUNDER_ADDRESS || this.signer.address;
        this.client = new ClobClient(
            CLOB_API_URL,
            CHAIN_ID,
            this.signer,
            this.apiCreds,
            SIGNATURE_TYPE,
            funder
        );

        console.log(`CLOB 客户端初始化完成 (签名类型: ${SIGNATURE_TYPE})`);
        console.log(`资金账户地址: ${funder}`);
    }

    readFilteredMarkets(jsonFilePath) {
        const fullPath = path.resolve(jsonFilePath);
        if (!fs.existsSync(fullPath)) {
            throw new Error(`文件不存在: ${fullPath}`);
        }

        const data = JSON.parse(fs.readFileSync(fullPath, "utf-8"));
        console.log(`\n从 ${jsonFilePath} 读取筛选结果:`);
        console.log(`  价格范围: ${data.price_min} ~ ${data.price_max}`);
        console.log(`  总筛选数: ${data.filtered_count}`);
        console.log(`  流动性前 ${data.top_by_liquidity_count} 个标的`);

        return data;
    }

    displayMarketInfo(market, index) {
        console.log(`\n[#${index + 1}] ${market.event_title}`);
        console.log(`    市场: ${market.market_question}`);
        console.log(`    价格: ${market.displayed_price.toFixed(3)}`);
        console.log(`    流动性: ${market.total_liquidity.toLocaleString()} USDC`);
        console.log(`    Token ID: ${market.token_id}`);
        console.log(`    买入深度: ${market.bid_depth.toFixed(2)} USDC`);
        console.log(`    卖出深度: ${market.ask_depth.toFixed(2)} USDC`);
        console.log(`    事件 Slug: ${market.event_slug}`);
        console.log(`    URL: ${market.url}`);
    }

    async getOrderbook(tokenId) {
        const book = await this.client.getOrderBook(tokenId);
        return book;
    }

    async getTickSize(tokenId) {
        const tickSize = await this.client.getTickSize(tokenId);
        return tickSize;
    }

    async getNegRisk(tokenId) {
        const isNegRisk = await this.client.getNegRisk(tokenId);
        return isNegRisk;
    }

    async placeBuyOrder(tokenId, amount, price, orderType = OrderType.GTC) {
        const tickSize = await this.getTickSize(tokenId);
        const negRisk = await this.getNegRisk(tokenId);

        console.log(`\n创建买单:`);
        console.log(`  Token ID: ${tokenId}`);
        console.log(`  金额: $${amount}`);
        console.log(`  价格: $${price}`);
        console.log(`  Tick Size: ${tickSize}`);
        console.log(`  Neg Risk: ${negRisk}`);

        const response = await this.client.createAndPostOrder(
            {
                tokenID: tokenId,
                price: price,
                size: amount,
                side: Side.BUY,
            },
            {
                tickSize: tickSize,
                negRisk: negRisk,
            },
            orderType
        );

        console.log(`  订单 ID: ${response.orderID}`);
        console.log(`  状态: ${response.status}`);

        return response;
    }

    async placeSellOrder(tokenId, shares, price, orderType = OrderType.GTC) {
        const tickSize = await this.getTickSize(tokenId);
        const negRisk = await this.getNegRisk(tokenId);

        console.log(`\n创建卖单:`);
        console.log(`  Token ID: ${tokenId}`);
        console.log(`  份额: ${shares}`);
        console.log(`  价格: $${price}`);

        const response = await this.client.createAndPostOrder(
            {
                tokenID: tokenId,
                price: price,
                size: shares,
                side: Side.SELL,
            },
            {
                tickSize: tickSize,
                negRisk: negRisk,
            },
            orderType
        );

        console.log(`  订单 ID: ${response.orderID}`);
        console.log(`  状态: ${response.status}`);

        return response;
    }

    async placeMarketOrderBuy(tokenId, amount, worstPrice) {
        const tickSize = await this.getTickSize(tokenId);
        const negRisk = await this.getNegRisk(tokenId);

        console.log(`\n创建市价买单 (FOK):`);
        console.log(`  Token ID: ${tokenId}`);
        console.log(`  金额: $${amount}`);
        console.log(`  最差价格: $${worstPrice}`);

        const marketOrder = await this.client.createMarketOrder(
            {
                tokenID: tokenId,
                side: Side.BUY,
                amount: amount,
                price: worstPrice,
            },
            {
                tickSize: tickSize,
                negRisk: negRisk,
            }
        );

        const response = await this.client.postOrder(marketOrder, OrderType.FOK);
        console.log(`  订单 ID: ${response.orderID}`);
        console.log(`  状态: ${response.status}`);

        return response;
    }

    async getOpenOrders(marketId = null, assetId = null) {
        const params = {};
        if (marketId) params.market = marketId;
        if (assetId) params.asset_id = assetId;

        const orders = await this.client.getOpenOrders(params);
        console.log(`\n未成交订单数: ${orders.length}`);

        return orders;
    }

    async cancelOrder(orderId) {
        console.log(`\n取消订单: ${orderId}`);
        const response = await this.client.cancelOrder(orderId);
        console.log(`  取消结果:`, response);
        return response;
    }

    async getTrades(marketId = null) {
        const params = marketId ? { market: marketId } : {};
        const trades = await this.client.getTrades(params);
        console.log(`\n交易历史数: ${trades.length}`);
        return trades;
    }

    async getOrder(orderId) {
        const order = await this.client.getOrder(orderId);
        return order;
    }

    async investInFilteredMarkets(
        jsonFilePath,
        amountPerMarket = DEFAULT_TRADE_AMOUNT,
        maxMarkets = 5,
        useMarketOrder = false
    ) {
        const data = this.readFilteredMarkets(jsonFilePath);
        const markets = data.top_by_liquidity.slice(0, maxMarkets);

        console.log(`\n========================================`);
        console.log(`投资策略执行`);
        console.log(`========================================`);
        console.log(`单市场投资金额: $${amountPerMarket}`);
        console.log(`最大投资市场数: ${maxMarkets}`);
        console.log(`订单类型: ${useMarketOrder ? "市价单 (FOK)" : "限价单 (GTC)"}`);

        const results = [];

        for (let i = 0; i < markets.length; i++) {
            const market = markets[i];
            this.displayMarketInfo(market, i);

            try {
                const orderbook = await this.getOrderbook(market.token_id);
                const bestAsk = orderbook.asks?.[orderbook.asks.length - 1]?.price || market.best_ask;
                const bestBid = orderbook.bids?.[orderbook.bids.length - 1]?.price || market.best_bid;

                console.log(`    当前卖一价: ${bestAsk}`);
                console.log(`    当前买一价: ${bestBid}`);

                const worstPrice = Math.min(market.displayed_price * (1 + DEFAULT_SLIPPAGE), 0.99);

                if (useMarketOrder) {
                    const result = await this.placeMarketOrderBuy(
                        market.token_id,
                        amountPerMarket,
                        worstPrice
                    );
                    results.push({
                        market: market,
                        orderType: "MARKET",
                        result: result,
                        success: result.status === "matched" || result.status === "live",
                    });
                } else {
                    const limitPrice = market.displayed_price;
                    const result = await this.placeBuyOrder(
                        market.token_id,
                        amountPerMarket,
                        limitPrice
                    );
                    results.push({
                        market: market,
                        orderType: "LIMIT",
                        result: result,
                        success: result.status === "matched" || result.status === "live",
                    });
                }

                await new Promise(resolve => setTimeout(resolve, 500));

            } catch (error) {
                console.error(`    下单失败: ${error.message}`);
                results.push({
                    market: market,
                    error: error.message,
                    success: false,
                });
            }
        }

        console.log(`\n========================================`);
        console.log(`投资执行结果汇总`);
        console.log(`========================================`);
        results.forEach((r, i) => {
            const status = r.success ? "成功" : "失败";
            console.log(`[#${i + 1}] ${r.market.market_question.substring(0, 50)}... - ${status}`);
            if (r.result) {
                console.log(`    订单 ID: ${r.result.orderID}, 状态: ${r.result.status}`);
            }
            if (r.error) {
                console.log(`    错误: ${r.error}`);
            }
        });

        return results;
    }

    async cancelAllOrders() {
        const orders = await this.getOpenOrders();
        console.log(`\n取消所有 ${orders.length} 个订单...`);

        for (const order of orders) {
            await this.cancelOrder(order.id);
        }

        console.log(`所有订单已取消`);
    }
}

module.exports = {
    PolymarketTrader,
    Side,
    OrderType,
};
