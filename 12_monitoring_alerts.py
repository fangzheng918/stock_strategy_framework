# -*- coding: utf-8 -*-
"""
模块12：监控与告警系统 (Monitoring & Alert System)

功能：
  • Kill-Switch 机制 - N分钟中止或盘口停止
  • 异常波动检测 - 自动告警
  • 违规交易检测 - 合规监控
  • 实时风险监控 - 持仓监控
  • 自动止战规则 - 多种停止条件

核心规则：
  1. 连续N分钟中止 → 停止交易
  2. 点差异常 → 停止交易
  3. 盘口撕裂 → 停止交易
  4. 最大回撤触发 → 停止交易
  5. 异常订单 → 告警
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from enum import Enum
from datetime import datetime, timedelta


class AlertLevel(Enum):
    """告警级别"""
    INFO = "信息"
    WARNING = "警告"
    CRITICAL = "严重"
    KILL_SWITCH = "紧急停止"


class MonitoringSystem:
    """交易监控系统"""
    
    def __init__(self):
        self.alerts = []
        self.kill_switch_active = False
        self.kill_switch_reason = None
        self.monitoring_start_time = datetime.now()
    
    def check_kill_switch(self, df: pd.DataFrame, current_drawdown: float,
                         max_drawdown_limit: float = -0.20,
                         halt_duration_minutes: int = 5) -> Dict:
        """
        Kill-Switch 检测 - 触发紧急停止交易
        
        触发条件：
        1. 最大回撤超过限制（如-20%）
        2. 点差异常扩大
        3. 连续中止超过N分钟
        
        参数:
            df: 市场数据
            current_drawdown: 当前回撤
            max_drawdown_limit: 回撤限制
            halt_duration_minutes: 中止持续时间
        
        返回:
            {
                'kill_switch_active': bool,
                'reason': 触发原因,
                'action': 建议行动
            }
        """
        reasons = []
        
        # 检查1：最大回撤限制
        if current_drawdown <= max_drawdown_limit:
            reasons.append(f'❌ 最大回撤超过限制：{current_drawdown*100:.2f}% < {max_drawdown_limit*100:.2f}%')
        
        # 检查2：点差异常
        if len(df) > 1:
            recent_spread = (df['High'].iloc[-1] - df['Low'].iloc[-1]) / df['Close'].iloc[-1]
            avg_spread = ((df['High'] - df['Low']) / df['Close']).mean()
            spread_ratio = recent_spread / avg_spread if avg_spread > 0 else 1
            
            if spread_ratio > 3.0:  # 点差扩大3倍以上
                reasons.append(f'❌ 点差异常扩大：{spread_ratio:.1f}倍')
        
        # 检查3：市场停止
        recent_volume = df['Volume'].tail(5).mean()
        if recent_volume == 0:
            reasons.append('❌ 市场停止交易（成交量为0）')
        
        kill_switch_triggered = len(reasons) > 0
        
        if kill_switch_triggered:
            self.kill_switch_active = True
            self.kill_switch_reason = reasons[0]
        
        return {
            'kill_switch_active': kill_switch_triggered,
            'reasons': reasons,
            'halt_duration_minutes': halt_duration_minutes if kill_switch_triggered else 0,
            'action': '⛔ 停止所有交易！' if kill_switch_triggered else '✅ 交易继续',
            'recommendations': [
                '立即平仓所有头寸',
                '进行风险评估',
                f'等待{halt_duration_minutes}分钟后重新评估'
            ] if kill_switch_triggered else []
        }
    
    def detect_market_anomalies(self, df: pd.DataFrame) -> List[Dict]:
        """
        检测市场异常
        
        异常类型：
        • 跳空缺口：当日开盘价与前日收盘价偏离>5%
        • 极限涨停/跌停：日内涨/跌>9.8%
        • 成交量异常：突然下跌或爆增
        • 点差异常：bid-ask点差异常扩大
        
        返回:
            告警列表
        """
        anomalies = []
        
        if len(df) < 2:
            return anomalies
        
        # 异常1：跳空缺口
        gap = (df['Open'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]
        if abs(gap) > 0.05:
            anomalies.append({
                'type': '跳空缺口',
                'level': AlertLevel.WARNING,
                'description': f'当日开盘价跳空{abs(gap)*100:.2f}%',
                'value': gap
            })
        
        # 异常2：极限涨/跌停
        daily_return = (df['Close'].iloc[-1] - df['Open'].iloc[-1]) / df['Open'].iloc[-1]
        if abs(daily_return) > 0.098:
            anomalies.append({
                'type': '极限涨跌',
                'level': AlertLevel.CRITICAL,
                'description': f'日内涨跌{abs(daily_return)*100:.2f}%，接近涨跌停',
                'value': daily_return
            })
        
        # 异常3：成交量异常
        recent_volume = df['Volume'].tail(5).mean()
        historical_volume = df['Volume'].tail(30).mean()
        if recent_volume < historical_volume * 0.3:
            anomalies.append({
                'type': '成交量异常',
                'level': AlertLevel.WARNING,
                'description': f'最近成交量仅为历史平均的{recent_volume/historical_volume*100:.1f}%',
                'value': recent_volume / historical_volume
            })
        elif recent_volume > historical_volume * 3:
            anomalies.append({
                'type': '成交量爆增',
                'level': AlertLevel.WARNING,
                'description': f'成交量为历史平均的{recent_volume/historical_volume*100:.1f}%',
                'value': recent_volume / historical_volume
            })
        
        # 异常4：点差异常
        spread = (df['High'].iloc[-1] - df['Low'].iloc[-1]) / df['Close'].iloc[-1]
        avg_spread = ((df['High'] - df['Low']) / df['Close']).mean()
        if spread > avg_spread * 2:
            anomalies.append({
                'type': '点差扩大',
                'level': AlertLevel.WARNING,
                'description': f'点差为平均的{spread/avg_spread:.1f}倍',
                'value': spread / avg_spread
            })
        
        return anomalies
    
    def detect_trading_violations(self, trade_record: Dict, daily_limit_pct: float = 0.1) -> List[str]:
        """
        检测交易违规
        
        检查项：
        • 超日成交限制
        • 滑点过大
        • 订单价格异常
        • 频繁撤单
        
        参数:
            trade_record: 交易记录
            daily_limit_pct: 日成交限制
        
        返回:
            违规列表
        """
        violations = []
        
        # 检查1：超日成交限制
        if trade_record.get('daily_volume_pct', 0) > daily_limit_pct:
            violations.append(f'❌ 日成交量超限：{trade_record["daily_volume_pct"]*100:.1f}% > {daily_limit_pct*100:.1f}%')
        
        # 检查2：滑点过大
        slippage_pct = trade_record.get('slippage_pct', 0)
        if slippage_pct > 0.5:
            violations.append(f'⚠️ 滑点过大：{slippage_pct:.2f}%')
        
        # 检查3：订单价格异常
        if trade_record.get('order_price_abnormal', False):
            violations.append('⚠️ 订单价格异常')
        
        # 检查4：频繁撤单
        cancellation_rate = trade_record.get('cancellation_rate', 0)
        if cancellation_rate > 0.3:  # 撤单率>30%
            violations.append(f'⚠️ 撤单频繁：{cancellation_rate*100:.1f}%')
        
        return violations
    
    def monitor_position_risk(self, positions: Dict, portfolio_value: float,
                             var_limit_pct: float = 0.02) -> Dict:
        """
        监控持仓风险
        
        检查项：
        • 单个头寸占比
        • 总VaR
        • 集中风险
        
        参数:
            positions: 头寸字典 {'asset1': 10000, 'asset2': 5000}
            portfolio_value: 投资组合总价值
            var_limit_pct: VaR限制（占比例）
        
        返回:
            风险报告
        """
        total_position = sum(positions.values())
        
        risks = {
            'concentration_risks': [],
            'var_warning': False,
            'rebalance_needed': False
        }
        
        # 检查1：单个头寸集中度
        for asset, value in positions.items():
            weight = value / portfolio_value if portfolio_value > 0 else 0
            
            if weight > 0.3:  # 单个头寸超过30%
                risks['concentration_risks'].append({
                    'asset': asset,
                    'weight': weight,
                    'warning': '单个头寸过高'
                })
                risks['rebalance_needed'] = True
        
        # 检查2：总VaR
        total_var = total_position * var_limit_pct
        var_limit = portfolio_value * var_limit_pct
        
        if total_var > var_limit:
            risks['var_warning'] = True
        
        return risks
    
    def auto_stop_trading_rules(self, equity_curve: pd.Series, num_losing_trades: int,
                               max_consecutive_losses: int = 5) -> Dict:
        """
        自动止战规则 - 多种停止交易的条件
        
        规则：
        1. 连续亏损N笔后停止
        2. 日内亏损超过X% 停止
        3. 账户权益跌破Y%停止
        
        参数:
            equity_curve: 权益曲线
            num_losing_trades: 连续亏损笔数
            max_consecutive_losses: 最大允许连续亏损
        
        返回:
            {
                'should_stop': bool,
                'reasons': 停止原因列表
            }
        """
        reasons = []
        
        # 规则1：连续亏损
        if num_losing_trades >= max_consecutive_losses:
            reasons.append(f'❌ 连续亏损{num_losing_trades}笔')
        
        # 规则2：日内亏损
        daily_return = (equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0]
        if daily_return < -0.05:  # 日内亏损超过5%
            reasons.append(f'❌ 日内亏损{abs(daily_return)*100:.1f}%')
        
        # 规则3：权益跌破
        initial_capital = equity_curve.iloc[0]
        if equity_curve.iloc[-1] < initial_capital * 0.90:  # 权益跌破90%
            reasons.append(f'❌ 账户权益跌破90%')
        
        return {
            'should_stop': len(reasons) > 0,
            'stop_reasons': reasons,
            'action': '停止交易' if len(reasons) > 0 else '继续交易'
        }
    
    def generate_alerts(self, check_results: List[Dict]) -> List[Dict]:
        """
        生成告警信息
        
        返回:
            格式化的告警列表
        """
        alerts = []
        
        for result in check_results:
            alert = {
                'timestamp': datetime.now(),
                'level': result.get('level', AlertLevel.INFO),
                'message': result.get('description', ''),
                'action': result.get('action', ''),
                'details': result
            }
            alerts.append(alert)
            self.alerts.append(alert)
        
        return alerts
    
    def generate_monitoring_report(self) -> str:
        """
        生成监控报告
        """
        report = f"""
{'='*70}
交易监控报告
{'='*70}

【Kill-Switch 状态】
  激活: {'是' if self.kill_switch_active else '否'}
  {'原因: ' + self.kill_switch_reason if self.kill_switch_active else ''}

【告警汇总】
  总告警数: {len(self.alerts)}
  严重告警: {len([a for a in self.alerts if a['level'] == AlertLevel.CRITICAL])}
  警告: {len([a for a in self.alerts if a['level'] == AlertLevel.WARNING])}

【最近告警】
"""
        for alert in self.alerts[-5:]:  # 显示最近5条
            report += f"\n  {alert['timestamp']}: [{alert['level'].value}] {alert['message']}"
        
        report += f"\n\n{'='*70}\n"
        
        return report


class RealTimeRiskMonitor:
    """实时风险监控器"""
    
    def __init__(self):
        self.risk_metrics = {}
    
    def update_risk_metrics(self, current_price: float, entry_price: float,
                           stop_loss: float, take_profit: float,
                           position_size: int) -> Dict:
        """
        实时更新风险指标
        
        返回:
            {
                'current_price': 当前价格,
                'unrealized_pnl': 未实现损益,
                'distance_to_sl': 距止损距离,
                'distance_to_tp': 距止盈距离,
                'status': 头寸状态
            }
        """
        unrealized_pnl = (current_price - entry_price) * position_size
        unrealized_pnl_pct = (current_price - entry_price) / entry_price * 100
        
        distance_to_sl = abs(current_price - stop_loss)
        distance_to_tp = abs(current_price - take_profit)
        distance_to_sl_pct = distance_to_sl / current_price * 100
        distance_to_tp_pct = distance_to_tp / current_price * 100
        
        # 判断状态
        if unrealized_pnl_pct < -3:
            status = '🔴 危险'
        elif unrealized_pnl_pct < 0:
            status = '🟡 亏损'
        elif unrealized_pnl_pct < 2:
            status = '⚪ 小盈利'
        else:
            status = '🟢 盈利'
        
        return {
            'current_price': current_price,
            'entry_price': entry_price,
            'unrealized_pnl': unrealized_pnl,
            'unrealized_pnl_pct': unrealized_pnl_pct,
            'distance_to_sl': distance_to_sl,
            'distance_to_sl_pct': distance_to_sl_pct,
            'distance_to_tp': distance_to_tp,
            'distance_to_tp_pct': distance_to_tp_pct,
            'status': status,
            'alerts': self._generate_position_alerts(
                current_price, stop_loss, take_profit, distance_to_sl_pct, distance_to_tp_pct
            )
        }
    
    @staticmethod
    def _generate_position_alerts(current_price: float, stop_loss: float,
                                 take_profit: float, dist_to_sl_pct: float,
                                 dist_to_tp_pct: float) -> List[str]:
        """生成头寸告警"""
        alerts = []
        
        if dist_to_sl_pct < 1.0:
            alerts.append(f'⚠️ 接近止损：{dist_to_sl_pct:.2f}%')
        
        if dist_to_tp_pct < 1.0:
            alerts.append(f'✅ 接近止盈：{dist_to_tp_pct:.2f}%')
        
        return alerts
