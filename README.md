# 股票交易策略评估框架

## 项目概述

这是一个**合规取向的股票交易策略框架**，核心目标是：
- **风险控制** - 严格的头寸管理、止损、回撤限制
- **流动性管理** - 评估市场深度、维持合理价差
- **合规执行** - 透明的信号生成、可审计的交易记录

## 框架架构

```
stock_strategy_framework/
├── 1_data_fetcher.py           # 数据获取与预处理
├── 2_anomaly_detector.py       # 异常波动检测 & 市场结构分析
├── 3_liquidity_manager.py      # 流动性管理 & 价差管理
├── 4_risk_manager.py           # 风险控制 & 头寸管理
├── 5_trading_strategy.py       # 交易信号生成 & 回测
├── 6_visualizer.py             # 结果可视化
├── main.py                     # 主程序 & 完整流程
└── requirements.txt            # 依赖包
```

## 功能模块详解

### 1️⃣ 数据获取模块 (`1_data_fetcher.py`)

**功能：**
- 从Yahoo Finance获取历史K线数据
- 支持多时间间隔（1分钟、5分钟、1小时、1天）
- 数据预处理与验证
- 生成模拟数据用于演示

**主要类：**
- `StockDataFetcher` - 数据获取

**使用示例：**
```python
from data_fetcher import StockDataFetcher

# 实时获取数据
fetcher = StockDataFetcher('AAPL', interval='1h')
data = fetcher.fetch_data()

# 或生成模拟数据
fetcher.generate_sample_data(days=180)
stats = fetcher.get_summary_stats()
```

### 2️⃣ 异常波动检测模块 (`2_anomaly_detector.py`)

**功能：**
- 基于Z-score的价格异常检测
- 成交量异常识别
- 波动率聚集检测
- 价差异常预警
- 散户 vs 机构行为识别

**核心指标：**
- `Returns_ZScore` - 收益率Z分数
- `Volume_Anomaly` - 成交量异常标志
- `High_Volatility` - 高波动率标志
- `Institutional_Ratio` - 机构主导比例

**使用示例：**
```python
from anomaly_detector import AnomalyDetector, MarketBehaviorAnalyzer

detector = AnomalyDetector(data, window=20)
detector.detect_all_anomalies()

analyzer = MarketBehaviorAnalyzer(detector.get_data())
analyzer.get_market_dominance()
```

### 3️⃣ 流动性管理模块 (`3_liquidity_manager.py`)

**功能：**
- 评估市场深度和流动性
- 计算交易成本（滑点、市场冲击）
- 维持合理的买卖价差
- 识别最优交易时间
- 价差合规监控

**核心指标：**
- `Market_Depth_Score` - 市场深度评分 (0-100)
- `Spread_Risk_Score` - 价差风险评分
- `Fair_Spread` - 合理价差
- `Optimal_Trade_Time` - 最优交易时间标志
- `Trading_Cost_Ratio` - 交易成本比例

**使用示例：**
```python
from liquidity_manager import LiquidityManager, SpreadManager

liq_mgr = LiquidityManager(data, position_size=1000)
liq_mgr.assess_market_depth()
liq_summary = liq_mgr.get_liquidity_summary()

spread_mgr = SpreadManager(data, target_spread=0.001)
spread_mgr.calculate_fair_spread()
spread_mgr.monitor_spread_compliance()
```

### 4️⃣ 风险管理模块 (`4_risk_manager.py`)

**功能：**
- 投资组合价值跟踪
- 回撤计算与限制
- 在险价值 (VaR) 计算
- 条件风险价值 (CVaR) 计算
- 止损价格设置
- 基于风险的头寸规模调整

**核心指标：**
- `Portfolio_Value` - 投资组合价值
- `Drawdown` - 当前回撤
- `VaR_Amount` - 95%置信度下的风险金额
- `ES_Amount` - 预期缺口（尾部风险）
- `Stop_Loss_Price` - 止损价
- `Adjusted_Position_Size` - 调整后头寸规模

**使用示例：**
```python
from risk_manager import RiskManager

risk_mgr = RiskManager(
    data,
    initial_capital=100000,
    position_size=1000,
    max_drawdown=0.1
)
risk_summary = risk_mgr.get_risk_summary(entry_price=100)
```

### 5️⃣ 交易策略模块 (`5_trading_strategy.py`)

**功能：**
- 综合信号生成（买/卖/持仓）
- 完整的策略回测框架
- 交易记录跟踪
- 性能指标计算

**买信号条件：**
- 异常波动触底（Z-score < -1.5）
- 流动性充足
- 价差合理
- 风险在可控范围

**卖信号条件：**
- 异常波动触顶（Z-score > 1.5）
- 止损被触发
- 获利回吐（5%以上）
- 流动性恶化

**性能指标：**
- 总收益率
- 年化收益率
- 夏普比率
- 最大回撤
- 胜率
- 盈利因子

**使用示例：**
```python
from trading_strategy import TradingStrategy

strategy = TradingStrategy(data, anomaly_data, liquidity_data, risk_data)
trades = strategy.backtest_strategy(
    initial_capital=100000,
    position_size=1000,
    buy_threshold=50,
    sell_threshold=30
)
performance = strategy.calculate_performance_metrics()
```

### 6️⃣ 可视化模块 (`6_visualizer.py`)

**功能：**
- 价格与信号图表
- 权益曲线与回撤曲线
- 异常波动可视化
- 流动性评分展示
- 价差分析图
- 市场主导权分析
- 综合仪表板

**使用示例：**
```python
from visualizer import StrategyVisualizer

viz = StrategyVisualizer(strategy_data, trades_df)
viz.create_detailed_report('output_dir')
viz.create_comprehensive_dashboard('dashboard.png')
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行完整分析
```bash
python main.py
```

### 3. 输出内容
- **交易记录**: `trade_records.csv`
- **执行摘要**: `strategy_analysis_report/executive_summary.txt`
- **可视化报告**: `strategy_analysis_report/` 目录下的多张图表
  - `1_price_signals.png` - 价格和交易信号
  - `2_equity_drawdown.png` - 权益曲线和回撤
  - `3_anomalies.png` - 异常波动检测
  - `4_signal_strength.png` - 信号强度分析
  - `5_liquidity_spread.png` - 流动性和价差
  - `6_risk_metrics.png` - 风险指标
  - `7_market_dominance.png` - 市场主导权
  - `8_pnl_distribution.png` - 盈亏分布
  - `9_comprehensive_dashboard.png` - 综合仪表板

## 数据流示意图

```
原始数据
   ↓
[数据获取] → 清洗、验证、格式化
   ↓
多个分析并行处理
   ├→ [异常检测] → Price/Volume异常、市场结构
   ├→ [流动性管理] → 深度评分、价差评估
   ├→ [风险管理] → VaR、回撤、止损
   └→ [市场分析] → 散户vs机构
   ↓
[交易策略] → 综合信号 → 买/卖/持仓
   ↓
[回测执行] → 模拟交易
   ↓
[性能评估] → 夏普比率、收益率、回撤
   ↓
[合规检查] → 风险、流动性、频率检查
   ↓
[可视化报告] → 图表、数据、建议
```

## 关键指标解释

### 异常波动
- **Z-Score > 2.5**: 极端波动（99%置信度）
- **Z-Score 2.0-2.5**: 显著波动（95%置信度）
- **Z-Score < -1.5**: 超卖信号

### 流动性评分 (0-100)
- **> 70**: 高流动性 - 最优交易时间
- **30-70**: 中等流动性 - 可交易
- **< 30**: 低流动性 - 需谨慎

### 价差 (基点, BP)
- **< 1 BP**: 非常紧
- **1-5 BP**: 合理
- **> 5 BP**: 过宽

### 市场主导权 (%)
- **> 60%**: 机构主导 - 大额交易、系统性
- **40-60%**: 平衡 - 双向力量
- **< 40%**: 散户主导 - 情绪化、高波动

### 夏普比率
- **> 1.0**: 优秀
- **0.5-1.0**: 良好
- **0-0.5**: 一般
- **< 0**: 亏损

## 回测参数说明

| 参数 | 说明 | 推荐值 |
|-----|------|--------|
| `initial_capital` | 初始资本 | 100,000 |
| `position_size` | 单笔头寸 | 1,000 股 |
| `max_drawdown` | 最大回撤限制 | 10% |
| `buy_threshold` | 买信号强度阈值 | 50 |
| `sell_threshold` | 卖信号强度阈值 | 30 |
| `window` | 滚动窗口大小 | 20 |

## 实际应用建议

### 1. 数据选择
```python
# 使用真实数据
fetcher = StockDataFetcher('AAPL', interval='1h')
data = fetcher.fetch_data()

# 或中国股票
fetcher = StockDataFetcher('000858.SZ', interval='1h')  # 五粮液
```

### 2. 参数调整
- **保守策略**: `max_drawdown=0.05`, `buy_threshold=70`
- **激进策略**: `max_drawdown=0.2`, `buy_threshold=30`
- **平衡策略**: `max_drawdown=0.1`, `buy_threshold=50`

### 3. 监控指标
重点关注：
- 最大回撤是否超限
- 交易成本是否过高
- 胜率是否满足要求
- 流动性是否充足

## 合规框架核心要点

✅ **已实现的合规控制：**
1. ✓ 严格的风险限制（回撤、VaR、CVaR）
2. ✓ 流动性检查（价差、深度、交易成本）
3. ✓ 透明的信号生成（量化规则）
4. ✓ 完整的审计跟踪（交易记录、时间戳）
5. ✓ 动态头寸管理（基于风险调整）
6. ✓ 定期压力测试（回撤监控）

⚠️ **使用注意：**
- 本框架仅用于教育和研究
- 真实交易需要额外的合规审查
- 过去表现不代表未来结果
- 请自行承担投资风险

## 文件说明

| 文件 | 功能 |
|-----|------|
| `requirements.txt` | Python 依赖包 |
| `1_data_fetcher.py` | 数据获取 |
| `2_anomaly_detector.py` | 异常检测 |
| `3_liquidity_manager.py` | 流动性管理 |
| `4_risk_manager.py` | 风险控制 |
| `5_trading_strategy.py` | 策略回测 |
| `6_visualizer.py` | 可视化展示 |
| `main.py` | 主程序入口 |
| `README.md` | 项目文档（本文件） |

## 常见问题

**Q: 如何使用真实数据？**
A: 在 `data_fetcher.py` 中，使用 `fetcher.fetch_data()` 替代 `generate_sample_data()`。需要网络连接。

**Q: 如何自定义交易信号？**
A: 编辑 `trading_strategy.py` 中的 `generate_buy_signals()` 和 `generate_sell_signals()` 方法。

**Q: 如何改变回测周期？**
A: 在 `main.py` 中的 `ComplianceFramework(days=90)` 中修改天数。

**Q: 如何优化策略参数？**
A: 使用网格搜索或贝叶斯优化，逐一尝试不同的阈值组合。

## 联系与支持

如有问题，请查看各模块中的详细注释和示例代码。

---

**最后更新**: 2025年11月10日
**版本**: 1.0
**状态**: 生产就绪 (Production Ready)
