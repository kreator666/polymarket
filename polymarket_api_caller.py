#!/usr/bin/env python3
"""
Polymarket API 调用脚本
基于现有功能封装，提供更便捷的调用接口

功能列表：
1. 深度筛选器 - 查找高流动性市场
2. Gamma API - 获取市场数据
3. CLOB API - 获取订单簿数据
"""

import requests
import concurrent.futures
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from enum import Enum


class Category(Enum):
    """Polymarket 市场类别枚举"""
    SPORTS = "Sports"
    POLITICS = "Politics"
    CRYPTO = "Crypto"
    CULTURE = "Culture"
    NBA = "NBA"
    SOCCER = "Soccer"
    NFL = "NFL"


class Side(Enum):
    """订单方向"""
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class MarketDepth:
    """市场深度数据结构"""
    event_title: str
    market_question: str
    slug: str
    token_id: str
    best_bid: float
    best_ask: float
    spread: float
    buy_depth: float
    sell_depth: float
    
    @property
    def min_depth(self) -> float:
        return min(self.buy_depth, self.sell_depth)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "min_depth": self.min_depth,
            "url": f"https://polymarket.com/event/{self.slug}"
        }


class PolymarketClient:
    """Polymarket API 客户端封装"""
    
    GAMMA_API = "https://gamma-api.polymarket.com"
    CLOB_API = "https://clob.polymarket.com"
    
    def __init__(self, timeout: int = 30, max_workers: int = 10):
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
    
    def get_events(
        self,
        limit: int = 50,
        active: bool = True,
        closed: bool = False,
        order: str = "liquidity",
        ascending: bool = False,
        category: Optional[str] = None,
        tag_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        从 Gamma API 获取事件列表
        
        Args:
            limit: 返回数量限制
            active: 是否只获取活跃事件
            closed: 是否包含已关闭事件
            order: 排序字段 (liquidity, volume_24hr, volume, end_date 等)
            ascending: 是否升序
            category: 按类别过滤 (如 "Sports", "Politics")
            tag_id: 按标签ID过滤
        
        Returns:
            事件列表
        """
        params = {
            "active": str(active).lower(),
            "closed": str(closed).lower(),
            "order": order,
            "ascending": str(ascending).lower(),
            "limit": limit,
        }
        
        if tag_id:
            params["tag_id"] = tag_id
        
        url = f"{self.GAMMA_API}/events"
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        events = resp.json()
        
        if category:
            cat_lower = category.lower()
            filtered = []
            for evt in events:
                tags = evt.get("tags", [])
                match = any(
                    cat_lower == t.get("label", "").lower() or 
                    cat_lower == t.get("slug", "").lower()
                    for t in tags
                )
                if match:
                    filtered.append(evt)
            events = filtered
        
        return events
    
    def get_event_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        通过 Slug 获取单个事件
        
        Args:
            slug: 事件的唯一标识符 (从 URL 中提取)
        
        Returns:
            事件详情
        """
        url = f"{self.GAMMA_API}/events/slug/{slug}"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError:
            return None
    
    def get_market_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        通过 Slug 获取单个市场
        
        Args:
            slug: 市场的唯一标识符
        
        Returns:
            市场详情
        """
        url = f"{self.GAMMA_API}/markets/slug/{slug}"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError:
            return None
    
    def get_orderbook(self, token_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定 token 的订单簿数据
        
        Args:
            token_id: CLOB token 标识符
        
        Returns:
            订单簿数据 (包含 bids 和 asks)
        """
        url = f"{self.CLOB_API}/book"
        params = {"token_id": token_id}
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None
    
    def calculate_depth(
        self,
        token_id: str,
        max_slippage: float = 0.02
    ) -> Optional[Dict[str, Any]]:
        """
        计算订单簿深度
        
        Args:
            token_id: CLOB token 标识符
            max_slippage: 可接受的最大滑点 (美元)
        
        Returns:
            深度计算结果
        """
        orderbook = self.get_orderbook(token_id)
        if not orderbook:
            return None
        
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])
        
        if not bids or not asks:
            return None
        
        best_bid = float(bids[-1]["price"])
        best_ask = float(asks[-1]["price"])
        spread = best_ask - best_bid
        
        buy_depth = 0.0
        max_buy_price = best_ask + max_slippage
        for a in reversed(asks):
            p = float(a["price"])
            s = float(a["size"])
            if p <= max_buy_price:
                buy_depth += p * s
            else:
                break
        
        sell_depth = 0.0
        min_sell_price = best_bid - max_slippage
        for b in reversed(bids):
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
            "sell_depth": sell_depth
        }


class DepthFilter:
    """市场深度筛选器"""
    
    def __init__(
        self,
        client: PolymarketClient,
        depth_threshold: float = 1000.0,
        max_slippage: float = 0.02,
        min_spread_filter: float = 0.10
    ):
        self.client = client
        self.depth_threshold = depth_threshold
        self.max_slippage = max_slippage
        self.min_spread_filter = min_spread_filter
    
    def extract_orderbook_markets(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """从事件中提取启用订单簿的市场"""
        markets = []
        for evt in events:
            for m in evt.get("markets", []):
                if not m.get("enableOrderBook"):
                    continue
                raw_token_ids = m.get("clobTokenIds")
                if not raw_token_ids:
                    continue
                try:
                    token_ids = (
                        json.loads(raw_token_ids) 
                        if isinstance(raw_token_ids, str) 
                        else raw_token_ids
                    )
                except Exception:
                    continue
                if not token_ids:
                    continue
                
                markets.append({
                    "event_title": evt.get("title", ""),
                    "market_question": m.get("question", ""),
                    "slug": m.get("slug", ""),
                    "token_id": str(token_ids[0]),
                })
        return markets
    
    def analyze_market(self, market: Dict[str, Any]) -> Optional[MarketDepth]:
        """分析单个市场的深度"""
        depth_info = self.client.calculate_depth(
            market["token_id"],
            self.max_slippage
        )
        if not depth_info:
            return None
        
        if depth_info["spread"] > self.min_spread_filter:
            return None
        
        if (depth_info["buy_depth"] < self.depth_threshold or 
            depth_info["sell_depth"] < self.depth_threshold):
            return None
        
        return MarketDepth(
            event_title=market["event_title"],
            market_question=market["market_question"],
            slug=market["slug"],
            token_id=market["token_id"],
            best_bid=depth_info["best_bid"],
            best_ask=depth_info["best_ask"],
            spread=depth_info["spread"],
            buy_depth=depth_info["buy_depth"],
            sell_depth=depth_info["sell_depth"]
        )
    
    def find_deep_markets(
        self,
        category: Optional[str] = "Sports",
        top_events: int = 50,
        limit: int = 10
    ) -> List[MarketDepth]:
        """
        查找高流动性市场
        
        Args:
            category: 类别过滤 (None 表示全市场)
            top_events: 初始扫描的事件数量
            limit: 返回结果数量限制
        
        Returns:
            符合条件的市场深度列表
        """
        events = self.client.get_events(
            limit=top_events,
            category=category
        )
        
        markets = self.extract_orderbook_markets(events)
        
        results: List[MarketDepth] = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.client.max_workers
        ) as executor:
            futures = {
                executor.submit(self.analyze_market, m): m 
                for m in markets
            }
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    results.append(res)
        
        results.sort(key=lambda x: x.min_depth, reverse=True)
        return results[:limit]


def demo_basic_usage():
    """演示基本用法"""
    print("=" * 60)
    print("Polymarket API 调用脚本 - 基本用法演示")
    print("=" * 60)
    
    client = PolymarketClient()
    
    print("\n[1] 获取体育类高流动性事件...")
    events = client.get_events(limit=10, category="Sports")
    print(f"    获取到 {len(events)} 个事件")
    
    if events:
        first_event = events[0]
        print(f"\n    第一个事件: {first_event.get('title', 'N/A')}")
        print(f"    Slug: {first_event.get('slug', 'N/A')}")
        print(f"    流动性: {first_event.get('liquidity', 'N/A')} USDC")
    
    print("\n[2] 使用深度筛选器查找高流动性市场...")
    depth_filter = DepthFilter(
        client=client,
        depth_threshold=1000.0,
        max_slippage=0.02
    )
    
    deep_markets = depth_filter.find_deep_markets(
        category="Sports",
        top_events=50,
        limit=5
    )
    
    print(f"\n    找到 {len(deep_markets)} 个深度充足的市场:\n")
    
    for i, market in enumerate(deep_markets, 1):
        print(f"    [{i}] {market.event_title}")
        print(f"        市场: {market.market_question}")
        print(f"        Slug: {market.slug}")
        print(f"        价格: Bid {market.best_bid:.3f} / Ask {market.best_ask:.3f}")
        print(f"        价差: {market.spread:.3f}")
        print(f"        买入深度: {market.buy_depth:,.2f} USDC")
        print(f"        卖出深度: {market.sell_depth:,.2f} USDC")
        print(f"        URL: https://polymarket.com/event/{market.slug}")
        print()
    
    print("=" * 60)
    print("演示完成")
    print("=" * 60)
    
    return deep_markets


def demo_advanced_usage():
    """演示高级用法"""
    print("\n" + "=" * 60)
    print("Polymarket API 调用脚本 - 高级用法演示")
    print("=" * 60)
    
    client = PolymarketClient()
    
    print("\n[1] 按不同排序方式获取事件...")
    
    print("\n    按 24小时交易量 排序:")
    events_by_volume = client.get_events(
        limit=5,
        order="volume_24hr"
    )
    for i, evt in enumerate(events_by_volume[:3], 1):
        print(f"    [{i}] {evt.get('title', 'N/A')}")
        print(f"        24h交易量: {evt.get('volume24hr', 'N/A')} USDC")
    
    print("\n    按 结束日期 排序 (即将到期的事件):")
    events_by_date = client.get_events(
        limit=5,
        order="end_date",
        ascending=True
    )
    for i, evt in enumerate(events_by_date[:3], 1):
        print(f"    [{i}] {evt.get('title', 'N/A')}")
        print(f"        结束日期: {evt.get('endDate', 'N/A')}")
    
    print("\n[2] 全市场扫描 (不限制类别)...")
    depth_filter = DepthFilter(
        client=client,
        depth_threshold=500.0,
        max_slippage=0.03
    )
    
    all_markets = depth_filter.find_deep_markets(
        category=None,
        top_events=100,
        limit=5
    )
    
    print(f"\n    全市场找到 {len(all_markets)} 个深度充足的市场")
    
    print("\n[3] 导出数据为 JSON...")
    if all_markets:
        market_data = [m.to_dict() for m in all_markets]
        json_output = json.dumps(market_data[:2], indent=2, ensure_ascii=False)
        print(f"\n    数据示例:\n{json_output}")
    
    print("\n" + "=" * 60)
    print("高级用法演示完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        demo_basic_usage()
        demo_advanced_usage()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
