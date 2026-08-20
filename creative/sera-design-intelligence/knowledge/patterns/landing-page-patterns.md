# UI Pattern: Landing Page Architecture

> 知识类型：ui-pattern
> 版本：1.0.0
> 适用：产品 Landing Page / 发布页 / 官网

---

## 模式概述

Landing Page 是产品面向用户的第一张脸。设计目标是：在有限时间内让用户完成理解→信任→转化。

---

## 标准结构

```
01 Hero（首屏：价值主张 + CTA + 信任信号）
    ↓
02 Problem / Solution（痛点 + 解决方案）
    ↓
03 Feature（核心功能展示）
    ↓
04 How It Works（工作原理 / 流程）
    ↓
05 Trust / Social Proof（信任信号）
    ↓
06 FAQ（常见问题拦截）
    ↓
07 CTA（最终转化）
    ↓
Footer（风险提示 + 版权）
```

---

## 模式变体

### 1. 金融产品 Landing Page

```
顺序：
01 Hero（双入口 CTA + KYC 信任）
02 服务介绍（3 列卡片）
03 合规说明（信任强化）
04 FAQ
05 CTA（TG 联系）

特点：
- 信任前置，合规可见
- 双入口降低决策负担
- 营销内容克制
```

### 2. SaaS Landing Page

```
顺序：
01 Hero（产品截图 + 免费试用）
02 核心功能（3 列 Feature）
03 技术优势（数据 / 性能）
04 客户案例 / Logo 墙
05 定价
06 FAQ
07 CTA

特点：
- 产品 Demo 直观
- 免费试用降低门槛
- 客户案例建立信任
```

### 3. AI 产品 Landing Page

```
顺序：
01 Hero（AI 能力 + Demo 区域）
02 使用场景（具体案例）
03 技术可信（准确率 + 安全）
04 定价
05 CTA

特点：
- Demo 首屏可见
- 能力边界清晰
- 使用场景具体
```

---

## Section 设计规则

### Section 头部标准

```
sec-tag（12.5px 700 uppercase 2px spacing brand）
    ↓ 14px gap
h2（44-64px 800 -1.2px spacing）
    ↓ 10px gap
p（15px 400 text2）
```

### 内容区

```
- 3 列 grid：功能 / 服务卡片
- 2 列 grid：FAQ / 合规
- 1 列：移动端自动降级
```

---

## 转化路径嵌入

```
每个 Section 都是转化漏斗的一环：

Hero      → 理解业务 → 点击 CTA
Feature   → 理解价值 → 进一步了解
Trust     → 建立信任 → 降低顾虑
FAQ       → 解决问题 → 消除障碍
CTA       → 最终行动 → 转化
```

---

## 检查清单

- [ ] 首屏是否回答了"这是什么"？
- [ ] 信息是否按"理解→信任→转化"顺序排列？
- [ ] 每个 Section 是否有"下一个动作"引导？
- [ ] 是否有 FAQ 拦截常见问题？
- [ ] 移动端是否完整可用？
- [ ] 加载性能是否 < 3s？