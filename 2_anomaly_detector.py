"""
模块 2: 异常波动检测与市场结构分析
功能: 识别异常波动、市场结构变化、散户 vs 机构行为
"""

import pandas as pd
import numpy as np
from scipy import stats


class AnomalyDetector:
    """异常检测类"""
    
    def __init__(self, data, window=20):
        """
        初始化异常检测器
        
        参数:
            data: OHLCV DataFrame
            window: 滚动窗口大小
        """
        self.data = data.copy()
        self.window = window
        self.anomalies_detected = False
        
    def detect_price_anomalies(self):
        """基于 Z-score 检测价格异常"""
        self.data['Returns_ZScore'] = stats.zscore(self.data['Returns'].fillna(0))
        self.data['Price_Anomaly'] = (np.abs(self.data['Returns_ZScore']) > 2.5).astype(int)
        return self.data['Price_Anomaly']
    
    def detect_volume_anomalies(self):
        """检测成交量异常"""
        rolling_vol = self.data['Volume'].rolling(self.window).mean()
        self.data['Volume_Anomaly'] = (self.data['Volume'] > rolling_vol * 2).astype(int)
        return self.data['Volume_Anomaly']
    
    def detect_volatility_clustering(self):
        """检测波动率聚集"""
        self.data['Rolling_Volatility'] = self.data['Returns'].rolling(self.window).std()
        vol_zscore = stats.zscore(self.data['Rolling_Volatility'].fillna(0))
        self.data['High_Volatility'] = (vol_zscore > 1.5).astype(int)
        return self.data['High_Volatility']
    
    def detect_all_anomalies(self):
        """检测所有异常"""
        self.detect_price_anomalies()
        self.detect_volume_anomalies()
        self.detect_volatility_clustering()
        
        # 综合异常分数
        self.data['Anomaly_Score'] = (
            self.data['Price_Anomaly'] * 0.4 +
            self.data['Volume_Anomaly'] * 0.3 +
            self.data['High_Volatility'] * 0.3
        )
        self.anomalies_detected = True
        return self.data
    
    def get_data(self):
        """返回包含异常标记的数据"""
        return self.data


class MarketBehaviorAnalyzer:
    """市场行为分析类"""
    
    def __init__(self, data):
        self.data = data.copy()
        
    def identify_market_dominance(self):
        """识别市场主导权（机构 vs 散户）"""
        # 基于成交量和波动率估计机构参与度
        vol_ratio = self.data['Volume'].rolling(20).mean() / self.data['Volume'].mean()
        volatility = self.data['Returns'].rolling(20).std()
        
        # 机构特征: 高成交量 + 低波动 = 系统性交易
        self.data['Institutional_Ratio'] = (
            (vol_ratio > 1.2) & (volatility < self.data['Returns'].std() * 1.5)
        ).astype(float) * 100
        
        return self.data['Institutional_Ratio']
    
    def get_market_dominance(self):
        """获取市场主导权统计"""
        return {
            'avg_institutional_ratio': self.identify_market_dominance().mean(),
            'market_structure': '机构主导' if self.identify_market_dominance().mean() > 60 else '散户主导'
        }
