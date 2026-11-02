# QuantAgent 多智能体量化研究平台

在西华大学与电子科技大学联合项目中担任开发成员，工作重点是研究看板、智能体决策层协作与本地模型接入。项目用于量化研究、回测与模拟交易。

## 我的工作

- 基于 Next.js 与 shadcn/ui 重构总览看板和研究台，组合实时 K 线、VWAP 指标、因子快照与新闻宏观信息，支持联动分析及证据链追溯。
- 参与重构 TradingAgents 决策层，组织技术、新闻、宏观、风控四角色并行分析与多空辩论。
- 为数据平台尚未就绪时的页面展示设计 API 兼容策略，打通 Ollama 本地模型调用链路。
- 设计滑动窗口预测实验，获取新闻与宏观数据，使用 DeepSeek 对 BTC、ETH、SOL 开展跨资产回测。

## 实验结果的适用范围

项目经历记录的实验中，“新闻 + 宏观”配置预测准确率为 41.38%，纯 K 线配置为 33%，相差 8.38 个百分点。这个结果仅对应当时的实验配置，不能代表投资收益或其他时间段的表现。

当前个人主页未附原始实验集、时间区间、样本量与完整复现实验，因此首页主要展示角色协作和工程实现，未把该数值作为通用性能结论。

## 公开实现入口

- [QuantAgent 仓库](https://github.com/helililili/QuantAgent)：本人账号下的 fork，README 说明了项目整体能力。
- [前端看板](https://github.com/helililili/QuantAgent/blob/main/frontend/app/dashboard/page.tsx)
- [Ollama 模型适配](https://github.com/helililili/QuantAgent/blob/main/backend/app/services/llm/ollama_provider.py)
- [回测服务](https://github.com/helililili/QuantAgent/tree/main/backend/app/services/backtester)

个人工作内容依据项目经历整理；公开仓库用于了解实现结构，不将整个团队项目归为个人独立成果。

[返回主页](../README.md)
