#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高价标的筛选器
功能：
1. 获取价格大于0.9的交易标的，记录前100个
2. 根据流动性从这100个中筛选出流动性最高的20个

根据 Polymarket 知识库：
- 价格显示为买卖价差的中间价：(bestBid + bestAsk) / 2
- 如果价差超过 $0.10，则显示最近成交价
- 流动性字段：liquidity（事件级别）、liquidityClob（市场级别）
"""

import sys
import io
import requests
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


@dataclass
class HighPriceMarket:
    """高价市场数据结构"""
    event_title: str
    market_question: str
    slug: str
    token_id: str
    condition_id: str
    best_bid: float
    best_ask: float
    spread: float
    mid_price: float
    last_trade_price: Optional[float]
    displayed_price: float
    event_liquidity: float
    market_liquidity: float
    volume_24hr: float
    volume: float
    enable_order_book: bool
    
    @property
    def total_liquidity(self) -> float:
        """总流动性（取事件和市场流动性的最大值）"""
        return max(self.event_liquidity, self.market_liquidity)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "total_liquidity": self.total_liquidity,
            "url": f"https://polymarket.com/event/{self.slug}",
            "extracted_at": datetime.now().isoformat()
        }


class HighPriceMarketFilter:
    """高价标的筛选器"""
    
    GAMMA_API = "https://gamma-api.polymarket.com"
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
    
    def fetch_events(
        self,
        limit: int = 200,
        active: bool = True,
        closed: bool = False,
        order: str = "liquidity",
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        从 Gamma API 获取事件列表
        
        Args:
            limit: 返回数量限制（需要获取足够多的事件来筛选出100个高价标的）
            active: 是否只获取活跃事件
            closed: 是否包含已关闭事件
            order: 排序字段
            ascending: 是否升序
        
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
        
        url = f"{self.GAMMA_API}/events"
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"获取事件时出错: {e}")
            return []
    
    def calculate_displayed_price(
        self,
        best_bid: Optional[float],
        best_ask: Optional[float],
        last_trade_price: Optional[float]
    ) -> Dict[str, Any]:
        """
        计算显示价格
        
        根据知识库：
        - 显示的价格是买卖价差的中间价
        - 如果价差超过 $0.10，则显示最近成交价
        
        Args:
            best_bid: 最优买价
            best_ask: 最优卖价
            last_trade_price: 最近成交价
        
        Returns:
            包含价格计算结果的字典
        """
        if best_bid is None:
            best_bid = 0.0
        if best_ask is None:
            best_ask = 0.0
        
        spread = best_ask - best_bid if best_bid and best_ask else 0.0
        
        if best_bid > 0 and best_ask > 0:
            mid_price = (best_bid + best_ask) / 2
        else:
            mid_price = 0.0
        
        if spread > 0.10 and last_trade_price is not None:
            displayed_price = last_trade_price
        elif mid_price > 0:
            displayed_price = mid_price
        elif last_trade_price is not None:
            displayed_price = last_trade_price
        else:
            displayed_price = 0.0
        
        return {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "mid_price": mid_price,
            "last_trade_price": last_trade_price,
            "displayed_price": displayed_price
        }
    
    def extract_markets_from_events(
        self,
        events: List[Dict[str, Any]],
        price_threshold: float = 0.9
    ) -> List[HighPriceMarket]:
        """
        从事件中提取市场，并筛选价格大于阈值的标的
        
        Args:
            events: 事件列表
            price_threshold: 价格阈值
        
        Returns:
            符合条件的市场列表
        """
        high_price_markets: List[HighPriceMarket] = []
        
        for evt in events:
            event_title = evt.get("title", "")
            event_liquidity = float(evt.get("liquidity", 0) or 0)
            volume_24hr = float(evt.get("volume24hr", 0) or 0)
            volume = float(evt.get("volume", 0) or 0)
            
            for m in evt.get("markets", []):
                best_bid_raw = m.get("bestBid")
                best_ask_raw = m.get("bestAsk")
                last_trade_price_raw = m.get("lastTradePrice")
                
                try:
                    best_bid = float(best_bid_raw) if best_bid_raw not in (None, "") else None
                    best_ask = float(best_ask_raw) if best_ask_raw not in (None, "") else None
                    last_trade_price = float(last_trade_price_raw) if last_trade_price_raw not in (None, "") else None
                except (ValueError, TypeError):
                    continue
                
                price_info = self.calculate_displayed_price(
                    best_bid, best_ask, last_trade_price
                )
                
                if price_info["displayed_price"] < price_threshold:
                    continue
                
                enable_order_book = m.get("enableOrderBook", False)
                market_liquidity = float(m.get("liquidityClob", 0) or 0)
                
                clob_token_ids = m.get("clobTokenIds")
                token_id = ""
                if clob_token_ids:
                    try:
                        token_ids = (
                            json.loads(clob_token_ids) 
                            if isinstance(clob_token_ids, str) 
                            else clob_token_ids
                        )
                        if token_ids and len(token_ids) > 0:
                            token_id = str(token_ids[0])
                    except Exception:
                        pass
                
                market = HighPriceMarket(
                    event_title=event_title,
                    market_question=m.get("question", ""),
                    slug=m.get("slug", ""),
                    token_id=token_id,
                    condition_id=m.get("conditionId", ""),
                    best_bid=price_info["best_bid"],
                    best_ask=price_info["best_ask"],
                    spread=price_info["spread"],
                    mid_price=price_info["mid_price"],
                    last_trade_price=price_info["last_trade_price"],
                    displayed_price=price_info["displayed_price"],
                    event_liquidity=event_liquidity,
                    market_liquidity=market_liquidity,
                    volume_24hr=volume_24hr,
                    volume=volume,
                    enable_order_book=enable_order_book
                )
                
                high_price_markets.append(market)
        
        return high_price_markets
    
    def find_high_price_markets(
        self,
        price_threshold: float = 0.9,
        initial_events: int = 500,
        top_by_price: int = 100,
        top_by_liquidity: int = 20
    ) -> Dict[str, Any]:
        """
        主方法：查找高价标的并按流动性筛选
        
        流程：
        1. 获取足够多的事件（默认500个，按流动性排序）
        2. 从事件中提取所有市场，并筛选价格 > 0.9 的标的
        3. 按价格从高到低排序，取前100个
        4. 从这100个中按流动性从高到低排序，取前20个
        
        Args:
            price_threshold: 价格阈值（默认0.9）
            initial_events: 初始获取的事件数量
            top_by_price: 按价格筛选后的数量（默认100）
            top_by_liquidity: 按流动性筛选后的数量（默认20）
        
        Returns:
            包含筛选结果的字典
        """
        print("=" * 70)
        print("Polymarket 高价标的筛选器")
        print(f"价格阈值: > {price_threshold} | 初始扫描: {initial_events} 个事件")
        print(f"按价格取前 {top_by_price} 个 → 按流动性取前 {top_by_liquidity} 个")
        print("=" * 70)
        
        print(f"\n[1/5] 获取前 {initial_events} 个事件（按流动性排序）...")
        events = self.fetch_events(limit=initial_events)
        print(f"      成功获取 {len(events)} 个事件")
        
        print(f"\n[2/5] 从事件中提取市场并筛选价格 > {price_threshold} 的标的...")
        high_price_markets = self.extract_markets_from_events(
            events, price_threshold
        )
        print(f"      找到 {len(high_price_markets)} 个价格 > {price_threshold} 的标的")
        
        if not high_price_markets:
            print("\n警告：未找到符合条件的标的")
            return {
                "price_threshold": price_threshold,
                "initial_events_count": len(events),
                "high_price_count": 0,
                "top_by_price": [],
                "top_by_liquidity": []
            }
        
        print(f"\n[3/5] 按价格从高到低排序，取前 {top_by_price} 个...")
        high_price_markets.sort(
            key=lambda x: (x.displayed_price, x.total_liquidity),
            reverse=True
        )
        
        top_by_price = high_price_markets[:top_by_price]
        print(f"      成功筛选出 {len(top_by_price)} 个高价标的")
        
        print(f"\n[4/5] 从这 {len(top_by_price)} 个中按流动性从高到低排序...")
        top_by_price_sorted_by_liquidity = sorted(
            top_by_price,
            key=lambda x: (x.total_liquidity, x.displayed_price),
            reverse=True
        )
        
        top_by_liquidity = top_by_price_sorted_by_liquidity[:top_by_liquidity]
        print(f"      成功筛选出 {len(top_by_liquidity)} 个流动性最高的标的")
        
        print(f"\n[5/5] 输出结果...")
        
        print(f"\n{'='*70}")
        print(f"阶段1结果：价格 > {price_threshold} 的前 {top_by_price} 个标的（按价格排序）")
        print(f"{'='*70}\n")
        
        for i, m in enumerate(top_by_price[:10], 1):
            print(f"#{i:02d} | 价格: {m.displayed_price:.3f} | 流动性: {m.total_liquidity:,.0f} USDC")
            print(f"      事件: {m.event_title}")
            print(f"      市场: {m.market_question}")
            print(f"      Slug: {m.slug}")
            print(f"      Bid: {m.best_bid:.3f} | Ask: {m.best_ask:.3f} | 价差: {m.spread:.3f}")
            if m.last_trade_price:
                print(f"      最近成交价: {m.last_trade_price:.3f}")
            print()
        
        print(f"\n{'='*70}")
        print(f"最终结果：流动性最高的前 {len(top_by_liquidity)} 个标的（从高价标的中筛选）")
        print(f"{'='*70}\n")
        
        for i, m in enumerate(top_by_liquidity, 1):
            print(f"#{i:02d} | 流动性: {m.total_liquidity:,.0f} USDC | 价格: {m.displayed_price:.3f}")
            print(f"      事件: {m.event_title}")
            print(f"      市场: {m.market_question}")
            print(f"      Slug: {m.slug}")
            print(f"      Token ID: {m.token_id}")
            print(f"      24h交易量: {m.volume_24hr:,.2f} USDC")
            print(f"      总交易量: {m.volume:,.2f} USDC")
            print(f"      订单簿启用: {'是' if m.enable_order_book else '否'}")
            print(f"      URL: https://polymarket.com/event/{m.slug}")
            print()
        
        print("-" * 70)
        print("Slug 列表（可直接用于前端 URL）:")
        for m in top_by_liquidity:
            print(f"  https://polymarket.com/event/{m.slug}")
        
        return {
            "price_threshold": price_threshold,
            "initial_events_count": len(events),
            "high_price_count": len(high_price_markets),
            "top_by_price_count": len(top_by_price),
            "top_by_liquidity_count": len(top_by_liquidity),
            "top_by_price": [m.to_dict() for m in top_by_price],
            "top_by_liquidity": [m.to_dict() for m in top_by_liquidity]
        }
    
    def save_results(
        self,
        results: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        保存结果到 JSON 文件
        
        Args:
            results: 筛选结果
            filename: 文件名（默认自动生成）
        
        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"high_price_markets_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {filename}")
        return filename


def main():
    """主函数"""
    filter = HighPriceMarketFilter()
    
    results = filter.find_high_price_markets(
        price_threshold=0.9,
        initial_events=500,
        top_by_price=100,
        top_by_liquidity=20
    )
    
    filter.save_results(results)
    
    return results


if __name__ == "__main__":
    main()
