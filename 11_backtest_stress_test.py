# -*- coding: utf-8 -*-
"""
模块11：回测与压力测试系统 (Backtest & Stress Testing)

功能：
  • 完整的策略回测框架
  • 多种压力测试场景
  • 绩效指标完整计算
  • 压力测试结果分析

测试场景：
  1. 正常行情：平稳上升/下降
  2. 高波动：VIX飙升、日内跳空
  3. 崩盘：快速大幅下跌
  4. 极端事件：限涨停/限跌停
  5. 流动性枯竭：交易量骤降
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from enum import Enum


class StressScenario(Enum):
    """压力测试场景枚举"""
    NORMAL = "正常行情"
    HIGH_VOLATILITY = "高波动率"
    FLASH_CRASH = "快速崩盘"
    LIMIT_DOWN = "限跌停"
    ILLIQUID = "流动性枯竭"
    CORRELATION_BREAKDOWN = "相关性破裂"


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 100000, commission_rate: float = 0.001):
        """
        初始化回测引擎
        
        参数:
            initial_capital: 初始资本
            commission_rate: 佣金率（单程）
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(self, df: pd.DataFrame, signals: pd.Series,
                    position_size: float = 0.1) -> Dict:
        """
        执行回测
        
        参数:
            df: 包含价格数据的DataFrame
            signals: 交易信号序列 (1=买，-1=卖，0=持仓)
            position_size: 每次交易的头寸大小
        
        返回:
            {
                'trades': 交易列表,
                'equity_curve': 权益曲线,
                'metrics': 性能指标
            }
        """
        cash = self.initial_capital
        position = 0
        entry_price = 0
        entry_date = None
        
        trades = []
        equity_values = [self.initial_capital]
        
        for idx in range(len(df)):
            current_price = df['Close'].iloc[idx]
            current_date = df.index[idx]
            signal = signals.iloc[idx] if idx < len(signals) else 0
            
            # 交易成本
            commission = 0
            
            # 买入信号
            if signal == 1 and position == 0:
                position_value = cash * position_size
                shares = position_value / current_price
                commission = position_value * self.commission_rate
                cash -= position_value + commission
                position = shares
                entry_price = current_price
                entry_date = current_date
            
            # 卖出信号
            elif signal == -1 and position > 0:
                position_value = position * current_price
                commission = position_value * self.commission_rate
                cash += position_value - commission
                
                pnl = position_value - (position * entry_price)
                pnl_pct = (pnl / (position * entry_price)) * 100
                
                trades.append({
                    'entry_date': entry_date,
                    'exit_date': current_date,
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'shares': position,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'commission': commission * 2  # 买入和卖出佣金
                })
                
                position = 0
            
            # 计算权益
            position_value = position * current_price if position > 0 else 0
            equity = cash + position_value
            equity_values.append(equity)
        
        # 计算性能指标
        equity_curve = pd.Series(equity_values[1:], index=df.index)
        metrics = self._calculate_metrics(df, equity_curve, trades)
        
        return {
            'trades': trades,
            'equity_curve': equity_curve,
            'metrics': metrics
        }
    
    def _calculate_metrics(self, df: pd.DataFrame, equity_curve: pd.Series,
                          trades: List[Dict]) -> Dict:
        """计算回测指标"""
        
        # 基础指标
        total_return = (equity_curve.iloc[-1] - self.initial_capital) / self.initial_capital
        
        # 计算最大回撤
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 计算年化收益
        trading_days = len(df)
        trading_years = trading_days / 252
        annualized_return = (1 + total_return) ** (1 / max(trading_years, 0.1)) - 1
        
        # 计算夏普比率
        daily_returns = equity_curve.pct_change().dropna()
        sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252) if daily_returns.std() > 0 else 0
        
        # 交易统计
        if trades:
            winning_trades = [t for t in trades if t['pnl'] > 0]
            losing_trades = [t for t in trades if t['pnl'] < 0]
            
            win_rate = len(winning_trades) / len(trades)
            
            avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
            profit_factor = abs(sum([t['pnl'] for t in winning_trades]) / 
                              sum([t['pnl'] for t in losing_trades])) if losing_trades else 0
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            profit_factor = 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades) if trades else 0,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }


class StressTestEngine:
    """压力测试引擎"""
    
    @staticmethod
    def generate_stress_scenario(df: pd.DataFrame, scenario: StressScenario) -> pd.DataFrame:
        """
        生成压力测试场景
        
        参数:
            df: 原始数据
            scenario: 压力场景
        
        返回:
            修改后的数据
        """
        df_stress = df.copy()
        
        if scenario == StressScenario.NORMAL:
            # 正常场景，返回原数据
            return df_stress
        
        elif scenario == StressScenario.HIGH_VOLATILITY:
            # 高波动率：波动幅度加倍
            df_stress['Close'] = df['Close'] * (1 + (np.random.randn(len(df)) * 0.02))
            df_stress['High'] = df['High'] * (1 + np.abs(np.random.randn(len(df)) * 0.03))
            df_stress['Low'] = df['Low'] * (1 - np.abs(np.random.randn(len(df)) * 0.03))
        
        elif scenario == StressScenario.FLASH_CRASH:
            # 闪崩：突然大幅下跌然后反弹
            crash_idx = len(df) // 3
            df_stress.loc[crash_idx:crash_idx+5, 'Close'] *= 0.95  # 5%快速下跌
            df_stress.loc[crash_idx+5:crash_idx+10, 'Close'] *= 1.02  # 快速反弹
        
        elif scenario == StressScenario.LIMIT_DOWN:
            # 限跌停：单日下跌10%
            worst_day_idx = len(df) // 2
            df_stress.loc[worst_day_idx, 'Close'] *= 0.90
            df_stress.loc[worst_day_idx, 'Low'] *= 0.90
        
        elif scenario == StressScenario.ILLIQUID:
            # 流动性枯竭：点差加大
            df_stress['High'] = df['High'] * 1.02
            df_stress['Low'] = df['Low'] * 0.98
            df_stress['Volume'] = df['Volume'] * 0.3
        
        elif scenario == StressScenario.CORRELATION_BREAKDOWN:
            # 相关性破裂：添加随机冲击
            shocks = np.random.choice([0.95, 0.96, 1.00, 1.04, 1.05], len(df))
            df_stress['Close'] = df['Close'] * shocks
        
        return df_stress
    
    @staticmethod
    def run_stress_test(df: pd.DataFrame, strategy_func, scenarios: List[StressScenario] = None) -> Dict:
        """
        运行压力测试
        
        参数:
            df: 原始数据
            strategy_func: 策略函数
            scenarios: 要测试的场景列表
        
        返回:
            {
                'scenario_results': {
                    '正常行情': {...},
                    '高波动': {...},
                    ...
                },
                'summary': 汇总
            }
        """
        if scenarios is None:
            scenarios = list(StressScenario)
        
        results = {}
        
        for scenario in scenarios:
            # 生成压力数据
            df_stress = StressTestEngine.generate_stress_scenario(df, scenario)
            
            # 运行策略
            signals = strategy_func(df_stress)
            
            # 计算结果（这里简化，实际应用中应完整计算）
            returns = df_stress['Close'].pct_change().dropna()
            
            results[scenario.value] = {
                'max_drawdown': (returns.cumsum().cummax() - returns.cumsum()).min(),
                'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
                'avg_return': returns.mean(),
                'std_dev': returns.std()
            }
        
        return {
            'scenario_results': results,
            'most_resilient': max(results.items(), key=lambda x: x[1]['sharpe_ratio'])[0],
            'most_vulnerable': min(results.items(), key=lambda x: x[1]['sharpe_ratio'])[0]
        }


class PerformanceAnalyzer:
    """性能分析器"""
    
    @staticmethod
    def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        计算风险价值 (Value at Risk)
        
        参数:
            returns: 收益序列
            confidence_level: 置信水平（95%表示5%的概率超过该损失）
        
        返回:
            VaR值
        """
        return returns.quantile(1 - confidence_level)
    
    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        计算条件风险价值 (Conditional Value at Risk / Expected Shortfall)
        """
        var_threshold = returns.quantile(1 - confidence_level)
        return returns[returns <= var_threshold].mean()
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, target_return: float = 0) -> float:
        """
        计算索提诺比率 - 只考虑下行风险
        """
        downside_returns = returns[returns < target_return]
        if len(downside_returns) == 0:
            return 0
        
        excess_return = returns.mean() - target_return
        downside_std = downside_returns.std()
        
        return excess_return / downside_std if downside_std > 0 else 0
    
    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series) -> float:
        """
        计算卡玛比率 = 年化收益 / 最大回撤
        """
        cumulative_returns = (1 + returns).cumprod()
        max_drawdown = (cumulative_returns.cummax() - cumulative_returns).max() / cumulative_returns.max()
        annual_return = (cumulative_returns.iloc[-1] ** (252 / len(returns)) - 1)
        
        return annual_return / max_drawdown if max_drawdown > 0 else 0
    
    @staticmethod
    def analyze_drawdown_periods(equity_curve: pd.Series) -> List[Dict]:
        """
        分析所有回撤期间
        
        返回:
            [{
                'start_date': 开始时间,
                'end_date': 结束时间,
                'depth': 回撤深度,
                'duration_days': 持续天数,
                'recovery_time': 恢复所需天数
            }]
        """
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        
        # 检测回撤开始和结束
        drawdown_periods = []
        in_drawdown = False
        start_idx = None
        
        for i in range(len(drawdown)):
            if drawdown.iloc[i] < -0.001 and not in_drawdown:  # 开始回撤
                in_drawdown = True
                start_idx = i
            elif drawdown.iloc[i] >= 0 and in_drawdown:  # 回撤恢复
                in_drawdown = False
                
                depth = drawdown.iloc[start_idx:i].min()
                duration = i - start_idx
                
                drawdown_periods.append({
                    'start_date': equity_curve.index[start_idx],
                    'end_date': equity_curve.index[i],
                    'depth': depth,
                    'duration_days': duration,
                    'recovery_time': duration  # 简化计算
                })
        
        return drawdown_periods
    
    @staticmethod
    def generate_performance_report(backtest_result: Dict) -> str:
        """
        生成性能报告
        """
        metrics = backtest_result['metrics']
        trades = backtest_result['trades']
        
        report = f"""
{'='*60}
策略性能报告
{'='*60}

【总体绩效】
  总收益率: {metrics['total_return']*100:.2f}%
  年化收益率: {metrics['annualized_return']*100:.2f}%
  最大回撤: {metrics['max_drawdown']*100:.2f}%
  夏普比率: {metrics['sharpe_ratio']:.2f}

【交易统计】
  总交易次数: {metrics['total_trades']}
  盈利交易: {metrics['winning_trades']}
  胜率: {metrics['win_rate']*100:.2f}%
  平均盈利: ${metrics['avg_win']:.2f}
  平均亏损: ${metrics['avg_loss']:.2f}
  利润因子: {metrics['profit_factor']:.2f}

{'='*60}
"""
        return report
