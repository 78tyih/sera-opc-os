# Sera FinTech Visual Language V1.0

> Design Intelligence Document
> 版本：1.0.0 · 2026-08-21
> 来源：HTX OTC Landing (v1) + HTX OTC Progress Hub (v1)
> 适用范围：金融科技 / 高价值服务 / AI 产品 / SaaS 平台

---

## 01. Design Philosophy

### 核心信念

```
Trust（信任）
+
Technology（科技）
+
Premium（质感）
+
Conversion（转化）
```

### 设计目标

不是炫技。而是让用户 **5 秒内理解**：

- **你是谁** — 品牌定位一目了然
- **你解决什么问题** — 价值主张清晰明确
- **为什么相信你** — 信任信号可见可信

### 设计原则

| 原则 | 含义 |
|---|---|
| **Information First** | 信息层级优于视觉装饰，内容即设计 |
| **Trust Before Action** | 转化前先建立信任，信任信号前置 |
| **Consistency Over Novelty** | 一致性优于新奇感，复用优于创造 |
| **Subtle Motion** | 动效克制、统一、有目的性 |
| **Conversion Oriented** | 每个板块都有明确的客户动作 |
| **Dark Mode Ready** | 深色模式不是取反，是独立设计 |

### 语气

```
专业 · 克制 · 清晰 · 可信
不 aggressive · 不炫耀 · 不制造焦虑
```

---

## 02. Visual Identity

### 品牌色板

```
#0052FF  ─── 主品牌色（交互、按钮、链接）
#003ECC  ─── 品牌深色（hover）
#EEF4FF  ─── 品牌浅色（选中态、标签）
#3E8EFF  ─── 深色模式品牌色（+6 亮度）
```

### 中性色板

```
#FFFFFF  ─── 亮色背景
#F6F8FB  ─── 次级背景
#E8ECF2  ─── 边框线
#14181F  ─── 主文字
#5A6272  ─── 辅助文字
#8A93A6  ─── 弱化文字
```

### 语义色板

```
#E5484D  ─── 错误 / 必填
#16A34A  ─── 成功 / 完成
#FFF8EC  ─── 警告背景
#F5E3B8  ─── 警告边框
#8A6D1A  ─── 警告文字
```

### 深色模式映射

```
#060708  ─── 深色背景
#EDEFF3  ─── 深色主文字
#A2A8B3  ─── 深色辅助文字
#797F8B  ─── 深色弱化文字
rgba(255,255,255,.1)  ─── 深色边框
rgba(22,24,29,.6)  ─── 深色卡片背景
```

### 色彩比例

```
黑色/深色 65%  │  白色 20%  │  蓝色 10%  │  语义色 5%
```

### 禁止规则

- ❌ 大面积渐变
- ❌ 彩虹色
- ❌ 紫色和绿色作为主色
- ❌ 霓虹发光堆叠
- ❌ 复杂 3D 效果

---

## 03. Typography

### 字体栈

```css
font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue",
  "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
```

### 字号层级

| 层级 | 桌面 | 移动端 | 字重 | 行高 | 字距 |
|---|---|---|---|---|---|
| **Hero 标题** | clamp(44px, 6vw, 64px) | clamp(29px, 8.4vw, 38px) | 800 | 1.14 | -1.5px |
| **板块标题** | clamp(44px, 6vw, 64px) | clamp(27px, 7.4vw, 34px) | 800 | 1.14 | -1.2px |
| **卡片标题** | 17-19px | 15-16.5px | 700 | 1.4 | — |
| **正文** | 14-15px | 13-13.5px | 400 | 1.65 | — |
| **辅助文字** | 13-13.5px | 12-12.5px | 400 | 1.55 | — |
| **标签** | 12.5px | 11.5px | 700 | 1.2 | 2px |
| **数据强调** | 13.5px | 12.5px | 700 | 1 | 0.5px |
| **风险提示** | 12px | 11px | 400 | 1.8 | — |

### 排版规则

- **对比驱动**：主标题 64px → 卡片标题 19px，视觉跳跃明显
- 标签全部 uppercase + 2px letter-spacing
- 段落最大宽度 660px（保持可读性）
- 行高 1.65 舒适阅读

---

## 04. Layout System

### 容器规范

```
内容最大宽度: 1120px
导航栏最大宽度: 1072px
水平 padding: 24px（桌面）→ 16px（移动）
板块间距: 84px（桌面）→ 52px（移动）
```

### 页面结构模式

#### Hero Pattern（首屏模式）
```
Large Statement（大标题 64px 800）
        ↓
Supporting Description（副标题 17px）
        ↓
CTA（双入口卡片 / 按钮）
        ↓
Trust Metrics（信任标识）
        ↓
Scroll Hint（下滑引导）
```

**适用**：金融产品、SaaS 首页、AI 产品

#### Feature Pattern（功能展示模式）

```
Section Label（标签）
    ↓
Section Title（标题）
    ↓
┌────────┐  ┌────────┐  ┌────────┐
│ Icon   │  │ Icon   │  │ Icon   │
│ Title  │  │ Title  │  │ Title  │
│ Desc   │  │ Desc   │  │ Desc   │
└────────┘  └────────┘  └────────┘
         3 列 grid
```

**适用**：服务介绍、产品优势、适用场景

#### FAQ Pattern（常见问题模式）
```
┌──────────────┐  ┌──────────────┐
│ Q1  ▶      │  │ Q5  ▶      │
│ Q2  ▶      │  │ Q6  ▶      │
│ Q3  ▶      │  │ Q7  ▶      │
│ Q4  ▶      │  │ Q8  ▶      │
└──────────────┘  └──────────────┘
         双列折叠
```

**适用**：FAQ、常见问题拦截

#### CTA Pattern（转化模式）
```
[            CTA Button →            ]
```

**适用**：页底转化、联系入口

### 栅格系统

| 规格 | 列数 | gap | 用途 |
|---|---|---|---|
| 3 列 grid | 1fr 1fr 1fr | 20px | 功能卡片 |
| 2 列 grid | 1fr 1fr | 20px | FAQ、合规 |
| 双入口 | 1fr 1fr | 40px | Hero CTA |
| 表单 | 1fr 1fr | 18px | 输入字段 |

### 响应式

| 断点 | 变化 |
|---|---|
| >900px | 桌面完整布局 |
| ≤900px | grid 降级为 1 列，导航链接隐藏 |
| ≤640px | 字体缩小、间距压缩、卡片内边距缩小 |

---

## 05. Component Library

### 组件清单

| 组件 | 用途 | 核心结构 |
|---|---|---|
| **SeraHero** | 首屏价值主张 | 标题 + 副标题 + CTA + 信任提示 |
| **SeraFeatureCard** | 功能展示 | 图标 + 标题 + 说明 + 悬停动效 |
| **SeraCardGrid** | 卡片矩阵容器 | 3 列 / 2 列栅格 |
| **SeraFAQ** | 常见问题 | 双列折叠 + 更多展开 |
| **SeraCTABar** | 转化按钮 | 品牌色按钮 + 箭头 |
| **SeraTrustBadge** | 信任标识 | 图标 + 简短说明 |
| **SeraFormCard** | 表单容器 | 分步表单 + 弹窗 |
| **SeraScrollHint** | 下滑引导 | 玻璃质感按钮 + 浮动动画 |
| **SeraNoticeBar** | 提示条 | 跑马灯式滚动 |
| **SeraKPICard** | 数据指标 | 标题 + 数值 + 进度条 + 状态 |
| **SeraCountdown** | 任务倒计时 | 编号 + 标题 + 倒计时 + 优先级 |
| **SeraPipeline** | 工作项分组 | 状态分组 + 列表 |

### 卡片通用样式

```css
.card {
  background: rgba(255,255,255,.62);
  backdrop-filter: blur(14px);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 28px;
  transition: all 0.3s cubic-bezier(.16,1,.3,1);
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 32px rgba(0,82,255,.10);
  border-color: #0052FF;
}
```

---

## 06. Motion System

### 核心缓动

```css
/* Sera Ease — 所有动效统一使用 */
cubic-bezier(0.16, 1, 0.3, 1)
```

**特性**：起始快 → 迅速响应 | 结束缓 → 自然减速

### 动效清单

| 动效 | 时长 | 触发 | 方式 |
|---|---|---|---|
| 浮现 Reveal | 0.72s | 页面滚动 | translateY(26px) + opacity 0→1 |
| 卡片悬停 | 0.3s | hover | ↑-3px + shadow + border-color |
| CTA 箭头 | 0.3s | hover | translateX(4px) |
| 手风琴展开 | 0.35s | click | max-height transition |
| 弹窗出现 | 0.35s | click | translateY(18px) + scale(0.97) → 1 |
| 下滑引导 | 2.4s infinite | 自动 | translateY(0→9px) 浮动 |
| 步骤切换 | 0.38-0.42s | click | translateX(-100%→0) |

### 动效原则

1. **统一缓动** — 所有动效使用同一曲线
2. **克制** — 悬停仅上移+阴影，不做夸张效果
3. **自然** — 从下往上 + 淡入，符合阅读动线
4. **性能** — 只用 transform + opacity（GPU 加速）
5. **可访问性** — 支持 prefers-reduced-motion

---

## 07. Conversion Architecture

### 转化漏斗

```
Attention（注意）
    ↓
Understanding（理解）
    ↓
Trust（信任）
    ↓
Action（行动）
```

### 着陆页转化路径

```
路径 A（客户自助）
Hero → 选择方向 → 查看流程 → 提交需求 → 人工联系

路径 B（FAQ 转化）
FAQ → 仍有疑问 → 人工联系

路径 C（直接转化）
CTA → 表单 → 提交 → 成功
```

### 转化设计模式

| 模式 | 说明 | 适用场景 |
|---|---|---|
| **首屏双 CTA** | 两个入口卡片并排，客户立即选择方向 | 金融产品 |
| **渐进式表单** | 分步收集，降低填写压力 | 复杂表单 |
| **弹窗表单** | 不跳转页面，保持上下文 | 需求提交 |
| **逃生出口** | 所有转化失败场景提供人工联系 | 所有表单 |
| **信任前置** | 信任信号在首屏可见 | 金融/高信任需求 |
| **FAQ 拦截** | 常见问题在转化前解决 | 所有产品页 |

### 表单设计原则

1. **最小字段集** — 只收关键字段，补充字段后续收集
2. **分步收集** — 3 步以内完成，每步 ≤ 3 个字段
3. **状态明确** — 默认 → 填写中 → 校验失败 → 提交中 → 成功/失败
4. **逃生出口** — 始终提供"资料不齐，人工联系"选项

---

## 08. Dashboard Design Language

### Dashboard 设计原则

| 原则 | 说明 |
|---|---|
| **信息密度优先** | 效率优于美观，数据密度合理 |
| **状态一目了然** | 每个项目第一时间展示状态标签 |
| **数据驱动** | 所有指标可量化、可追踪 |
| **下一步明确** | 每个模块底部展示下一步动作 |
| **实时性** | 关键数据秒级刷新 |

### KPI 卡片结构

```
┌──────────────────────────────────┐
│ 指标名称                         │
│ 状态标签（待启动/进行中/已完成）  │
│ 当前值 / 目标值 · 百分比         │
│ ████████░░░░░░░░░░░░ 进度条     │
│ 下一步：具体行动描述              │
└──────────────────────────────────┘
```

### 状态系统

```
🟢 已完成  — 绿色
🔵 进行中  — 蓝色
⚪ 待启动  — 灰色
🔴 已阻塞  — 红色
```

---

## 09. Usage Guide

### 适用场景

| 场景 | 推荐模式 | 核心组件 |
|---|---|---|
| 金融产品首页 | Hero + Feature + FAQ + CTA | SeraHero, SeraFeatureCard, SeraFAQ |
| SaaS 产品页 | Hero + Feature + CTA | SeraHero, SeraFeatureCard, SeraCTABar |
| AI 产品发布 | Hero + Feature + Trust + CTA | SeraHero, SeraTrustBadge, SeraCTABar |
| 运营 Dashboard | KPI + Pipeline + Timeline | SeraKPICard, SeraCountdown, SeraPipeline |
| 项目管理页 | Summary + KPI + Tasks | SeraKPICard, SeraPipeline, SeraCountdown |

### 快速启动

1. 确定产品类型 → 选择对应场景模板
2. 定义品牌色 → 设置 `--brand` 和 `--brand-dark`
3. 构建页面结构 → 按 Hero → Feature → Trust → FAQ → CTA 顺序
4. 应用字体层级 → 标题 800 / 卡片标题 700 / 正文 400
5. 添加动效 → 统一使用 Sera Ease 缓动
6. 检查深色模式 → 验证色彩映射是否正确

### 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0.0 | 2026-08-21 | 初始版本，基于 HTX OTC Landing + Progress Hub 提取 |

---

*Sera FinTech Visual Language V1.0 · 属于 Sera Design Intelligence System*