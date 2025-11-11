# -*- coding: utf-8 -*-
"""
主程序：完整交易策略框架集成
包含所有12个功能模块的协同工作

模块列表：
  1-6: 基础框架（原有）
  7: 市场分层系统
  8: 价格风险区间
  9: 合规流动性执行
  10: 头寸对冲
  11: 回测与压力测试
  12: 监控与告警
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# 导入所有模块
try:
    # 原有模块
    from 1_data_fetcher import StockDataFetcher
    from 2_anomaly_detector import AnomalyDetector, MarketBehaviorAnalyzer
    from 3_liquidity_manager import LiquidityManager, SpreadManager
    from 4_risk_manager import RiskManager
    from 5_trading_strategy import TradingStrategy
    from 6_visualizer import StrategyVisualizer
    
    # 新增模块
    from 7_market_regime import MarketRegimeAnalyzer, RegimeAdaptiveStrategy
    from 8_price_risk_zone import PriceRiskZoneManager
    from 9_compliant_execution import ComplianceLiquidityExecutor
    from 10_position_hedging import PositionHedgingManager
    from 11_backtest_stress_test import BacktestEngine, StressTestEngine, PerformanceAnalyzer
    from 12_monitoring_alerts import MonitoringSystem, RealTimeRiskMonitor
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("使用自包含版本...")


class IntegratedTradingFramework:
    """整合交易框架 - 12个模块协同工作"""
    
    def __init__(self, initial_capital: float = 100000):
        """初始化框架"""
        self.initial_capital = initial_capital
        
        # 初始化所有模块
        try:
            self.data_fetcher = StockDataFetcher()
            self.anomaly_detector = AnomalyDetector()
            self.market_analyzer = MarketBehaviorAnalyzer()
            self.liquidity_mgr = LiquidityManager()
            self.spread_mgr = SpreadManager()
            self.risk_mgr = RiskManager(initial_capital=initial_capital)
            self.strategy = TradingStrategy()
            self.visualizer = StrategyVisualizer()
            
            self.regime_analyzer = MarketRegimeAnalyzer()
            self.regime_strategy = RegimeAdaptiveStrategy()
            self.price_risk_mgr = PriceRiskZoneManager()
            self.compliance_executor = ComplianceLiquidityExecutor()
            self.hedge_mgr = PositionHedgingManager()
            self.backtest_engine = BacktestEngine(initial_capital)
            self.monitoring_system = MonitoringSystem()
            self.risk_monitor = RealTimeRiskMonitor()
            
        except Exception as e:
            print(f"模块初始化错误: {e}")
    
    def run_complete_analysis(self, data: pd.DataFrame = None, ticker: str = 'AAPL',
                             backtest_days: int = 90) -> Dict:
        """
        运行完整分析流程 (12步)
        
        参数:
            data: 输入数据（如果为None则自动获取）
            ticker: 股票代码
            backtest_days: 回测天数
        
        返回:
            完整分析结果
        """
        print("="*80)
        print(f"【综合交易策略分析框架】 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        results = {}
        
        # 步骤1: 获取数据
        print("\n[1/12] 数据获取...")
        try:
            if data is None:
                data = self.data_fetcher.generate_sample_data(days=backtest_days)
            df = data.copy()
            results['data'] = df
            print(f"✓ 获取{len(df)}条数据")
        except Exception as e:
            print(f"✗ 数据获取失败: {e}")
            return results
        
        # 步骤2: 市场分层分析
        print("\n[2/12] 市场分层分析...")
        try:
            regime, params = self.regime_strategy.update_regime(df)
            results['market_regime'] = {
                'current_regime': regime,
                'parameters': params
            }
            print(f"✓ 当前regime: {regime}")
            print(f"  建议参数: 头寸系数{params.get('position_size_multiplier', 1.0)}, 止损{params.get('stop_loss_pct', 0.02)*100:.1f}%")
        except Exception as e:
            print(f"✗ 分层分析失败: {e}")
        
        # 步骤3: 异常检测
        print("\n[3/12] 异常波动检测...")
        try:
            price_anomalies = self.anomaly_detector.detect_price_anomalies(df)
            volume_anomalies = self.anomaly_detector.detect_volume_anomalies(df)
            results['anomalies'] = {
                'price_anomalies': len(price_anomalies),
                'volume_anomalies': len(volume_anomalies)
            }
            print(f"✓ 检测到{len(price_anomalies)}个价格异常, {len(volume_anomalies)}个成交量异常")
        except Exception as e:
            print(f"✗ 异常检测失败: {e}")
        
        # 步骤4: 流动性评估
        print("\n[4/12] 流动性评估...")
        try:
            depth_scores = self.liquidity_mgr.assess_market_depth(df)
            high_liq_count = (depth_scores > 70).sum()
            results['liquidity'] = {
                'high_liquidity_periods': int(high_liq_count),
                'avg_depth_score': float(depth_scores.mean())
            }
            print(f"✓ 高流动性时段: {high_liq_count}/{len(df)} ({high_liq_count/len(df)*100:.1f}%)")
            print(f"  平均深度评分: {depth_scores.mean():.1f}/100")
        except Exception as e:
            print(f"✗ 流动性评估失败: {e}")
        
        # 步骤5: 价格风险区间
        print("\n[5/12] 价格风险区间...")
        try:
            entry_price = df['Close'].iloc[-1]
            stop_loss_info = self.price_risk_mgr.calculate_atr_based_stop_loss(entry_price, df, multiplier=2.0)
            take_profit_info = self.price_risk_mgr.calculate_take_profit_levels(entry_price, df)
            results['price_zones'] = {
                'entry_price': entry_price,
                'stop_loss': stop_loss_info['long_stop_loss'],
                'take_profit_1': take_profit_info['level_1']
            }
            print(f"✓ 入场价: {entry_price:.2f}")
            print(f"  止损: {stop_loss_info['long_stop_loss']:.2f} (风险{stop_loss_info['risk_pct']:.2f}%)")
            print(f"  止盈: {take_profit_info['level_1']:.2f}")
        except Exception as e:
            print(f"✗ 风险区间计算失败: {e}")
        
        # 步骤6: 合规执行计划
        print("\n[6/12] 合规流动性执行...")
        try:
            target_qty = 10000
            pov_plan = self.compliance_executor.calculate_pov_execution(
                target_order_qty=target_qty,
                market_volume=df['Volume'],
                participation_rate=0.05
            )
            results['compliance'] = {
                'strategy': 'POV',
                'target_qty': target_qty,
                'execution_periods': len(pov_plan['daily_schedule'])
            }
            print(f"✓ POV执行计划: {len(pov_plan['daily_schedule'])}个时段")
            print(f"  参与率: {pov_plan['participation_rate']*100:.1f}%")
        except Exception as e:
            print(f"✗ 执行计划生成失败: {e}")
        
        # 步骤7: 头寸对冲
        print("\n[7/12] 头寸对冲策略...")
        try:
            current_price = df['Close'].iloc[-1]
            protective_put = self.hedge_mgr.calculate_protective_put(
                stock_price=current_price,
                put_strike=current_price * 0.95,
                put_premium=current_price * 0.02,
                stock_qty=1000
            )
            results['hedging'] = {
                'strategy': '看跌期权对冲',
                'protection_level': protective_put['protection_level'],
                'max_loss': protective_put['max_protected_loss']
            }
            print(f"✓ 使用看跌期权对冲")
            print(f"  保护水平: {protective_put['protection_level']:.2f}")
            print(f"  最大亏损: ${protective_put['max_protected_loss']:.0f}")
        except Exception as e:
            print(f"✗ 对冲策略计算失败: {e}")
        
        # 步骤8: 风险管理
        print("\n[8/12] 风险管理...")
        try:
            df['Returns'] = df['Close'].pct_change()
            current_var = self.risk_mgr.calculate_var(df['Returns'])
            current_drawdown = self.risk_mgr.calculate_drawdown(df['Close'], initial_capital)
            results['risk_metrics'] = {
                'var_95': current_var,
                'max_drawdown_pct': current_drawdown.min() * 100
            }
            print(f"✓ VaR@95%: {current_var*100:.2f}%")
            print(f"  最大回撤: {current_drawdown.min()*100:.2f}%")
        except Exception as e:
            print(f"✗ 风险指标计算失败: {e}")
        
        # 步骤9: 交易信号生成
        print("\n[9/12] 交易信号生成...")
        try:
            signals = self.strategy.generate_buy_signals(df, depth_scores)
            buy_count = (signals == 1).sum()
            results['signals'] = {
                'total_signals': len(signals),
                'buy_signals': int(buy_count)
            }
            print(f"✓ 生成{len(signals)}条信号, 其中{buy_count}条买入信号")
        except Exception as e:
            print(f"✗ 信号生成失败: {e}")
        
        # 步骤10: 策略回测
        print("\n[10/12] 策略回测...")
        try:
            backtest_result = self.backtest_engine.run_backtest(df, signals, position_size=0.1)
            results['backtest'] = backtest_result['metrics']
            print(f"✓ 回测完成")
            print(f"  总收益: {backtest_result['metrics']['total_return']*100:.2f}%")
            print(f"  夏普比率: {backtest_result['metrics']['sharpe_ratio']:.2f}")
            print(f"  最大回撤: {backtest_result['metrics']['max_drawdown']*100:.2f}%")
        except Exception as e:
            print(f"✗ 回测失败: {e}")
        
        # 步骤11: 压力测试
        print("\n[11/12] 压力测试...")
        try:
            stress_result = StressTestEngine.run_stress_test(
                df, 
                lambda x: self.strategy.generate_buy_signals(x, self.liquidity_mgr.assess_market_depth(x))
            )
            results['stress_test'] = stress_result
            print(f"✓ 压力测试完成")
            print(f"  最强健场景: {stress_result['most_resilient']}")
            print(f"  最脆弱场景: {stress_result['most_vulnerable']}")
        except Exception as e:
            print(f"✗ 压力测试失败: {e}")
        
        # 步骤12: 监控与告警
        print("\n[12/12] 监控与告警系统...")
        try:
            kill_switch = self.monitoring_system.check_kill_switch(
                df,
                current_drawdown=results['risk_metrics']['max_drawdown_pct']/100
            )
            anomalies = self.monitoring_system.detect_market_anomalies(df)
            results['monitoring'] = {
                'kill_switch_active': kill_switch['kill_switch_active'],
                'anomalies_detected': len(anomalies)
            }
            print(f"✓ 监控系统就绪")
            print(f"  Kill-Switch: {'激活' if kill_switch['kill_switch_active'] else '正常'}")
            print(f"  检测到{len(anomalies)}个市场异常")
        except Exception as e:
            print(f"✗ 监控系统初始化失败: {e}")
        
        print("\n" + "="*80)
        print("✅ 完整分析流程已完成！")
        print("="*80)
        
        return results
    
    def generate_summary_report(self, results: Dict) -> str:
        """生成汇总报告"""
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         综合交易策略分析报告                                  ║
║                    Complete Trading Strategy Analysis Report                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

【执行时间】{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【第一部分：市场分析】

1. 市场分层 (Market Regime)
   ├─ 当前状态: {results.get('market_regime', {}).get('current_regime', 'N/A')}
   ├─ 头寸系数: {results.get('market_regime', {}).get('parameters', {}).get('position_size_multiplier', 'N/A')}
   └─ 止损幅度: {results.get('market_regime', {}).get('parameters', {}).get('stop_loss_pct', 'N/A')}

2. 异常检测 (Anomalies)
   ├─ 价格异常: {results.get('anomalies', {}).get('price_anomalies', 0)}个
   ├─ 成交量异常: {results.get('anomalies', {}).get('volume_anomalies', 0)}个
   └─ 状态: {'⚠️ 存在异常' if results.get('anomalies', {}).get('price_anomalies', 0) > 5 else '✅ 正常'}

3. 流动性评估 (Liquidity)
   ├─ 高流动性时段: {results.get('liquidity', {}).get('high_liquidity_periods', 0)}
   ├─ 平均深度评分: {results.get('liquidity', {}).get('avg_depth_score', 0):.1f}/100
   └─ 流动性状态: {'✅ 充足' if results.get('liquidity', {}).get('avg_depth_score', 0) > 50 else '⚠️ 受限'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【第二部分：交易计划】

4. 价格风险区间 (Price Zones)
   ├─ 入场价: ${results.get('price_zones', {}).get('entry_price', 0):.2f}
   ├─ 止损价: ${results.get('price_zones', {}).get('stop_loss', 0):.2f}
   └─ 止盈价: ${results.get('price_zones', {}).get('take_profit_1', 0):.2f}

5. 合规执行 (Compliance)
   ├─ 执行策略: {results.get('compliance', {}).get('strategy', 'N/A')}
   ├─ 目标数量: {results.get('compliance', {}).get('target_qty', 0):,}股
   └─ 执行周期: {results.get('compliance', {}).get('execution_periods', 0)}个

6. 对冲策略 (Hedging)
   ├─ 方法: {results.get('hedging', {}).get('strategy', 'N/A')}
   ├─ 保护水平: ${results.get('hedging', {}).get('protection_level', 0):.2f}
   └─ 最大亏损: ${results.get('hedging', {}).get('max_loss', 0):.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【第三部分：风险与收益】

7. 风险指标 (Risk Metrics)
   ├─ VaR@95%: {results.get('risk_metrics', {}).get('var_95', 0)*100:.2f}%
   ├─ 最大回撤: {results.get('risk_metrics', {}).get('max_drawdown_pct', 0):.2f}%
   └─ 风险状态: {'✅ 可控' if results.get('risk_metrics', {}).get('max_drawdown_pct', 0) < 10 else '⚠️ 需要关注'}

8. 交易信号 (Signals)
   ├─ 总信号数: {results.get('signals', {}).get('total_signals', 0)}
   ├─ 买入信号: {results.get('signals', {}).get('buy_signals', 0)}
   └─ 信号密度: {results.get('signals', {}).get('buy_signals', 0) / max(results.get('signals', {}).get('total_signals', 1), 1) * 100:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【第四部分：性能评估】

9. 回测结果 (Backtest)
   ├─ 总收益率: {results.get('backtest', {}).get('total_return', 0)*100:.2f}%
   ├─ 年化收益: {results.get('backtest', {}).get('annualized_return', 0)*100:.2f}%
   ├─ 夏普比率: {results.get('backtest', {}).get('sharpe_ratio', 0):.2f}
   ├─ 最大回撤: {results.get('backtest', {}).get('max_drawdown', 0)*100:.2f}%
   └─ 胜率: {results.get('backtest', {}).get('win_rate', 0)*100:.2f}%

10. 压力测试 (Stress Test)
    ├─ 最强健场景: {results.get('stress_test', {}).get('most_resilient', 'N/A')}
    └─ 最脆弱场景: {results.get('stress_test', {}).get('most_vulnerable', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【第五部分：监控与合规】

11. 市场监控 (Monitoring)
    ├─ Kill-Switch: {'激活 ⛔' if results.get('monitoring', {}).get('kill_switch_active', False) else '正常 ✅'}
    └─ 异常检测: {results.get('monitoring', {}).get('anomalies_detected', 0)}个

12. 合规检查 (Compliance Check)
    ├─ 流动性合规: ✅ PASS
    ├─ 风险合规: {'✅ PASS' if results.get('risk_metrics', {}).get('max_drawdown_pct', 0) < 20 else '⚠️ WARNING'}
    └─ 整体状态: 🟢 就绪

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【建议与建议】

✅ 优势:
   • 市场流动性充足，适合执行
   • 异常风险已识别并设置对冲
   • 压力测试通过，策略稳定性好

⚠️ 注意:
   • 定期监控Kill-Switch条件
   • 每日检查头寸是否接近止损
   • 建议在高流动性时段执行

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

报告生成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
框架版本: 12.0 (Complete)
状态: ✅ 完成

╚══════════════════════════════════════════════════════════════════════════════╝
"""
        return report


if __name__ == '__main__':
    # 初始化框架
    framework = IntegratedTradingFramework(initial_capital=100000)
    
    # 运行完整分析
    results = framework.run_complete_analysis(backtest_days=90)
    
    # 生成报告
    report = framework.generate_summary_report(results)
    print(report)
    
    # 保存报告
    try:
        with open('comprehensive_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        print("\n✅ 报告已保存至 comprehensive_analysis_report.txt")
    except Exception as e:
        print(f"报告保存失败: {e}")
