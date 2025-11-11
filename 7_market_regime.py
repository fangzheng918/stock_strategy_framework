"""
模块 7: 市场分层系统 (Market Regime Classification)
功能: 自动识别 4 种市场状态并自适应参数调整
"""

import pandas as pd
import numpy as np


class MarketRegimeAnalyzer:
    """市场分层分析器"""
    
    def __init__(self, data, lookback=50):
        self.data = data.copy()
        self.lookback = lookback
        self.current_regime = None
        
    def calculate_regime_features(self):
        """计算 regime 特征"""
        # ATR
        high_low = self.data['High'] - self.data['Low']
        self.data['ATR'] = high_low.rolling(14).mean()
        
        # 波动率
        self.data['Volatility'] = self.data['Returns'].rolling(self.lookback).std()
        
        # 成交量比
        self.data['Volume_Ratio'] = self.data['Volume'] / self.data['Volume'].rolling(self.lookback).mean()
        
        # 盘口宽度（High - Low）
        self.data['Spread_Width'] = (self.data['High'] - self.data['Low']) / self.data['Close']
        
        # RSI 简化版
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
        return self.data[['ATR', 'Volatility', 'Volume_Ratio', 'Spread_Width', 'RSI']]
    
    def classify_regime(self):
        """分类市场状态"""
        self.calculate_regime_features()
        
        volatility = self.data['Volatility'].iloc[-1]
        vol_mean = self.data['Volatility'].mean()
        trend = (self.data['Close'].iloc[-1] - self.data['Close'].iloc[-50]) / self.data['Close'].iloc[-50]
        
        scores = {
            'Flat': 0,
            'Up': 0,
            'Down': 0,
            'Chaos': 0
        }
        
        # 平稳市场
        if volatility < vol_mean * 0.8:
            scores['Flat'] = 2
        
        # 上升市场
        if trend > 0.02 and volatility < vol_mean * 1.2:
            scores['Up'] = 2
        
        # 下降市场
        if trend < -0.02 and volatility < vol_mean * 1.2:
            scores['Down'] = 2
        
        # 混乱市场
        if volatility > vol_mean * 1.5:
            scores['Chaos'] = 2
        
        # 基于成交量
        vol_ratio = self.data['Volume_Ratio'].iloc[-1]
        if vol_ratio > 1.5:
            scores['Chaos'] += 1
        elif vol_ratio < 0.7:
            scores['Flat'] += 1
        
        # 确定 regime
        regime = max(scores, key=scores.get)
        confidence = scores[regime] / sum(scores.values())
        
        self.current_regime = {'regime': regime, 'confidence': confidence, 'scores': scores}
        return regime, confidence


class RegimeAdaptiveStrategy:
    """自适应策略"""
    
    def __init__(self, data):
        self.analyzer = MarketRegimeAnalyzer(data)
        self.regime_params = {
            'Flat': {'buy_threshold': 0.7, 'stop_loss_pct': 0.02, 'position_multiplier': 0.8},
            'Up': {'buy_threshold': 0.5, 'stop_loss_pct': 0.03, 'position_multiplier': 1.2},
            'Down': {'buy_threshold': 0.9, 'stop_loss_pct': 0.01, 'position_multiplier': 0.5},
            'Chaos': {'buy_threshold': 0.95, 'stop_loss_pct': 0.005, 'position_multiplier': 0.3}
        }
    
    def get_current_regime_parameters(self):
        """获取当前 regime 的参数"""
        regime, confidence = self.analyzer.classify_regime()
        params = self.regime_params[regime].copy()
        params['confidence'] = confidence
        params['regime'] = regime
        return params
    
    def analyze_regime_transition(self):
        """分析 regime 转换"""
        current_regime, current_conf = self.analyzer.classify_regime()
        
        # 比较前期 regime
        history_size = min(10, len(self.analyzer.data))
        prev_volatility = self.analyzer.data['Volatility'].iloc[-history_size:-1].mean()
        curr_volatility = self.analyzer.data['Volatility'].iloc[-1]
        
        transition = {
            'current_regime': current_regime,
            'volatility_change': curr_volatility - prev_volatility,
            'confidence': current_conf,
            'transition_risk': abs(curr_volatility - prev_volatility) / prev_volatility if prev_volatility > 0 else 0
        }
        
        return transition
