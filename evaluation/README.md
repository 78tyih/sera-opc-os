# Sera OPC OS — Evaluation 评估体系

评估每个 Agent / 每个模型的实际表现，回答「哪个 Agent 做得好」「哪个模型驱动效果更好」。

## 结构

```
evaluation/
├── README.md             # 本文件
└── agent-score.yaml      # 汇总评分（按 Agent × 模型）
```

每个 Agent 目录内的 `evaluation.yaml` 定义其专属评估维度与权重（维度见下）。

## 评估流程

1. 任务完成后，按目标 Agent 的 `evaluation.yaml` 维度逐项打分（1-5）
2. 加权汇总 → 写入 `agent-score.yaml`
3. 同一任务用不同模型跑 → 对比模型分（如 DeepSeek vs GPT 驱动 propfirm-agent）
4. 定期回顾 → 优化 Agent 组合 / 模型路由

## 各 Agent 评估维度

| Agent | 维度（权重） |
|---|---|
| propfirm-agent | research_accuracy (0.4) · competitive_insight (0.3) · output_completeness (0.3) |
| otc-agent | response_quality (0.3) · risk_accuracy (0.3) · deal_conversion (0.2) · followup_timeliness (0.2) |
| trading-agent | analysis_accuracy (0.4) · research_depth (0.3) · report_quality (0.3) |
| video-agent | script_quality (0.25) · visual_consistency (0.25) · rendering_success (0.25) · user_approval (0.25) |
| design-agent | visual_hierarchy (0.35) · brand_consistency (0.35) · deliverable_quality (0.3) |

## 评分标准（1-5）

| 分 | 含义 |
|---|---|
| 5 | 超出预期，可直接交付 |
| 4 | 达标，少量微调 |
| 3 | 基本可用，需返工 |
| 2 | 方向对但质量差 |
| 1 | 不可用 |
