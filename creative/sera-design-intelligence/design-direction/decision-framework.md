# Design Decision Framework

> 设计决策框架 — Design Director Layer 的核心决策系统
> 版本：V3.3
> 定位：从"主观推荐"升级为"量化决策"

## 概述

Design Decision Framework 是一个量化的设计决策系统，通过多维度的产品属性分析、风格匹配评分、组合优化和置信度计算，将设计方向从"直觉判断"升级为"数据驱动决策"。

## 1. 决策矩阵 (Decision Matrix)

### 产品属性 × 风格维度

决策矩阵将产品属性映射到风格维度，每个维度给出权重，最终计算综合匹配度。

| 产品属性 | 权重 | 风格维度 | 说明 |
|---------|------|---------|------|
| Industry (行业) | 40% | 行业匹配度 | 产品所在的行业是否与风格推荐的行业匹配 |
| Audience (受众) | 25% | 受众匹配度 | 目标用户群体是否与风格的目标受众一致 |
| Goal (目标) | 20% | 目标匹配度 | 产品的商业目标是否与风格的转化目标一致 |
| Keywords (关键词) | 15% | 语义匹配度 | 品牌关键词与风格关键词的语义重叠度 |

### 风格维度定义

每种风格包含以下维度评分（1-10）：

| 维度 | 说明 | 示例 |
|------|------|------|
| trust_level | 信任感/专业度 | FinTech Premium: 10, AI Future: 7 |
| technology_level | 科技感/前沿感 | AI Future: 10, Content Platform: 6 |
| luxury_level | 奢华感/高端感 | FinTech Premium: 7, SaaS Landing: 5 |
| playfulness_level | 趣味性/亲和力 | AI Future: 6, Operations Dashboard: 1 |
| minimalism_level | 极简程度 | AI Future: 9, FinTech Premium: 8 |

## 2. 评分算法 (Scoring Algorithm)

### 基础匹配度计算

```
Total Score = Σ(attribute_weight × attribute_score)

其中:
- attribute_weight 是产品属性的权重（见决策矩阵）
- attribute_score 是风格在该属性上的匹配得分
```

### 详细评分规则

#### 行业匹配 (权重 40%)
- 风格.industry == 产品.industry: +40 分
- 产品.industry in 风格.recommended_for: +20 分
- 不匹配: +0 分

#### 受众匹配 (权重 25%)
- 风格.audience == 产品.audience: +25 分
- 产品.audience in 风格.target_user: +15 分
- 不匹配: +0 分

#### 目标匹配 (权重 20%)
- 产品.goal in 风格.conversion_goal 或反之: +20 分
- 部分匹配: +10 分
- 不匹配: +0 分

#### 关键词匹配 (权重 15%)
- 计算品牌关键词与风格关键词的交集
- 每匹配一个关键词: +5 分
- 上限: 15 分

### 归一化

```
normalized_score = raw_score / max_possible_score
```

最大可能分数 = 40 + 25 + 20 + 15 = 100 分

## 3. 多风格组合优化 (Multi-Style Combination)

### 组合原则

1. **主次分明**: 一个主风格（权重 >= 50%），2-3 个辅助风格
2. **互补不冲突**: 辅助风格补充主风格的不足，而非重复
3. **风格距离**: 建议组合的风格之间不宜过于相似（避免冗余）或过于不同（避免割裂）

### 组合算法

```
1. 对所有风格按匹配度排序
2. 取 Top N 风格作为候选
3. 主风格 = 匹配度最高的风格
4. 辅助风格选择:
   - 从剩余风格中选择匹配度高的
   - 检查与主风格的相关性（不选择过于相似的）
   - 优先选择能补充主风格薄弱维度的风格
5. 权重归一化: 确保所有权重之和 = 1
```

### 组合示例

| 产品 | 主风格 | 权重 | 辅助风格1 | 权重 | 辅助风格2 | 权重 |
|------|--------|------|-----------|------|-----------|------|
| AI 金融助手 | AI Future | 50% | FinTech Premium | 30% | SaaS Landing | 20% |
| 企业级 SaaS | SaaS Landing | 55% | FinTech Premium | 25% | Operations Dashboard | 20% |
| 内容平台 | Content Platform | 60% | SaaS Landing | 25% | AI Future | 15% |

## 4. 置信度评分 (Confidence Scoring)

### 置信度等级

| 等级 | 条件 | 含义 |
|------|------|------|
| High | 主风格匹配度 > 50% | 推荐可靠，可直接执行 |
| Medium | 主风格匹配度 30-50% | 推荐需人工复核 |
| Low | 主风格匹配度 < 30% | 推荐仅供参考，需进一步分析 |

### 置信度影响因素

- **数据质量**: 输入的产品画像越完整，置信度越高
- **风格覆盖度**: 已有风格库是否能覆盖该产品类型
- **匹配差距**: Top1 与 Top2 的差距越大，置信度越高
- **历史验证**: 该风格组合是否在类似产品上验证过

### 置信度提升建议

- 补充更多产品属性（如产品阶段、目标市场、品牌调性）
- 提供竞品参考案例
- 提供明确的业务目标（如转化率提升、品牌认知）

## 5. 兜底策略 (Fallback Strategy)

### 当无良好匹配时

如果所有风格的匹配度都低于 30%，系统执行兜底策略：

1. **行业扩展**: 放宽行业匹配限制，寻找跨行业参考
2. **受众导向**: 以受众匹配为优先，忽略行业属性
3. **混合推荐**: 综合 Top 3 风格的共性特征，生成"合成风格"
4. **人工介入**: 输出低置信度标记，建议设计总监人工决策

### 兜底输出示例

```yaml
fallback_triggered: true
reason: "无风格匹配度超过 30%"
recommendation:
  approach: "行业扩展 + 受众导向"
  candidate_styles:
    - style: "SaaS Landing"
      match_reason: "受众类型匹配，行业可扩展"
    - style: "AI Future"
      match_reason: "科技感需求匹配，视觉语言可借鉴"
  synthetic_style:
    base: "SaaS Landing"
    adjustments:
      - "降低正式感，增加亲和力"
      - "采用更柔和的色彩方案"
      - "增加动效丰富度"
  confidence: "low"
  action: "建议 Design Director 人工决策"
```

## 6. 示例

### 示例 1: FinTech 平台

**产品画像**:
```yaml
name: "HTX OTC Desk"
industry: "finance"
audience: "institutional"
goal: "trust & conversion"
brand_keywords: ["professional", "premium", "secure"]
```

**匹配结果**:
| 风格 | 行业(40) | 受众(25) | 目标(20) | 关键词(15) | 总分 |
|------|----------|----------|----------|------------|------|
| FinTech Premium | 40 | 25 | 20 | 15 | 100 |
| SaaS Landing | 20 | 15 | 20 | 10 | 65 |
| AI Future | 20 | 15 | 20 | 5 | 60 |
| Operations Dashboard | 0 | 15 | 0 | 5 | 20 |
| Content Platform | 0 | 0 | 0 | 5 | 5 |

**组合**: 100% FinTech Premium（单一风格已完美匹配）
**置信度**: High (100%)

### 示例 2: AI 产品

**产品画像**:
```yaml
name: "牛牛 AI"
industry: "ai"
audience: "developer"
goal: "free trial signup"
brand_keywords: ["intelligent", "minimal", "innovative"]
```

**匹配结果**:
| 风格 | 行业(40) | 受众(25) | 目标(20) | 关键词(15) | 总分 |
|------|----------|----------|----------|------------|------|
| AI Future | 40 | 25 | 20 | 15 | 100 |
| SaaS Landing | 20 | 15 | 20 | 10 | 65 |
| FinTech Premium | 20 | 0 | 20 | 5 | 45 |
| Content Platform | 0 | 0 | 0 | 5 | 5 |
| Operations Dashboard | 0 | 0 | 0 | 0 | 0 |

**组合**: 65% AI Future + 35% SaaS Landing
**置信度**: High (100%)

### 示例 3: SaaS 产品

**产品画像**:
```yaml
name: "Sera Design Intelligence"
industry: "saas"
audience: "decision-maker"
goal: "free trial signup"
brand_keywords: ["professional", "modern", "innovative"]
```

**匹配结果**:
| 风格 | 行业(40) | 受众(25) | 目标(20) | 关键词(15) | 总分 |
|------|----------|----------|----------|------------|------|
| SaaS Landing | 40 | 25 | 20 | 15 | 100 |
| AI Future | 20 | 15 | 20 | 10 | 65 |
| FinTech Premium | 20 | 15 | 20 | 10 | 65 |
| Content Platform | 0 | 0 | 0 | 5 | 5 |
| Operations Dashboard | 0 | 0 | 0 | 0 | 0 |

**组合**: 55% SaaS Landing + 25% AI Future + 20% FinTech Premium
**置信度**: High (100%)
**说明**: 主风格 SaaS Landing 提供专业感，AI Future 补充科技感，FinTech Premium 补充可信赖感

## 7. 与 Style Router 的关系

```
Style Router (风格路由)
    │
    ├── 基于规则匹配：if product == X then style == Y
    ├── 输出：简单风格推荐列表
    ├── 适合：快速原型、标准场景
    │
    ▼
Decision Framework (决策框架)
    │
    ├── 基于量化评分：多维权重计算
    ├── 输出：完整的设计方向决策（含置信度、风险、依据）
    ├── 适合：正式项目、品牌级决策
    ├── 支持：多风格组合、版本对比、策略回溯
    │
    ▼
Design Director Agent (设计总监)
    │
    ├── 接收 Decision Framework 的输出
    ├── 结合 Design Memory 的历史反馈
    ├── 参考 Design Benchmark 的案例评分
    └── 输出最终 Design Direction Schema
```

## 8. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-08-21 | 初始版本，V3.3 Design Director Layer 核心决策框架 |