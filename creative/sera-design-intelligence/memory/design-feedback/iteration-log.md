# Design Iteration Log

> 设计迭代日志 — 记录每次设计优化与决策依据

## 格式

每次迭代记录：

```yaml
iteration: <编号>
date: <日期>
product: <产品>
trigger: <触发原因 — 数据反馈/用户反馈/设计评审>
change: <变更描述>
rationale: <决策依据>
result: <结果>
new_rule: <是否生成新设计规则>
```

## 迭代历史

| 迭代 | 日期 | 产品 | 变更 | 结果 | 新规则 |
|---|---|---|---|---|---|
| 001 | 2026-08-15 | HTX OTC Desk | CTA 移至 Hero 区域右侧固定 | 转化率 +50%，点击率 +46% | 是 |
| 002 | 2026-08-16 | HTX OTC Progress Hub | 优化进度指示器，增加状态标签颜色区分 | 任务完成时间 -15.6% | 是 |
| 003 | 2026-08-20 | HTX OTC Desk | 在 Hero 区域增加安全认证徽章和监管信息 | 待测量 | 待定 |

## 反馈 → 规则生成工作流

每次迭代的数据通过以下管道自动生成设计规则：

```
用户反馈/实验数据 → 迭代记录 → 规则引擎 → design-rules.json
```

1. **触发**: 数据反馈、用户反馈或设计评审触发迭代
2. **变更**: 实施设计变更并记录 rationale
3. **测量**: 通过 ConversionTracker 记录转化指标变化
4. **规则生成**: 验证有效的变更通过 DesignRulesEngine 生成设计规则
5. **应用**: 新规则自动关联到对应产品，指导后续设计决策

## 迭代记录

### Iteration 001

```yaml
iteration: 001
date: 2026-08-15
product: HTX OTC Desk
trigger: 数据反馈 — CTA 转化率低于行业基准
change: 将 CTA 从折叠线以下移至 Hero 区域右侧固定
rationale: 金融产品用户需要明确的行动引导，首屏可见 CTA 可提升 40%+ 转化率
result: 转化率 +50%，点击率 +46%
new_rule: true
```

**New Rule Generated:** 金融产品首屏必须包含可见 CTA，CTA 应在 Hero 区域内而非折叠线以下。

---

### Iteration 002

```yaml
iteration: 002
date: 2026-08-16
product: HTX OTC Progress Hub
trigger: 用户反馈 — 操作流程不清晰
change: 优化进度指示器，增加状态标签颜色区分
rationale: 用户需要快速理解当前状态和下一步操作
result: 任务完成时间 -15.6%
new_rule: true
```

**New Rule Generated:** Dashboard 进度指示器应使用语义颜色区分状态（进行中=蓝色，完成=绿色，失败=红色）。

---

### Iteration 003

```yaml
iteration: 003
date: 2026-08-20
product: HTX OTC Desk
trigger: 设计评审 — 信任信号不足
change: 在 Hero 区域增加安全认证徽章和监管信息
rationale: 金融产品用户首先评估安全性，再评估产品功能
result: 待测量
new_rule: pending
```

## 规则生成

每次迭代若产生新设计规则，应同步更新到 `rules-engine/design-rules.json`。