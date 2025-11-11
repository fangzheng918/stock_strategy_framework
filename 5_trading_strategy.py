"""
模块 5: 交易策略与回测框架
功能: 买卖信号生成、回测执行、性能评估
"""

import pandas as pd
import numpy as np


class TradingStrategy:
    """交易策略类"""
    
    def __init__(self, price_data, anomaly_data, liquidity_data, risk_data):
        self.price_data = price_data.copy()
        self.anomaly_data = anomaly_data.copy()
        self.liquidity_data = liquidity_data.copy()
        self.risk_data = risk_data.copy()
        self.trades = []
        
    def generate_buy_signals(self, anomaly_threshold=1.5, liquidity_threshold=50):
        """生成买信号"""
        buy_signals = (
            (self.anomaly_data['Returns_ZScore'] < -anomaly_threshold) &
            (self.liquidity_data['Market_Depth_Score'] > liquidity_threshold)
        ).astype(int)
        return buy_signals
    
    def generate_sell_signals(self, anomaly_threshold=1.5, profit_target=0.05):
        """生成卖信号"""
        # 简单规则: 异常触顶或获利回吐
        sell_signals = (
            (self.anomaly_data['Returns_ZScore'] > anomaly_threshold) |
            (self.price_data['Returns'].rolling(5).sum() > profit_target)
        ).astype(int)
        return sell_signals
    
    def backtest_strategy(self, initial_capital=100000, position_size=1000, 
                         buy_threshold=50, sell_threshold=30):
        """执行回测"""
        portfolio_value = initial_capital
        position = 0
        trades = []
        equity_curve = [initial_capital]
        
        buy_signals = self.generate_buy_signals(anomaly_threshold=buy_threshold/100)
        sell_signals = self.generate_sell_signals(anomaly_threshold=sell_threshold/100)
        
        for i in range(len(self.price_data)):
            price = self.price_data['Close'].iloc[i]
            
            # 买信号
            if buy_signals.iloc[i] and position == 0:
                position = position_size
                entry_price = price
                trades.append({
                    'Date': self.price_data.index[i],
                    'Action': 'BUY',
                    'Price': price,
                    'Qty': position_size
                })
            
            # 卖信号
            elif sell_signals.iloc[i] and position > 0:
                pnl = (price - entry_price) * position
                pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0
                position = 0
                portfolio_value += pnl
                trades.append({
                    'Date': self.price_data.index[i],
                    'Action': 'SELL',
                    'Price': price,
                    'PnL': pnl,
                    'PnL%': pnl_pct
                })
            
            equity_curve.append(portfolio_value)
        
        self.trades = pd.DataFrame(trades)
        self.equity_curve = pd.Series(equity_curve, index=self.price_data.index)
        return self.trades
    
    def calculate_performance_metrics(self):
        """计算性能指标"""
        if self.equity_curve is None:
            return None
        
        returns = self.equity_curve.pct_change().dropna()
        final_value = self.equity_curve.iloc[-1]
        initial_value = self.equity_curve.iloc[0]
        total_return = (final_value - initial_value) / initial_value
        
        # 夏普比率
        sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # 最大回撤
        cummax = self.equity_curve.cummax()
        drawdown = (self.equity_curve - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 胜率
        if len(self.trades) > 0:
            winning_trades = len(self.trades[self.trades.get('PnL', 0) > 0])
            win_rate = winning_trades / len(self.trades) if len(self.trades) > 0 else 0
        else:
            win_rate = 0
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'num_trades': len(self.trades)
        }
