# -*- coding: utf-8 -*-
"""
参数示例与配置文件 (Parameters & Configuration Examples)

包含所有12个模块的推荐参数配置
可根据不同风险偏好调整

作者: Trading Framework Team
版本: 12.0
"""

# ==============================================================================
# 【第7模块】市场分层参数 (Market Regime Parameters)
# ==============================================================================

MARKET_REGIME_PARAMS = {
    'lookback_window': 20,           # 回看窗口（期数）
    'volatility_thresholds': {
        'low': 0.02,                 # 低波动阈值
        'high': 0.05                 # 高波动阈值
    },
    'volume_thresholds': {
        'low': 1.2,                  # 低量能阈值
        'high': 2.5                  # 高量能阈值
    },
    'regime_parameters': {
        'Flat': {                    # 平稳行情参数
            'buy_threshold': 60,
            'sell_threshold': 40,
            'position_size_multiplier': 0.5,
            'stop_loss_pct': 0.01,
            'take_profit_pct': 0.02,
            'max_holding_time': 60
        },
        'Up': {                      # 上升行情参数
            'buy_threshold': 30,
            'sell_threshold': 70,
            'position_size_multiplier': 1.5,
            'stop_loss_pct': 0.03,
            'take_profit_pct': 0.05,
            'max_holding_time': 120
        },
        'Down': {                    # 下降行情参数
            'buy_threshold': 70,
            'sell_threshold': 30,
            'position_size_multiplier': 1.5,
            'stop_loss_pct': 0.03,
            'take_profit_pct': 0.05,
            'max_holding_time': 120
        },
        'Chaos': {                   # 失衡行情参数
            'buy_threshold': 80,
            'sell_threshold': 20,
            'position_size_multiplier': 0.2,
            'stop_loss_pct': 0.005,
            'take_profit_pct': 0.01,
            'max_holding_time': 30
        }
    }
}


# ==============================================================================
# 【第8模块】价格风险区间参数 (Price Risk Zone Parameters)
# ==============================================================================

PRICE_RISK_ZONE_PARAMS = {
    # ATR参数
    'atr_period': 14,                # ATR周期
    'atr_multiplier_sl': 2.0,        # 止损ATR倍数
    'atr_multiplier_tp': 1.5,        # 止盈ATR倍数
    
    # Bollinger带参数
    'bollinger_period': 20,          # Bollinger周期
    'bollinger_std_dev': 2,          # 标准差倍数
    
    # Lookback参数
    'lookback_period': 20,           # 回看周期
    'lookback_multiplier': 1.5,      # Lookback ATR倍数
    
    # 止盈方法
    'take_profit_method': 'atr',     # 'atr' / 'fixed' / 'fibonacci'
    'take_profit_levels': {
        'level_1_pct': 2.0,          # 第一级止盈（%）
        'level_2_pct': 5.0,          # 第二级止盈（%）
        'level_3_pct': 10.0          # 第三级止盈（%）
    },
    
    # 风险/收益比要求
    'min_risk_reward_ratio': 1.5,    # 最小R:R比例
    'preferred_risk_reward_ratio': 2.0  # 偏好R:R比例
}


# ==============================================================================
# 【第9模块】合规流动性执行参数 (Compliance Execution Parameters)
# ==============================================================================

COMPLIANCE_EXECUTION_PARAMS = {
    # POV参数
    'pov_participation_rate': 0.05,  # 参与率（5%-15%）
    'pov_lookback_periods': 30,      # 回看周期
    
    # VWAP参数
    'vwap_lookback_periods': 30,     # VWAP回看周期
    
    # TWAP参数
    'twap_execution_time_minutes': 60,  # TWAP执行时间（分钟）
    
    # 冰山单参数
    'iceberg_visible_ratio': 0.10,   # 显示比例（10%）
    'iceberg_refresh_interval_sec': 10,  # 刷新间隔（秒）
    
    # 再平衡参数
    'rebalance_threshold_pct': 5.0,  # 再平衡阈值（%）
    'rebalance_frequency': 'daily',  # 再平衡频率
    
    # 合规限制
    'daily_volume_limit_pct': 0.1,   # 日成交限制（占市场成交%）
    'max_order_size_pct': 0.05,      # 单笔订单最大占比（%）
}


# ==============================================================================
# 【第10模块】头寸对冲参数 (Position Hedging Parameters)
# ==============================================================================

POSITION_HEDGING_PARAMS = {
    # 看跌期权对冲
    'protective_put': {
        'strike_pct_below': 0.95,    # 行权价（目前价格的95%）
        'premium_pct': 0.02          # 期权费（目前价格的2%）
    },
    
    # 领口对冲
    'collar_hedge': {
        'put_strike_pct': 0.95,      # 看跌行权价
        'call_strike_pct': 1.10,     # 看涨行权价
        'put_premium_pct': 0.02,     # 看跌费用
        'call_premium_pct': 0.02     # 看涨收入
    },
    
    # 期货对冲
    'futures_hedge': {
        'hedge_ratio': 1.0,          # 对冲比率（1.0=完全对冲）
        'contract_size': 100         # 期货合约大小
    },
    
    # 配对交易对冲
    'pairs_hedge': {
        'correlation_target': 0.8,   # 目标相关性
        'beta_threshold': 0.2        # Beta偏差容限
    }
}


# ==============================================================================
# 【第11模块】回测与压力测试参数 (Backtest & Stress Test Parameters)
# ==============================================================================

BACKTEST_STRESS_PARAMS = {
    # 回测参数
    'initial_capital': 100000,       # 初始资本
    'commission_rate': 0.001,        # 佣金率（单程）
    'slippage_pct': 0.001,           # 滑点（%）
    'position_size': 0.1,            # 头寸大小（占资本%）
    
    # 压力测试场景
    'stress_scenarios': [
        'NORMAL',                    # 正常行情
        'HIGH_VOLATILITY',           # 高波动
        'FLASH_CRASH',               # 闪崩
        'LIMIT_DOWN',                # 限跌停
        'ILLIQUID',                  # 流动性枯竭
        'CORRELATION_BREAKDOWN'      # 相关性破裂
    ],
    
    # 性能指标参数
    'var_confidence_level': 0.95,    # VaR置信水平
    'sharpe_risk_free_rate': 0.02,   # 无风险收益率
    'calmar_periods': 252            # 卡玛比率周期（年）
}


# ==============================================================================
# 【第12模块】监控与告警参数 (Monitoring & Alert Parameters)
# ==============================================================================

MONITORING_ALERT_PARAMS = {
    # Kill-Switch参数
    'max_drawdown_limit': -0.20,     # 最大回撤限制（-20%）
    'halt_duration_minutes': 5,      # 中止持续时间（分钟）
    'spread_multiplier_threshold': 3.0,  # 点差倍数阈值
    
    # 异常检测参数
    'gap_threshold_pct': 0.05,       # 跳空缺口阈值（5%）
    'limit_move_threshold': 0.098,   # 极限涨跌阈值（9.8%）
    'volume_abnormal_ratio': 0.3,    # 成交量异常比（30%为极低）
    
    # 交易违规检测
    'daily_volume_limit': 0.1,       # 日成交限制
    'slippage_limit': 0.005,         # 滑点限制
    'cancellation_rate_limit': 0.3,  # 撤单率限制
    
    # 持仓风险监控
    'position_concentration_limit': 0.3,  # 单个头寸占比限制（30%）
    'var_limit_pct': 0.02,           # VaR限制（占投资组合%）
    'consecutive_loss_limit': 5,     # 连续亏损笔数限制
    
    # 告警级别
    'alert_levels': {
        'INFO': 1,                   # 信息
        'WARNING': 2,                # 警告
        'CRITICAL': 3,               # 严重
        'KILL_SWITCH': 4             # 紧急停止
    }
}


# ==============================================================================
# 【推荐配置】按风险偏好选择
# ==============================================================================

STRATEGY_PROFILES = {
    'conservative': {                # 保守型
        'description': '风险最小，收益稳定',
        'regime_params': MARKET_REGIME_PARAMS['regime_parameters']['Flat'],
        'max_drawdown': -0.10,       # 最大回撤10%
        'position_size': 0.05,       # 小头寸
        'stop_loss_pct': 0.01,       # 紧止损
        'take_profit_pct': 0.02,     # 保守止盈
        'hedge_strategy': 'protective_put',  # 使用看跌对冲
        'daily_loss_limit': -0.02    # 日亏损限制2%
    },
    
    'balanced': {                    # 平衡型（推荐）
        'description': '风险收益平衡，适合大多数投资者',
        'regime_params': MARKET_REGIME_PARAMS['regime_parameters']['Up'],
        'max_drawdown': -0.15,       # 最大回撤15%
        'position_size': 0.10,       # 中等头寸
        'stop_loss_pct': 0.02,       # 中止损
        'take_profit_pct': 0.05,     # 中等止盈
        'hedge_strategy': 'collar',  # 使用领口对冲
        'daily_loss_limit': -0.05    # 日亏损限制5%
    },
    
    'aggressive': {                  # 激进型
        'description': '追求高收益，承受高风险',
        'regime_params': MARKET_REGIME_PARAMS['regime_parameters']['Up'],
        'max_drawdown': -0.25,       # 最大回撤25%
        'position_size': 0.20,       # 大头寸
        'stop_loss_pct': 0.05,       # 宽止损
        'take_profit_pct': 0.10,     # 激进止盈
        'hedge_strategy': 'futures',  # 使用期货对冲
        'daily_loss_limit': -0.10    # 日亏损限制10%
    }
}


# ==============================================================================
# 【技术指标参数】常见配置
# ==============================================================================

TECHNICAL_INDICATORS = {
    'RSI': {
        'period': 14,                # RSI周期
        'overbought': 70,            # 超买线
        'oversold': 30               # 超卖线
    },
    
    'MACD': {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9
    },
    
    'Bollinger_Bands': {
        'period': 20,
        'std_dev': 2,
        'lower_percentile': 0.2,     # 下轨百分位
        'upper_percentile': 0.8      # 上轨百分位
    },
    
    'ATR': {
        'period': 14,
        'multiplier': 2.0            # ATR倍数
    },
    
    'Moving_Averages': {
        'SMA_short': 20,
        'SMA_long': 50,
        'EMA_short': 12,
        'EMA_long': 26
    }
}


# ==============================================================================
# 【市场时段参数】
# ==============================================================================

TRADING_SESSIONS = {
    'US': {
        'open_time': '09:30',        # 美股开盘
        'close_time': '16:00',       # 美股收盘
        'pre_market': ('04:00', '09:30'),
        'after_hours': ('16:00', '20:00')
    },
    
    'China': {
        'morning_open': '09:30',
        'morning_close': '11:30',
        'afternoon_open': '13:00',
        'afternoon_close': '15:00'
    },
    
    'Europe': {
        'open_time': '08:00',
        'close_time': '16:30'
    }
}


# ==============================================================================
# 【推荐的参数组合】
# ==============================================================================

RECOMMENDED_COMBINATIONS = {
    '高频短线': {
        'description': '1-5分钟K线，频繁交易',
        'time_frame': '1m',
        'regime': 'Up',
        'execution_strategy': 'TWAP',
        'hedge': 'pairs_trade',
        'rebalance_frequency': 'hourly',
        'stop_loss_pct': 0.02,
        'take_profit_pct': 0.03
    },
    
    '中期趋势': {
        'description': '15-60分钟K线，追踪趋势',
        'time_frame': '15m',
        'regime': 'Up/Down',
        'execution_strategy': 'VWAP',
        'hedge': 'collar',
        'rebalance_frequency': 'daily',
        'stop_loss_pct': 0.03,
        'take_profit_pct': 0.05
    },
    
    '长期投资': {
        'description': '日线及以上，长期持仓',
        'time_frame': '1d',
        'regime': 'Flat',
        'execution_strategy': 'POV',
        'hedge': 'protective_put',
        'rebalance_frequency': 'weekly',
        'stop_loss_pct': 0.10,
        'take_profit_pct': 0.20
    }
}


if __name__ == '__main__':
    # 打印推荐配置
    import json
    
    print("="*80)
    print("【交易策略框架 - 参数配置示例】")
    print("="*80)
    
    print("\n【风险偏好配置】")
    for profile_name, profile_config in STRATEGY_PROFILES.items():
        print(f"\n{profile_name.upper()}:")
        print(f"  {profile_config['description']}")
        print(f"  最大回撤: {profile_config['max_drawdown']*100:.1f}%")
        print(f"  头寸大小: {profile_config['position_size']*100:.1f}%")
        print(f"  日亏损限制: {profile_config['daily_loss_limit']*100:.1f}%")
    
    print("\n【推荐参数组合】")
    for combo_name, combo_config in RECOMMENDED_COMBINATIONS.items():
        print(f"\n{combo_name}:")
        print(f"  {combo_config['description']}")
        print(f"  时间周期: {combo_config['time_frame']}")
        print(f"  执行策略: {combo_config['execution_strategy']}")
        print(f"  对冲方式: {combo_config['hedge']}")
    
    print("\n" + "="*80)
    print("✅ 参数配置完成！")
    print("="*80)
