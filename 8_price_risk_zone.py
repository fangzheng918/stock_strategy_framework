"""
模块 8: 价格风险区间管理 (Price Risk Zone Management)
功能: 多种止损/止盈方法、风险收益评估、价格区间监控
"""

import pandas as pd
import numpy as np


class PriceRiskZoneManager:
    """价格风险区间管理器"""
    
    def __init__(self, data, lookback_period=20):
        self.data = data.copy()
        self.lookback_period = lookback_period
        
    def calculate_atr(self, period=14):
        """计算 ATR"""
        high_low = self.data['High'] - self.data['Low']
        high_close = abs(self.data['High'] - self.data['Close'].shift())
        low_close = abs(self.data['Low'] - self.data['Close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        return atr.iloc[-1] if len(atr) > 0 else 0
    
    def calculate_bollinger_bands(self, period=20, std_dev=2):
        """计算 Bollinger 带"""
        sma = self.data['Close'].rolling(period).mean()
        std = self.data['Close'].rolling(period).std()
        
        upper = sma + std_dev * std
        middle = sma
        lower = sma - std_dev * std
        
        return {'upper': upper.iloc[-1], 'middle': middle.iloc[-1], 'lower': lower.iloc[-1]}
    
    def calculate_lookback_stop_loss(self, entry_price, atr_mult=2.0):
        """Lookback + ATR 止损"""
        lookback_high = self.data['High'].iloc[-self.lookback_period:].max()
        lookback_low = self.data['Low'].iloc[-self.lookback_period:].min()
        
        atr = self.calculate_atr()
        stop_loss = max(lookback_low - atr * atr_mult, entry_price * 0.95)
        
        return stop_loss
    
    def calculate_bollinger_stop_loss(self, period=20, std_dev=2):
        """Bollinger 带止损"""
        bands = self.calculate_bollinger_bands(period, std_dev)
        return bands['lower']
    
    def calculate_atr_based_stop_loss(self, entry_price, atr_mult=2.0):
        """ATR 止损"""
        atr = self.calculate_atr()
        return entry_price - atr * atr_mult
    
    def calculate_floating_stop_loss(self, entry_price, current_price, atr_mult=1.5):
        """浮动止损（尾随）"""
        atr = self.calculate_atr()
        trailing_stop = current_price - atr * atr_mult
        return max(trailing_stop, entry_price - atr * atr_mult * 2)
    
    def calculate_take_profit_levels(self, entry_price, method='atr', risk_distance=None):
        """计算三级止盈"""
        if risk_distance is None:
            risk_distance = self.calculate_atr()
        
        if method == 'atr':
            tp1 = entry_price + risk_distance * 1.0
            tp2 = entry_price + risk_distance * 2.0
            tp3 = entry_price + risk_distance * 3.0
        elif method == 'fixed':
            tp1 = entry_price * 1.02
            tp2 = entry_price * 1.05
            tp3 = entry_price * 1.10
        elif method == 'fibonacci':
            tp1 = entry_price * 1.0382
            tp2 = entry_price * 1.0618
            tp3 = entry_price * 1.1618
        else:
            tp1 = tp2 = tp3 = entry_price
        
        return {'TP1': tp1, 'TP2': tp2, 'TP3': tp3}
    
    def assess_risk_reward_ratio(self, entry_price, stop_loss, take_profit):
        """评估风险/收益比"""
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        
        ratio = reward / risk if risk > 0 else 0
        
        return {
            'risk': risk,
            'reward': reward,
            'ratio': ratio,
            'quality': '优秀' if ratio >= 2.0 else '良好' if ratio >= 1.5 else '一般'
        }
    
    def monitor_price_zones(self, entry_price, stop_loss, take_profit_levels):
        """监控价格区间"""
        current_price = self.data['Close'].iloc[-1]
        
        alerts = []
        
        if current_price < stop_loss:
            alerts.append('✗ 触发止损！')
        elif current_price < stop_loss * 1.05:
            alerts.append('⚠️ 接近止损')
        
        if current_price > take_profit_levels['TP3']:
            alerts.append('✓ 已超过最高止盈')
        elif current_price > take_profit_levels['TP2']:
            alerts.append('✓ 已达到 TP2')
        elif current_price > take_profit_levels['TP1']:
            alerts.append('✓ 已达到 TP1')
        
        return {
            'current_price': current_price,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit_levels,
            'alerts': alerts
        }
