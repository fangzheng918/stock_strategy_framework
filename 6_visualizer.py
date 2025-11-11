"""
模块 6: 结果可视化
功能: 生成分析图表、仪表板、报告
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


class StrategyVisualizer:
    """可视化类"""
    
    def __init__(self, data, trades_df=None):
        self.data = data
        self.trades_df = trades_df
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        
    def plot_price_and_signals(self, output_path='price_signals.png'):
        """绘制价格和交易信号"""
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(self.data.index, self.data['Close'], label='收盘价', linewidth=1.5)
        
        if self.trades_df is not None and len(self.trades_df) > 0:
            buy_trades = self.trades_df[self.trades_df['Action'] == 'BUY']
            sell_trades = self.trades_df[self.trades_df['Action'] == 'SELL']
            
            ax.scatter(buy_trades['Date'], buy_trades['Price'], color='green', 
                      marker='^', label='买点', s=100)
            ax.scatter(sell_trades['Date'], sell_trades['Price'], color='red', 
                      marker='v', label='卖点', s=100)
        
        ax.set_title('价格和交易信号', fontsize=14, fontweight='bold')
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=100)
        plt.close()
    
    def plot_equity_curve(self, equity_curve, output_path='equity_drawdown.png'):
        """绘制权益曲线和回撤"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # 权益曲线
        ax1.plot(equity_curve.index, equity_curve, label='权益曲线', color='blue', linewidth=1.5)
        ax1.fill_between(equity_curve.index, equity_curve, alpha=0.3)
        ax1.set_title('投资组合权益曲线', fontsize=12, fontweight='bold')
        ax1.set_ylabel('权益价值')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 回撤
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax * 100
        ax2.fill_between(drawdown.index, drawdown, alpha=0.5, color='red')
        ax2.plot(drawdown.index, drawdown, color='darkred', linewidth=1.5)
        ax2.set_title('回撤分析', fontsize=12, fontweight='bold')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('回撤 (%)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=100)
        plt.close()
    
    def create_comprehensive_dashboard(self, output_path='dashboard.png'):
        """创建综合仪表板"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
        
        # 收益率分布
        returns = self.data['Returns'].dropna()
        ax1.hist(returns, bins=50, edgecolor='black', alpha=0.7)
        ax1.set_title('收益率分布', fontsize=12, fontweight='bold')
        ax1.set_xlabel('日收益率')
        ax1.axvline(returns.mean(), color='red', linestyle='--', label=f'平均: {returns.mean():.4f}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 价格走势
        ax2.plot(self.data.index, self.data['Close'], linewidth=1.5)
        ax2.set_title('价格走势', fontsize=12, fontweight='bold')
        ax2.set_ylabel('价格')
        ax2.grid(True, alpha=0.3)
        
        # 成交量
        ax3.bar(self.data.index, self.data['Volume'], alpha=0.7, color='steelblue')
        ax3.set_title('成交量', fontsize=12, fontweight='bold')
        ax3.set_ylabel('成交量')
        ax3.grid(True, alpha=0.3)
        
        # 波动率
        volatility = self.data['Returns'].rolling(20).std()
        ax4.plot(self.data.index, volatility, color='orange', linewidth=1.5)
        ax4.fill_between(self.data.index, volatility, alpha=0.3, color='orange')
        ax4.set_title('滚动波动率 (20天)', fontsize=12, fontweight='bold')
        ax4.set_ylabel('波动率')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=100)
        plt.close()
    
    def create_detailed_report(self, output_dir='strategy_analysis_report'):
        """生成详细报告"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        self.plot_price_and_signals(f'{output_dir}/1_price_signals.png')
        self.plot_equity_curve(pd.Series(range(len(self.data))), f'{output_dir}/2_equity_drawdown.png')
        self.create_comprehensive_dashboard(f'{output_dir}/3_comprehensive.png')
        
        print(f"报告已生成到: {output_dir}/")
