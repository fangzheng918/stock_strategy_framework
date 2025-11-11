# -*- coding: utf-8 -*-
"""
模块10：头寸对冲系统 (Position Hedging & Offsetting)

功能：
  • 期权对冲（看跌期权/领口策略）
  • 衍生品对冲（期货、权证）
  • 相关资产对冲（配对交易）
  • 动态对冲比率计算

核心目标：
  • 限制最大亏损
  • 在保持上升空间的前提下保护头寸
  • 管理极端风险
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional


class PositionHedgingManager:
    """头寸对冲管理器"""
    
    def __init__(self):
        self.hedges = {}  # 对冲记录
    
    def calculate_protective_put(self, stock_price: float, put_strike: float,
                                 put_premium: float, stock_qty: int) -> Dict:
        """
        看跌期权对冲 (Protective Put)
        
        策略：买入看跌期权，保护股票头寸
        
        损益：
        • 股价上涨：无限利润 - 期权费
        • 股价下跌：亏损限制在 (股价 - 行权价) × 股数
        
        参数:
            stock_price: 当前股价
            put_strike: 看跌期权行权价
            put_premium: 看跌期权费用（每股）
            stock_qty: 持有股数
        
        返回:
            {
                'strategy': '看跌期权对冲',
                'protection_level': 保护下限,
                'max_loss': 最大亏损,
                'cost': 对冲成本,
                'cost_pct': 对冲成本占比,
                'breakeven': 盈亏平衡点,
                'payoff_chart': 损益图表数据
            }
        """
        # 成本
        total_premium = put_premium * stock_qty
        
        # 保护水平：行权价
        protection_level = put_strike
        
        # 最大亏损：股价跌到行权价，再减去已支付的期权费
        if stock_price > put_strike:
            # 目前还没行权
            max_protected_loss = (stock_price - put_strike) * stock_qty + total_premium
        else:
            # 已经行权
            max_protected_loss = total_premium
        
        # 盈亏平衡点
        breakeven_price = put_strike + put_premium
        
        # 生成不同股价下的损益
        price_range = np.linspace(stock_price * 0.5, stock_price * 1.5, 50)
        payoff = []
        
        for price in price_range:
            # 股票损益
            stock_pnl = (price - stock_price) * stock_qty
            
            # 期权损益
            if price <= put_strike:
                # 期权行权，收益 = (行权价 - 当前价) × 股数 - 期权费
                option_pnl = (put_strike - price) * stock_qty - total_premium
            else:
                # 期权不行权，亏损期权费
                option_pnl = -total_premium
            
            total_pnl = stock_pnl + option_pnl
            
            payoff.append({
                'price': price,
                'stock_pnl': stock_pnl,
                'option_pnl': option_pnl,
                'total_pnl': total_pnl
            })
        
        return {
            'strategy': '看跌期权对冲',
            'current_stock_price': stock_price,
            'put_strike': put_strike,
            'put_premium': put_premium,
            'stock_qty': stock_qty,
            'total_cost': total_premium,
            'cost_pct_of_position': (total_premium / (stock_price * stock_qty)) * 100,
            'protection_level': protection_level,
            'max_protected_loss': max_protected_loss,
            'breakeven_price': breakeven_price,
            'unlimited_upside': stock_price * 1.5,  # 继续上涨的空间
            'payoff_chart': payoff
        }
    
    def calculate_collar_hedge(self, stock_price: float, put_strike: float, put_premium: float,
                              call_strike: float, call_premium: float, stock_qty: int) -> Dict:
        """
        领口对冲 (Collar Hedge) = 买看跌 + 卖看涨
        
        策略：同时买入看跌期权和卖出看涨期权
        • 看跌期权提供下限保护
        • 看涨期权收取费用，抵消看跌期权成本
        
        特点：对冲成本低甚至零成本
        
        参数:
            stock_price: 当前股价
            put_strike: 买入看跌行权价
            put_premium: 买入看跌费用
            call_strike: 卖出看涨行权价
            call_premium: 卖出看涨收入
            stock_qty: 持有股数
        
        返回:
            {
                'strategy': '领口对冲',
                'net_cost': 净成本,
                'downside_protection': 下限保护,
                'upside_cap': 上限收益,
                ...
            }
        """
        # 净成本（负数表示有收入）
        total_put_cost = put_premium * stock_qty
        total_call_income = call_premium * stock_qty
        net_cost = total_put_cost - total_call_income
        
        # 下限保护
        floor_price = put_strike
        
        # 上限（看涨被行权时）
        ceiling_price = call_strike
        
        # 最大损失：股价跌到put_strike
        max_loss = (stock_price - put_strike) * stock_qty + net_cost
        
        # 最大收益：股价涨到call_strike
        max_gain = (call_strike - stock_price) * stock_qty - net_cost
        
        # 损益图表
        price_range = np.linspace(stock_price * 0.5, stock_price * 1.5, 50)
        payoff = []
        
        for price in price_range:
            stock_pnl = (price - stock_price) * stock_qty
            
            # 看跌期权
            if price <= put_strike:
                put_pnl = (put_strike - price) * stock_qty - total_put_cost
            else:
                put_pnl = -total_put_cost
            
            # 看涨期权
            if price >= call_strike:
                call_pnl = -((price - call_strike) * stock_qty - total_call_income)
            else:
                call_pnl = total_call_income
            
            total_pnl = stock_pnl + put_pnl + call_pnl
            
            payoff.append({
                'price': price,
                'stock_pnl': stock_pnl,
                'put_pnl': put_pnl,
                'call_pnl': call_pnl,
                'total_pnl': total_pnl
            })
        
        return {
            'strategy': '领口对冲（零成本或低成本）',
            'current_price': stock_price,
            'put_strike': put_strike,
            'call_strike': call_strike,
            'put_cost': total_put_cost,
            'call_income': total_call_income,
            'net_cost': net_cost,
            'net_cost_status': '零成本' if abs(net_cost) < 0.01 else ('有收入' if net_cost < 0 else '有成本'),
            'protected_range': (floor_price, ceiling_price),
            'max_loss': max_loss,
            'max_gain': max_gain,
            'payoff_chart': payoff
        }
    
    def calculate_futures_hedge(self, spot_position_qty: float, spot_price: float,
                               futures_price: float, hedge_ratio: float = 1.0) -> Dict:
        """
        期货对冲 - 用期货合约对冲现货头寸
        
        参数:
            spot_position_qty: 现货头寸数量
            spot_price: 现货价格
            futures_price: 期货价格
            hedge_ratio: 对冲比率（通常0.8-1.0，<1表示不完全对冲）
        
        返回:
            {
                'spot_position': 现货头寸,
                'hedge_position': 期货对冲头寸,
                'basis': 基差,
                'expected_result': 对冲结果
            }
        """
        # 确定对冲手数
        # 假设1份期货合约代表100单位
        futures_contract_size = 100
        futures_qty = (spot_position_qty * hedge_ratio) / futures_contract_size
        
        # 基差 = 期货价格 - 现货价格
        basis = futures_price - spot_price
        basis_pct = (basis / spot_price) * 100
        
        # 假设不同情景下的对冲结果
        scenarios = []
        
        price_scenarios = [
            spot_price * 0.85,  # 下跌15%
            spot_price * 0.90,  # 下跌10%
            spot_price,         # 不变
            spot_price * 1.10,  # 上涨10%
            spot_price * 1.15   # 上涨15%
        ]
        
        for new_spot_price in price_scenarios:
            # 假设期货价格随现货变化
            price_change_pct = (new_spot_price - spot_price) / spot_price
            new_futures_price = futures_price + (futures_price * price_change_pct)
            
            # 现货损益
            spot_pnl = (new_spot_price - spot_price) * spot_position_qty
            
            # 期货损益（做空，所以价格下跌时获利）
            futures_pnl = -(new_futures_price - futures_price) * futures_qty * futures_contract_size
            
            # 总损益
            total_pnl = spot_pnl + futures_pnl
            
            scenarios.append({
                'spot_price': new_spot_price,
                'futures_price': new_futures_price,
                'spot_pnl': spot_pnl,
                'futures_pnl': futures_pnl,
                'total_pnl': total_pnl,
                'hedge_effectiveness': abs(total_pnl) / abs(spot_pnl) if spot_pnl != 0 else 0
            })
        
        return {
            'strategy': '期货对冲',
            'spot_position_qty': spot_position_qty,
            'spot_price': spot_price,
            'futures_price': futures_price,
            'hedge_ratio': hedge_ratio,
            'futures_contracts': futures_qty,
            'basis': basis,
            'basis_pct': basis_pct,
            'scenarios': scenarios
        }
    
    def calculate_dynamic_hedge_ratio(self, current_vol: float, target_vol: float,
                                     position_value: float, hedge_instrument_vol: float) -> float:
        """
        动态对冲比率 - 根据波动率调整对冲数量
        
        规则：波动率越高，对冲比率越高
        
        参数:
            current_vol: 当前波动率
            target_vol: 目标波动率（期望风险）
            position_value: 头寸价值
            hedge_instrument_vol: 对冲工具的波动率
        
        返回:
            对冲比率
        """
        if hedge_instrument_vol == 0:
            return 0
        
        # 基础公式：对冲数量 = 头寸价值 × 头寸波动率 / 对冲工具波动率
        base_ratio = (current_vol / hedge_instrument_vol) * (target_vol / current_vol)
        
        # 限制在0-1.5之间
        hedge_ratio = np.clip(base_ratio, 0, 1.5)
        
        return hedge_ratio
    
    def calculate_pairs_hedge(self, long_stock_price: float, long_qty: int,
                             short_stock_price: float, beta: float) -> Dict:
        """
        配对交易对冲 - 做多一只股票同时做空相关股票
        
        参数:
            long_stock_price: 做多股票的价格
            long_qty: 做多数量
            short_stock_price: 做空股票的价格
            beta: 两只股票的相关系数（β）
        
        返回:
            {
                'long_position': 做多头寸,
                'short_position': 做空头寸,
                'hedge_ratio': 对冲比率,
                'expected_market_neutral': 市场中性预期
            }
        """
        # 头寸价值
        long_position_value = long_stock_price * long_qty
        
        # 计算做空数量以实现市场中性
        # 做空价值 = 做多价值 × Beta
        short_position_value = long_position_value * beta
        short_qty = short_position_value / short_stock_price
        
        # 对冲比率
        hedge_ratio = short_position_value / long_position_value
        
        # 模拟损益
        scenarios = []
        market_moves = [-20, -10, 0, 10, 20]  # 市场涨跌百分比
        
        for market_move_pct in market_moves:
            # 做多股票价格变化
            long_price_change = long_stock_price * market_move_pct / 100
            new_long_price = long_stock_price + long_price_change
            
            # 做空股票价格变化（与市场关系由beta决定）
            short_price_change = short_stock_price * (market_move_pct * beta) / 100
            new_short_price = short_stock_price + short_price_change
            
            # 损益
            long_pnl = long_price_change * long_qty
            short_pnl = -short_price_change * short_qty
            total_pnl = long_pnl + short_pnl
            
            scenarios.append({
                'market_move_pct': market_move_pct,
                'long_pnl': long_pnl,
                'short_pnl': short_pnl,
                'total_pnl': total_pnl,
                'market_neutrality': 'Good' if abs(total_pnl) < abs(long_pnl) * 0.2 else 'Fair'
            })
        
        return {
            'strategy': '配对交易对冲',
            'long_stock_price': long_stock_price,
            'long_qty': long_qty,
            'long_position_value': long_position_value,
            'short_stock_price': short_stock_price,
            'short_qty': short_qty,
            'short_position_value': short_position_value,
            'beta': beta,
            'hedge_ratio': hedge_ratio,
            'scenarios': scenarios
        }
    
    def calculate_vega_hedge(self, position_vega: float, target_vega: float = 0) -> Dict:
        """
        波动率对冲 - 对冲波动率风险
        
        参数:
            position_vega: 当前头寸的vega（波动率敏感度）
            target_vega: 目标vega（通常为0表示完全对冲）
        
        返回:
            对冲建议
        """
        vega_gap = position_vega - target_vega
        
        if abs(vega_gap) < 0.01:
            recommendation = '无需对冲，已达到目标'
        elif vega_gap > 0:
            recommendation = f'头寸看多波动率，需要卖出期权（每个点Vega={abs(vega_gap):.2f}）来对冲'
        else:
            recommendation = f'头寸看空波动率，需要买入期权（每个点Vega={abs(vega_gap):.2f}）来对冲'
        
        return {
            'current_vega': position_vega,
            'target_vega': target_vega,
            'vega_gap': vega_gap,
            'recommendation': recommendation,
            'greek_name': 'Vega（波动率敏感度）'
        }
    
    def calculate_delta_hedge(self, position_delta: float, target_delta: float = 0) -> Dict:
        """
        方向对冲 - 对冲方向风险（Delta）
        
        参数:
            position_delta: 当前头寸的delta（方向敏感度）
            target_delta: 目标delta（通常为0表示完全对冲）
        
        返回:
            对冲建议
        """
        delta_gap = position_delta - target_delta
        
        if abs(delta_gap) < 0.01:
            recommendation = '头寸已中性，无需对冲'
        elif delta_gap > 0:
            recommendation = f'头寸看多，需要卖出期货或看跌期权进行空头对冲（Delta={abs(delta_gap):.2f}）'
        else:
            recommendation = f'头寸看空，需要买入期货或看涨期权进行多头对冲（Delta={abs(delta_gap):.2f}）'
        
        return {
            'current_delta': position_delta,
            'target_delta': target_delta,
            'delta_gap': delta_gap,
            'recommendation': recommendation,
            'greek_name': 'Delta（方向敏感度）'
        }
