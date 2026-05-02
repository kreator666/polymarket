#!/usr/bin/env python3
"""
根据 Polymarket 知识库实操建议：
1. Gamma API 按 liquidity 筛选活跃事件
2. CLOB API 查订单簿计算有效深度
3. 输出深度 >= 阈值的标的
"""

import requests
import concurrent.futures
import json
from dataclasses import dataclass
from typing import List, Optional

# ============ 配置 ============
GAMMA_API = "https://gamma-api.polymarket.com/events"
CLOB_API = "https://clob.polymarket.com/book"

DEPTH_THRESHOLD = 1000.0      # USDC，深度阈值
MAX_SLIPPAGE = 0.02           # 美元，可接受滑点（如最优价±2美分）
TOP_EVENTS = 50               # 先取流动性前N的事件（加过滤时建议适当调大）
MAX_WORKERS = 10              # 并发查询订单簿
MIN_SPREAD_FILTER = 0.10      # 跳过价差过大的市场（显示价格会变成最近成交价）

# 类别过滤：设为 None 表示不过滤；例如 "Sports", "Politics", "Crypto", "Culture"
# 也支持子类别，如 "NBA", "Soccer", "NFL"
CATEGORY_FILTER = "Sports"    # 示例：只跑体育类


@dataclass
class MarketDepth:
    event_title: str
    market_question: str
    slug: str
    token_id: str
    best_bid: float
    best_ask: float
    spread: float
    buy_depth: float   # 买入Yes需要的USDC深度
    sell_depth: float  # 卖出Yes能换回的USDC深度


def fetch_top_events(limit: int = TOP_EVENTS, category: Optional[str] = CATEGORY_FILTER) -> List[dict]:
    """从 Gamma API 获取按流动性排序的活跃事件，支持按类别标签过滤"""
    params = {
        "active": "true",
        "closed": "false",
        "order": "liquidity",
        "ascending": "false",
        "limit": limit,
    }
    resp = requests.get(GAMMA_API, params=params, timeout=30)
    resp.raise_for_status()
    events = resp.json()

    if category:
        cat_lower = category.lower()
        filtered = []
        for evt in events:
            tags = evt.get("tags", [])
            match = any(
                cat_lower == t.get("label", "").lower() or cat_lower == t.get("slug", "").lower()
                for t in tags
            )
            if match:
                filtered.append(evt)
        events = filtered

    return events


def extract_orderbook_markets(events: List[dict]) -> List[dict]:
    """提取所有启用了订单簿的市场，返回带 token_id 的列表"""
    markets = []
    for evt in events:
        for m in evt.get("markets", []):
            if not m.get("enableOrderBook"):
                continue
            raw_token_ids = m.get("clobTokenIds")
            if not raw_token_ids:
                continue
            # API 返回的是 JSON 字符串，需要解析
            try:
                token_ids = json.loads(raw_token_ids) if isinstance(raw_token_ids, str) else raw_token_ids
            except Exception:
                continue
            if not token_ids or len(token_ids) == 0:
                continue
            # 通常 index 0 是 Yes，index 1 是 No
            markets.append({
                "event_title": evt.get("title", ""),
                "market_question": m.get("question", ""),
                "slug": m.get("slug", ""),
                "token_id": str(token_ids[0]),  # Yes token
                "best_bid": m.get("bestBid"),
                "best_ask": m.get("bestAsk"),
                "liquidityClob": m.get("liquidityClob"),
            })
    return markets


def calculate_book_depth(token_id: str, max_slippage: float = MAX_SLIPPAGE) -> Optional[dict]:
    """查询 CLOB 订单簿并计算买卖深度"""
    try:
        resp = requests.get(CLOB_API, params={"token_id": token_id}, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        bids = data.get("bids", [])
        asks = data.get("asks", [])

        if not bids or not asks:
            return None

        # bids 按价格从低到高，最优 bid 在最后
        best_bid = float(bids[-1]["price"])
        # asks 按价格从高到低，最优 ask 在最后
        best_ask = float(asks[-1]["price"])
        spread = best_ask - best_bid

        # 买入深度：从最优 ask 往上累加（容忍 max_slippage 的价格上涨）
        buy_depth = 0.0
        max_buy_price = best_ask + max_slippage
        for a in reversed(asks):  # 从最优 ask 向更高价格遍历
            p = float(a["price"])
            s = float(a["size"])
            if p <= max_buy_price:
                buy_depth += p * s
            else:
                break

        # 卖出深度：从最优 bid 往下累加（容忍 max_slippage 的价格下跌）
        sell_depth = 0.0
        min_sell_price = best_bid - max_slippage
        for b in reversed(bids):  # 从最优 bid 向更低价格遍历
            p = float(b["price"])
            s = float(b["size"])
            if p >= min_sell_price:
                sell_depth += p * s
            else:
                break

        return {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "buy_depth": buy_depth,
            "sell_depth": sell_depth,
        }
    except Exception as e:
        # 生产环境可以打日志
        return None


def analyze_market(m: dict) -> Optional[MarketDepth]:
    """分析单个市场的深度"""
    depth_info = calculate_book_depth(m["token_id"])
    if not depth_info:
        return None

    # 如果价差过大，跳过（知识库提到价差>0.10显示最近成交价，流动性差）
    if depth_info["spread"] > MIN_SPREAD_FILTER:
        return None

    return MarketDepth(
        event_title=m["event_title"],
        market_question=m["market_question"],
        slug=m["slug"],
        token_id=m["token_id"],
        best_bid=depth_info["best_bid"],
        best_ask=depth_info["best_ask"],
        spread=depth_info["spread"],
        buy_depth=depth_info["buy_depth"],
        sell_depth=depth_info["sell_depth"],
    )


def main():
    filter_info = f"类别: {CATEGORY_FILTER}" if CATEGORY_FILTER else "类别: 全部"
    print("=" * 60)
    print("Polymarket 深度筛选器")
    print(f"阈值: {DEPTH_THRESHOLD} USDC | 滑点容忍: {MAX_SLIPPAGE} USD | {filter_info}")
    print("=" * 60)

    # 1. 获取高流动性事件
    print(f"\n[1/4] 获取流动性前 {TOP_EVENTS} 的活跃事件...")
    if CATEGORY_FILTER:
        print(f"      过滤类别: {CATEGORY_FILTER}")
    events = fetch_top_events()
    print(f"      获取到 {len(events)} 个事件")

    # 2. 提取可交易的市场
    print("\n[2/4] 提取启用了订单簿的市场...")
    markets = extract_orderbook_markets(events)
    print(f"      提取到 {len(markets)} 个市场")

    # 3. 并发查询订单簿深度
    print(f"\n[3/4] 并发查询 {len(markets)} 个市场的订单簿...")
    results: List[MarketDepth] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(analyze_market, m): m for m in markets}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
    print(f"      成功分析 {len(results)} 个市场")

    # 4. 筛选深度足够的标的
    print(f"\n[4/4] 筛选深度 >= {DEPTH_THRESHOLD} USDC 的标的...")
    # 策略：买入深度和卖出深度都足够，才能顺畅进出
    deep_markets = [
        r for r in results
        if r.buy_depth >= DEPTH_THRESHOLD and r.sell_depth >= DEPTH_THRESHOLD
    ]
    # 按最小深度排序（取最充裕的）
    deep_markets.sort(key=lambda x: min(x.buy_depth, x.sell_depth), reverse=True)

    top10 = deep_markets[:10]

    print(f"\n{'='*60}")
    print(f"前 {len(top10)} 个深度充足的标的（双侧深度 >= {DEPTH_THRESHOLD} USDC）")
    print(f"{'='*60}\n")

    if not top10:
        print("未找到满足条件的标的，建议：")
        print("  - 降低 DEPTH_THRESHOLD")
        print("  - 增大 TOP_EVENTS 扫描更多市场")
        print("  - 放宽 MAX_SLIPPAGE 容忍更大滑点")
        return

    for i, m in enumerate(top10, 1):
        min_depth = min(m.buy_depth, m.sell_depth)
        print(f"#{i:02d} | {m.event_title}")
        print(f"      市场: {m.market_question}")
        print(f"      Slug: {m.slug}")
        print(f"      Token: {m.token_id}")
        print(f"      价格: Bid {m.best_bid:.3f} / Ask {m.best_ask:.3f} (价差 {m.spread:.3f})")
        print(f"      买入深度: {m.buy_depth:,.2f} USDC | 卖出深度: {m.sell_depth:,.2f} USDC")
        print(f"      最小深度: {min_depth:,.2f} USDC")
        print()

    # 同时输出便于复制粘贴的 slug 列表
    print("-" * 60)
    print("Slug 列表（可直接用于前端 URL）:")
    for m in top10:
        print(f"  https://polymarket.com/event/{m.slug}")


if __name__ == "__main__":
    main()
