#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高价值标的筛选器
功能：
1. 获取价格在 0.8~0.95 之间的交易标的
2. 确保买卖双方都有交易深度
3. 排除已经结束的事件
4. 根据流动性筛选出最高的标的

根据 Polymarket 知识库：
- 价格显示为买卖价差的中间价：(bestBid + bestAsk) / 2
- 如果价差超过 $0.10，则显示最近成交价
- 流动性字段：liquidity（事件级别）、liquidityClob（市场级别）
"""

import sys
import os
import requests
import json
import concurrent.futures
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'

def _print_safe(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                new_args.append(arg.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
            else:
                new_args.append(arg)
        print(*new_args, **kwargs)


@dataclass
class OrderBookDepth:
    """订单簿深度数据"""
    bid_depth: float = 0.0
    ask_depth: float = 0.0
    best_bid: float = 0.0
    best_ask: float = 0.0
    spread: float = 0.0
    has_both_sides: bool = False


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
    end_date: Optional[str] = None
    is_active: bool = True
    bid_depth: float = 0.0
    ask_depth: float = 0.0
    orderbook_check_passed: bool = False
    
    @property
    def total_liquidity(self) -> float:
        """总流动性（取事件和市场流动性的最大值）"""
        return max(self.event_liquidity, self.market_liquidity)
    
    @property
    def has_both_sides_depth(self) -> bool:
        """买卖双方都有深度"""
        return self.bid_depth > 0 and self.ask_depth > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "total_liquidity": self.total_liquidity,
            "has_both_sides_depth": self.has_both_sides_depth,
            "url": f"https://polymarket.com/event/{self.slug}",
            "extracted_at": datetime.now().isoformat()
        }


class HighPriceMarketFilter:
    """高价值标的筛选器"""
    
    GAMMA_API = "https://gamma-api.polymarket.com"
    CLOB_API = "https://clob.polymarket.com"
    
    def __init__(
        self,
        price_min: float = 0.8,
        price_max: float = 0.95,
        min_spread: float = 0.0,
        max_spread: float = 0.10,
        min_bid_depth: float = 10.0,
        min_ask_depth: float = 10.0,
        depth_slippage: float = 0.05,
        timeout: int = 30,
        max_workers: int = 10
    ):
        """
        初始化筛选器
        
        Args:
            price_min: 最低价格（默认0.8）
            price_max: 最高价格（默认0.95）
            min_spread: 最小价差（默认0.0，不过滤）
            max_spread: 最大价差（默认0.10，超过则认为流动性差）
            min_bid_depth: 最小买入深度（USDC）
            min_ask_depth: 最小卖出深度（USDC）
            depth_slippage: 计算深度时的滑点容忍度
            timeout: 请求超时时间
            max_workers: 并发线程数
        """
        self.price_min = price_min
        self.price_max = price_max
        self.min_spread = min_spread
        self.max_spread = max_spread
        self.min_bid_depth = min_bid_depth
        self.min_ask_depth = min_ask_depth
        self.depth_slippage = depth_slippage
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
    
    def fetch_events(
        self,
        limit: int = 500,
        active: bool = True,
        closed: bool = False,
        order: str = "liquidity",
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        从 Gamma API 获取事件列表
        
        Args:
            limit: 返回数量限制
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
            _print_safe(f"获取事件时出错: {e}")
            return []
    
    def is_event_ended(self, end_date_str: Optional[str]) -> bool:
        """
        检查事件是否已结束
        
        Args:
            end_date_str: 结束日期字符串（ISO格式）
        
        Returns:
            是否已结束
        """
        if not end_date_str:
            return False
        
        try:
            if end_date_str.endswith('Z'):
                end_date_str = end_date_str[:-1] + '+00:00'
            
            if '+' in end_date_str:
                end_date = datetime.fromisoformat(end_date_str)
            else:
                end_date = datetime.fromisoformat(end_date_str)
            
            now = datetime.now(end_date.tzinfo) if end_date.tzinfo else datetime.now()
            return end_date < now
        except Exception as e:
            _print_safe(f"解析日期出错: {e}")
            return False
    
    def get_orderbook(self, token_id: str) -> Optional[Dict[str, Any]]:
        """
        获取订单簿数据
        
        Args:
            token_id: CLOB 代币 ID
        
        Returns:
            订单簿数据
        """
        url = f"{self.CLOB_API}/book"
        params = {"token_id": token_id}
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return None
    
    def calculate_orderbook_depth(
        self,
        orderbook: Dict[str, Any],
        slippage: float = None
    ) -> OrderBookDepth:
        """
        计算订单簿深度
        
        Args:
            orderbook: 订单簿数据
            slippage: 滑点容忍度
        
        Returns:
            订单簿深度数据
        """
        if slippage is None:
            slippage = self.depth_slippage
        
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])
        
        if not bids or not asks:
            return OrderBookDepth(has_both_sides=False)
        
        best_bid = float(bids[-1]["price"])
        best_ask = float(asks[-1]["price"])
        spread = best_ask - best_bid
        
        min_sell_price = best_bid - slippage
        bid_depth = 0.0
        for b in reversed(bids):
            p = float(b["price"])
            s = float(b["size"])
            if p >= min_sell_price:
                bid_depth += p * s
            else:
                break
        
        max_buy_price = best_ask + slippage
        ask_depth = 0.0
        for a in reversed(asks):
            p = float(a["price"])
            s = float(a["size"])
            if p <= max_buy_price:
                ask_depth += p * s
            else:
                break
        
        has_both_sides = bid_depth >= self.min_bid_depth and ask_depth >= self.min_ask_depth
        
        return OrderBookDepth(
            bid_depth=bid_depth,
            ask_depth=ask_depth,
            best_bid=best_bid,
            best_ask=best_ask,
            spread=spread,
            has_both_sides=has_both_sides
        )
    
    def check_market_depth(self, market: Dict[str, Any]) -> Optional[OrderBookDepth]:
        """
        检查市场的订单簿深度
        
        Args:
            market: 市场数据（包含 token_id）
        
        Returns:
            订单簿深度数据，如果没有订单簿则返回 None
        """
        token_id = market.get("token_id", "")
        if not token_id:
            return None
        
        orderbook = self.get_orderbook(token_id)
        if not orderbook:
            return None
        
        return self.calculate_orderbook_depth(orderbook)
    
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
    
    def is_price_in_range(self, price: float) -> bool:
        """
        检查价格是否在目标范围内
        
        Args:
            price: 价格
        
        Returns:
            是否在范围内
        """
        return self.price_min <= price <= self.price_max
    
    def extract_markets_from_events(
        self,
        events: List[Dict[str, Any]],
        check_orderbook: bool = True
    ) -> List[HighPriceMarket]:
        """
        从事件中提取市场，并应用筛选条件
        
        Args:
            events: 事件列表
            check_orderbook: 是否检查订单簿深度
        
        Returns:
            符合条件的市场列表
        """
        filtered_markets: List[HighPriceMarket] = []
        all_candidates: List[Dict[str, Any]] = []
        
        _print_safe(f"\n[预处理] 提取所有市场并初步筛选...")
        
        for evt in events:
            event_title = evt.get("title", "")
            event_liquidity = float(evt.get("liquidity", 0) or 0)
            volume_24hr = float(evt.get("volume24hr", 0) or 0)
            volume = float(evt.get("volume", 0) or 0)
            end_date = evt.get("endDate")
            
            if self.is_event_ended(end_date):
                continue
            
            for m in evt.get("markets", []):
                enable_order_book = m.get("enableOrderBook", False)
                if not enable_order_book:
                    continue
                
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
                
                if not self.is_price_in_range(price_info["displayed_price"]):
                    continue
                
                if price_info["spread"] > self.max_spread:
                    continue
                
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
                
                all_candidates.append({
                    "event_title": event_title,
                    "market_question": m.get("question", ""),
                    "slug": m.get("slug", ""),
                    "token_id": token_id,
                    "condition_id": m.get("conditionId", ""),
                    "price_info": price_info,
                    "event_liquidity": event_liquidity,
                    "market_liquidity": market_liquidity,
                    "volume_24hr": volume_24hr,
                    "volume": volume,
                    "enable_order_book": enable_order_book,
                    "end_date": end_date,
                })
        
        _print_safe(f"      初步筛选后有 {len(all_candidates)} 个候选市场")
        
        if check_orderbook and all_candidates:
            _print_safe(f"\n[深度检查] 并发检查订单簿深度（{self.max_workers} 线程）...")
            
            def check_single_market(candidate: Dict) -> Optional[HighPriceMarket]:
                if not candidate["token_id"]:
                    return None
                
                depth = self.check_market_depth({"token_id": candidate["token_id"]})
                
                if depth is None:
                    return None
                
                if not depth.has_both_sides:
                    return None
                
                return HighPriceMarket(
                    event_title=candidate["event_title"],
                    market_question=candidate["market_question"],
                    slug=candidate["slug"],
                    token_id=candidate["token_id"],
                    condition_id=candidate["condition_id"],
                    best_bid=candidate["price_info"]["best_bid"],
                    best_ask=candidate["price_info"]["best_ask"],
                    spread=candidate["price_info"]["spread"],
                    mid_price=candidate["price_info"]["mid_price"],
                    last_trade_price=candidate["price_info"]["last_trade_price"],
                    displayed_price=candidate["price_info"]["displayed_price"],
                    event_liquidity=candidate["event_liquidity"],
                    market_liquidity=candidate["market_liquidity"],
                    volume_24hr=candidate["volume_24hr"],
                    volume=candidate["volume"],
                    enable_order_book=candidate["enable_order_book"],
                    end_date=candidate["end_date"],
                    is_active=True,
                    bid_depth=depth.bid_depth,
                    ask_depth=depth.ask_depth,
                    orderbook_check_passed=True
                )
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(check_single_market, c): c for c in all_candidates}
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        filtered_markets.append(result)
            
            _print_safe(f"      深度检查后剩余 {len(filtered_markets)} 个市场")
        else:
            for candidate in all_candidates:
                filtered_markets.append(HighPriceMarket(
                    event_title=candidate["event_title"],
                    market_question=candidate["market_question"],
                    slug=candidate["slug"],
                    token_id=candidate["token_id"],
                    condition_id=candidate["condition_id"],
                    best_bid=candidate["price_info"]["best_bid"],
                    best_ask=candidate["price_info"]["best_ask"],
                    spread=candidate["price_info"]["spread"],
                    mid_price=candidate["price_info"]["mid_price"],
                    last_trade_price=candidate["price_info"]["last_trade_price"],
                    displayed_price=candidate["price_info"]["displayed_price"],
                    event_liquidity=candidate["event_liquidity"],
                    market_liquidity=candidate["market_liquidity"],
                    volume_24hr=candidate["volume_24hr"],
                    volume=candidate["volume"],
                    enable_order_book=candidate["enable_order_book"],
                    end_date=candidate["end_date"],
                    is_active=True,
                    orderbook_check_passed=False
                ))
        
        return filtered_markets
    
    def find_high_value_markets(
        self,
        initial_events: int = 500,
        top_by_price: int = 100,
        top_by_liquidity: int = 20,
        check_orderbook: bool = True
    ) -> Dict[str, Any]:
        """
        主方法：查找高价值标的并按流动性筛选
        
        流程：
        1. 获取足够多的事件（按流动性排序）
        2. 排除已结束的事件
        3. 筛选价格在 0.8~0.95 之间的标的
        4. 确保买卖双方都有交易深度
        5. 按价格排序取前 N 个
        6. 按流动性排序取前 M 个
        
        Args:
            initial_events: 初始获取的事件数量
            top_by_price: 按价格筛选后的数量
            top_by_liquidity: 按流动性筛选后的数量
            check_orderbook: 是否检查订单簿深度
        
        Returns:
            包含筛选结果的字典
        """
        _print_safe("=" * 80)
        _print_safe("Polymarket 高价值标的筛选器")
        _print_safe(f"价格范围: {self.price_min} ~ {self.price_max}")
        _print_safe(f"价差限制: <= {self.max_spread}")
        _print_safe(f"最小深度: 买入 >= {self.min_bid_depth} USDC | 卖出 >= {self.min_ask_depth} USDC")
        _print_safe(f"滑点容忍: {self.depth_slippage} USD")
        _print_safe("=" * 80)
        
        _print_safe(f"\n[1/6] 获取前 {initial_events} 个事件（按流动性排序）...")
        events = self.fetch_events(limit=initial_events)
        _print_safe(f"      成功获取 {len(events)} 个事件")
        
        _print_safe(f"\n[2/6] 筛选条件：")
        _print_safe(f"      - 价格在 {self.price_min} ~ {self.price_max} 之间")
        _print_safe(f"      - 价差 <= {self.max_spread}")
        _print_safe(f"      - 排除已结束的事件")
        if check_orderbook:
            _print_safe(f"      - 买卖双方都有订单簿深度（买入 >= {self.min_bid_depth}, 卖出 >= {self.min_ask_depth}）")
        
        filtered_markets = self.extract_markets_from_events(
            events, check_orderbook=check_orderbook
        )
        
        if not filtered_markets:
            _print_safe("\n警告：未找到符合条件的标的")
            _print_safe("建议：")
            _print_safe("  - 放宽价格范围")
            _print_safe("  - 增大价差限制")
            _print_safe("  - 降低最小深度要求")
            return {
                "price_min": self.price_min,
                "price_max": self.price_max,
                "max_spread": self.max_spread,
                "min_bid_depth": self.min_bid_depth,
                "min_ask_depth": self.min_ask_depth,
                "initial_events_count": len(events),
                "filtered_count": 0,
                "top_by_price": [],
                "top_by_liquidity": []
            }
        
        _print_safe(f"\n[3/6] 按价格从高到低排序，取前 {top_by_price} 个...")
        filtered_markets.sort(
            key=lambda x: (x.displayed_price, x.total_liquidity),
            reverse=True
        )
        
        top_by_price = filtered_markets[:top_by_price]
        _print_safe(f"      成功筛选出 {len(top_by_price)} 个高价值标的")
        
        _print_safe(f"\n[4/6] 从这 {len(top_by_price)} 个中按流动性从高到低排序...")
        top_by_price_sorted_by_liquidity = sorted(
            top_by_price,
            key=lambda x: (x.total_liquidity, x.displayed_price),
            reverse=True
        )
        
        top_by_liquidity = top_by_price_sorted_by_liquidity[:top_by_liquidity]
        _print_safe(f"      成功筛选出 {len(top_by_liquidity)} 个流动性最高的标的")
        
        _print_safe(f"\n[5/6] 输出结果...")
        
        _print_safe(f"\n{'='*80}")
        _print_safe(f"阶段1结果：价格在 {self.price_min}~{self.price_max} 的前 {top_by_price} 个标的（按价格排序）")
        _print_safe(f"{'='*80}\n")
        
        for i, m in enumerate(top_by_price[:10], 1):
            _print_safe(f"#{i:02d} | 价格: {m.displayed_price:.3f} | 流动性: {m.total_liquidity:,.0f} USDC")
            _print_safe(f"      事件: {m.event_title}")
            _print_safe(f"      市场: {m.market_question}")
            _print_safe(f"      Slug: {m.slug}")
            _print_safe(f"      Bid: {m.best_bid:.3f} | Ask: {m.best_ask:.3f} | 价差: {m.spread:.3f}")
            if m.orderbook_check_passed:
                _print_safe(f"      买入深度: {m.bid_depth:,.2f} USDC | 卖出深度: {m.ask_depth:,.2f} USDC")
            if m.last_trade_price:
                _print_safe(f"      最近成交价: {m.last_trade_price:.3f}")
            _print_safe()
        
        _print_safe(f"\n{'='*80}")
        _print_safe(f"最终结果：流动性最高的前 {len(top_by_liquidity)} 个标的")
        _print_safe(f"{'='*80}\n")
        
        for i, m in enumerate(top_by_liquidity, 1):
            _print_safe(f"#{i:02d} | 流动性: {m.total_liquidity:,.0f} USDC | 价格: {m.displayed_price:.3f}")
            _print_safe(f"      事件: {m.event_title}")
            _print_safe(f"      市场: {m.market_question}")
            _print_safe(f"      Slug: {m.slug}")
            _print_safe(f"      Token ID: {m.token_id}")
            _print_safe(f"      Bid: {m.best_bid:.3f} | Ask: {m.best_ask:.3f} | 价差: {m.spread:.3f}")
            if m.orderbook_check_passed:
                _print_safe(f"      买入深度: {m.bid_depth:,.2f} USDC | 卖出深度: {m.ask_depth:,.2f} USDC")
            _print_safe(f"      24h交易量: {m.volume_24hr:,.2f} USDC")
            _print_safe(f"      总交易量: {m.volume:,.2f} USDC")
            _print_safe(f"      订单簿启用: {'是' if m.enable_order_book else '否'}")
            _print_safe(f"      URL: https://polymarket.com/event/{m.slug}")
            _print_safe()
        
        _print_safe("-" * 80)
        _print_safe("Slug 列表（可直接用于前端 URL）:")
        for m in top_by_liquidity:
            _print_safe(f"  https://polymarket.com/event/{m.slug}")
        
        return {
            "price_min": self.price_min,
            "price_max": self.price_max,
            "max_spread": self.max_spread,
            "min_bid_depth": self.min_bid_depth,
            "min_ask_depth": self.min_ask_depth,
            "depth_slippage": self.depth_slippage,
            "initial_events_count": len(events),
            "filtered_count": len(filtered_markets),
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
            filename = f"high_value_markets_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        _print_safe(f"\n结果已保存到: {filename}")
        return filename


def main():
    """主函数"""
    filter = HighPriceMarketFilter(
        price_min=0.8,
        price_max=0.95,
        max_spread=0.10,
        min_bid_depth=10.0,
        min_ask_depth=10.0,
        depth_slippage=0.05,
        max_workers=10
    )
    
    results = filter.find_high_value_markets(
        initial_events=500,
        top_by_price=100,
        top_by_liquidity=20,
        check_orderbook=True
    )
    
    filter.save_results(results)
    
    return results


if __name__ == "__main__":
    main()
