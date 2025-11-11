"""
模块 4: 风险管理与头寸控制
功能: 投资组合风险跟踪、VaR/CVaR 计算、止损设置、头寸规模调整
"""

import pandas as pd
import numpy as np
from scipy import stats


class RiskManager:
    """风险管理类"""
    
    def __init__(self, data, initial_capital=100000, position_size=1000, max_drawdown=0.1):
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.max_drawdown = max_drawdown
        self.portfolio_value = initial_capital
        
    def calculate_portfolio_value(self, returns):
        """计算投资组合价值"""
        cumulative_returns = (1 + returns).cumprod()
        self.data['Portfolio_Value'] = self.initial_capital * cumulative_returns
        return self.data['Portfolio_Value']
    
    def calculate_var(self, confidence=0.95):
        """计算风险价值 (VaR)"""
        returns = self.data['Returns'].dropna()
        var = np.percentile(returns, (1 - confidence) * 100)
        self.data['VaR_Amount'] = self.portfolio_value * abs(var)
        return var
    
    def calculate_cvar(self, confidence=0.95):
        """计算条件风险价值 (CVaR/Expected Shortfall)"""
        returns = self.data['Returns'].dropna()
        var = np.percentile(returns, (1 - confidence) * 100)
        cvar = returns[returns <= var].mean()
        self.data['CVaR_Amount'] = self.portfolio_value * abs(cvar)
        return cvar
    
    def calculate_drawdown(self):
        """计算回撤"""
        cummax = self.data['Portfolio_Value'].cummax()
        self.data['Drawdown'] = (self.data['Portfolio_Value'] - cummax) / cummax
        self.data['Drawdown_Pct'] = self.data['Drawdown'] * 100
        return self.data['Drawdown_Pct']
    
    def check_max_drawdown(self):
        """检查最大回撤是否超限"""
        max_dd = self.data['Drawdown'].min()
        return max_dd >= self.max_drawdown, max_dd
    
    def calculate_stop_loss_price(self, entry_price, atr=None):
        """计算止损价格"""
        if atr is None:
            # 基于波动率计算 ATR
            high_low = self.data['High'] - self.data['Low']
            atr = high_low.rolling(14).mean().iloc[-1]
        
        stop_loss = entry_price - atr * 2
        return stop_loss
    
    def adjust_position_size(self, volatility_adjusted=True):
        """调整头寸规模"""
        if volatility_adjusted:
            volatility = self.data['Returns'].rolling(20).std().iloc[-1]
            base_volatility = self.data['Returns'].std()
            adjustment_factor = base_volatility / volatility if volatility > 0 else 1
            self.adjusted_position_size = int(self.position_size * adjustment_factor)
        else:
            self.adjusted_position_size = self.position_size
        
        return self.adjusted_position_size
    
    def get_risk_summary(self, entry_price=100):
        """获取风险摘要"""
        self.calculate_portfolio_value(self.data['Returns'])
        self.calculate_drawdown()
        
        return {
            'portfolio_value': self.data['Portfolio_Value'].iloc[-1],
            'max_drawdown': self.data['Drawdown'].min(),
            'var_95': self.calculate_var(0.95),
            'cvar_95': self.calculate_cvar(0.95),
            'stop_loss_price': self.calculate_stop_loss_price(entry_price),
            'adjusted_position_size': self.adjust_position_size()
        }
