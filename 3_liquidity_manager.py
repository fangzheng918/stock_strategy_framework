"""
模块 3: 流动性管理与价差评估
功能: 评估市场深度、计算交易成本、价差合规监控
"""

import pandas as pd
import numpy as np


class LiquidityManager:
    """流动性管理类"""
    
    def __init__(self, data, position_size=1000):
        self.data = data.copy()
        self.position_size = position_size
        
    def calculate_market_depth(self):
        """评估市场深度"""
        # 基于成交量和价格波动估计深度
        volume_score = (self.data['Volume'] / self.data['Volume'].quantile(0.75)).clip(0, 2) * 50
        volatility_score = (1 / (1 + self.data['Returns'].rolling(20).std())) * 50
        
        self.data['Market_Depth_Score'] = (volume_score + volatility_score) / 2
        return self.data['Market_Depth_Score']
    
    def assess_market_depth(self):
        """评估流动性充足性"""
        depth = self.calculate_market_depth()
        self.data['Liquidity_Adequate'] = (depth > 30).astype(int)
        return self.data[['Market_Depth_Score', 'Liquidity_Adequate']]
    
    def identify_optimal_trade_time(self):
        """识别最优交易时间"""
        depth = self.data['Market_Depth_Score']
        self.data['Optimal_Trade_Time'] = (depth > 70).astype(int)
        return self.data['Optimal_Trade_Time']
    
    def get_liquidity_summary(self):
        """获取流动性摘要"""
        return {
            'avg_depth_score': self.data['Market_Depth_Score'].mean(),
            'high_liquidity_pct': (self.data['Market_Depth_Score'] > 70).sum() / len(self.data) * 100,
            'med_liquidity_pct': ((self.data['Market_Depth_Score'] >= 30) & 
                                 (self.data['Market_Depth_Score'] <= 70)).sum() / len(self.data) * 100
        }


class SpreadManager:
    """价差管理类"""
    
    def __init__(self, data, target_spread=0.001):
        self.data = data.copy()
        self.target_spread = target_spread
        
    def calculate_fair_spread(self):
        """计算合理价差"""
        # 基于波动率计算
        volatility = self.data['Returns'].rolling(20).std()
        price = self.data['Close']
        
        # 合理价差 = volatility * price * spread_factor
        spread_factor = 0.001  # 0.1% 基础
        self.data['Fair_Spread'] = (volatility * price * spread_factor).fillna(self.target_spread)
        
        return self.data['Fair_Spread']
    
    def monitor_spread_compliance(self):
        """监控价差合规"""
        fair_spread = self.calculate_fair_spread()
        self.data['Spread_Compliant'] = (fair_spread <= self.target_spread * 2).astype(int)
        
        return {
            'avg_spread': fair_spread.mean(),
            'compliance_pct': self.data['Spread_Compliant'].sum() / len(self.data) * 100,
            'status': '通过' if self.data['Spread_Compliant'].mean() > 0.95 else '需改进'
        }
