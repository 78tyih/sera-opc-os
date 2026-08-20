# Sera CEO Agent — Priority Engine

> 版本：1.2.0
> 用途：项目优先级排序与资源分配引擎

---

## 优先级评分模型

```
Priority Score = 
  Business Value × 0.30 +
  Market Opportunity × 0.20 +
  Competition × 0.15 +
  Resource Fit × 0.20 +
  Strategic Alignment × 0.15
```

## 活跃项目容量

| 类型 | 最大并行数 | 说明 |
|------|-----------|------|
| **P0** 紧急项目 | 1 | CEO 直接关注，需立即资源 |
| **P1** 核心项目 | 2 | 持续投入，常规进度 |
| **P2** 探索项目 | 3 | 低资源消耗，验证模式 |
| **P3** 待定项目 | 不限 | HOLD 状态，等待触发 |

## 资源分配原则

```
Agent 分配模型：
  - 每个 P0 项目占用 1 个主 Agent + 2 个支持 Agent
  - 每个 P1 项目占用 1 个主 Agent + 1 个支持 Agent
  - 每个 P2 项目占用 0.5 个 Agent（共享）

Skill 分配模型：
  - 核心 Skill 不可抢占（sera-project-profile, sera-design-studio）
  - 支持 Skill 可共享（sera-market-research, sera-copywriting）
```

## 当前项目优先级排序

| 项目 | 优先级 | 状态 | 分数 | 负责 Agent | 下一里程碑 |
|------|--------|------|------|-----------|-----------|
| 牛牛 AI | P1 | 规划中 | 82 | product-agent | 产品定义完成 |
| TradeSpan | P1 | 规划中 | 78 | product-agent | 产品定义完成 |
| PropFirm TV | P0 | 活跃 | 91 | propfirm-agent | 视频生产 |
| HTX OTC | P1 | 活跃 | 76 | otc-agent | 落地页优化 |
| Deltapex | P1 | 活跃 | 72 | propfirm-agent | 品牌升级 |

## 优先级调整规则

1. **每周自动重排** — 基于进展和阻塞情况
2. **新项目插入** — 只有 P0 或 P1 可抢占现有项目
3. **项目停滞 14 天** — 自动降级为 P2
4. **项目停滞 30 天** — 自动转为 HOLD
5. **外部信号触发** — 市场变化、客户需求、竞品动作可提升优先级

## 阻塞处理

| 阻塞类型 | 处理方式 | 超时策略 |
|----------|---------|---------|
| 资源不足 | 降级 P2/P3 项目释放资源 | 3 天 |
| 依赖阻塞 | 并行处理其他任务 | 7 天 |
| 决策阻塞 | 升级到 CEO Agent | 2 天 |
| 外部阻塞 | 转为 HOLD 等待 | 14 天 |