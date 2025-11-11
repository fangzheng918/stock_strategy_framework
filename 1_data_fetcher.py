"""
模块 1: 数据获取与预处理
功能: 从 Yahoo Finance 获取实时数据或生成模拟数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf


class StockDataFetcher:
    """股票数据获取类"""
    
    def __init__(self, symbol='AAPL', interval='1d'):
        """
        初始化数据获取器
        
        参数:
            symbol: 股票代码
            interval: 时间间隔 ('1m', '5m', '1h', '1d')
        """
        self.symbol = symbol
        self.interval = interval
        self.data = None
        
    def fetch_data(self, start_date=None, end_date=None):
        """从 Yahoo Finance 获取真实数据"""
        try:
            if start_date is None:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=180)
            
            self.data = yf.download(self.symbol, start=start_date, end=end_date, 
                                   interval=self.interval, progress=False)
            self.data['Returns'] = self.data['Close'].pct_change()
            return self.data
        except Exception as e:
            print(f"无法获取真实数据: {e}，使用模拟数据")
            return self.generate_sample_data(days=180)
    
    def generate_sample_data(self, days=180, initial_price=100):
        """生成高质量模拟数据"""
        dates = pd.date_range(end=datetime.now(), periods=days*24, freq='H')  # 每小时 1 个数据点
        
        # 生成价格轨迹
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.01, len(dates))
        prices = initial_price * np.exp(np.cumsum(returns))
        
        # 添加随机波动
        noise = np.random.normal(0, prices * 0.005, len(dates))
        prices = prices + noise
        
        # 构建 OHLCV
        data = pd.DataFrame(index=dates)
        data['Open'] = prices * (1 + np.random.uniform(-0.002, 0.002, len(dates)))
        data['Close'] = prices
        data['High'] = prices * (1 + np.abs(np.random.uniform(0, 0.01, len(dates))))
        data['Low'] = prices * (1 - np.abs(np.random.uniform(0, 0.01, len(dates))))
        data['Volume'] = np.random.uniform(1e6, 5e6, len(dates))
        data['Returns'] = data['Close'].pct_change()
        
        self.data = data
        return data
    
    def get_summary_stats(self):
        """获取数据统计"""
        if self.data is None:
            return None
        return {
            'total_rows': len(self.data),
            'date_range': f"{self.data.index[0]} to {self.data.index[-1]}",
            'avg_price': self.data['Close'].mean(),
            'volatility': self.data['Returns'].std(),
            'missing_values': self.data.isnull().sum().sum()
        }
