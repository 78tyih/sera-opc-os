# Sera Component Library — 组件库

> 版本：v1.0
> 来源：Sera FinTech Visual Language V1.0
> 适用范围：金融科技 / SaaS / AI 产品页面

---

## 1. 组件索引

### Landing Page 组件

| 组件 | 优先级 | 依赖 | 状态 |
|---|---|---|---|
| `SeraHero` | P0 | — | ✅ v1 |
| `SeraFeatureCard` | P0 | — | ✅ v1 |
| `SeraCardGrid` | P0 | — | ✅ v1 |
| `SeraFAQ` | P0 | — | ✅ v1 |
| `SeraCTABar` | P0 | — | ✅ v1 |
| `SeraTrustBadge` | P1 | — | ✅ v1 |
| `SeraFormCard` | P1 | SeraFormStep | ✅ v1 |
| `SeraScrollHint` | P2 | — | ✅ v1 |
| `SeraNoticeBar` | P2 | — | ✅ v1 |

### Dashboard 组件

| 组件 | 优先级 | 依赖 | 状态 |
|---|---|---|---|
| `SeraKPICard` | P0 | — | ✅ v1 |
| `SeraCountdown` | P0 | — | ✅ v1 |
| `SeraPipeline` | P0 | — | ✅ v1 |
| `SeraSummaryCard` | P1 | — | ✅ v1 |
| `SeraTimeline` | P1 | — | ✅ v1 |
| `SeraStatusBadge` | P0 | — | ✅ v1 |

---

## 2. 组件规范

### 2.1 SeraHero

**用途**：产品首屏价值主张展示

**结构**：
```
┌──────────────────────────────────────────┐
│                                          │
│      大标题 (64px 800 -1.5px)           │
│            ↓                             │
│      副标题 (17px 400 text2)            │
│            ↓                             │
│  ┌──────────┐  ┌──────────┐             │
│  │ CTA 1    │  │ CTA 2    │             │
│  └──────────┘  └──────────┘             │
│            ↓                             │
│     信任提示 (13px text3)               │
│            ↓                             │
│     下滑引导按钮                         │
└──────────────────────────────────────────┘
```

**CSS 规范**：
```css
.hero {
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.hero h1 {
  font-size: clamp(44px, 6vw, 64px);
  font-weight: 800;
  letter-spacing: -1.5px;
  line-height: 1.14;
}
```

### 2.2 SeraFeatureCard

**用途**：功能 / 服务 / 优势展示

**结构**：
```
┌──────────────────────────┐
│  [icon 44×44]            │
│  标题 17px 700           │
│  描述 14px text2         │
│                          │
│  hover: ↑-3px shadow    │
│  border-color: brand     │
└──────────────────────────┘
```

**CSS 规范**：
```css
.feature-card {
  background: rgba(255,255,255,.62);
  backdrop-filter: blur(14px);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 28px;
  transition: all 0.3s cubic-bezier(.16,1,.3,1);
}
.feature-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
  border-color: var(--brand);
}
```

### 2.3 SeraFAQ

**用途**：常见问题折叠展示

**结构**：
```
┌──────────────────────────────────┐
│  ┌────────────────────────────┐  │
│  │ 问题 15.5px 600    ▶    │  │
│  ├────────────────────────────┤  │
│  │ 答案 14px text2           │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ 更多信息 ▼                │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

**交互**：
- 点击问题展开/折叠
- 展开时箭头旋转 180°，边框变品牌色
- 内容使用 max-height transition（0.35s）

### 2.4 SeraKPICard

**用途**：Dashboard 数据指标展示

**结构**：
```
┌──────────────────────────────────┐
│  指标名称                        │
│  状态标签                        │
│  当前值 / 目标值 · 百分比       │
│  ████████░░░░░░░░░░░░ 进度条    │
│  下一步：具体行动描述            │
└──────────────────────────────────┘
```

**状态标签**：
```css
.status-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}
.status-badge.done { background: #EAF9F0; color: #16A34A; }
.status-badge.active { background: #EEF4FF; color: #0052FF; }
.status-badge.pending { background: #F6F8FB; color: #8A93A6; }
.status-badge.blocked { background: #FFF0F0; color: #E5484D; }
```

### 2.5 SeraCTABar

**用途**：页面底部转化按钮

**结构**：
```css
.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  background: var(--brand);
  color: #fff;
  border-radius: 10px;
  padding: 14px 32px;
  font-size: 15px;
  font-weight: 700;
  transition: all 0.25s cubic-bezier(.16,1,.3,1);
}
.cta-btn:hover {
  background: var(--brand-dark);
  transform: translateY(-2px);
  box-shadow: 0 10px 26px rgba(0,82,255,.4);
}
```

---

## 3. 组件组合模式

### 3.1 金融产品首页
```
SeraHero
    ↓
SeraCardGrid + SeraFeatureCard × 3
    ↓
SeraCardGrid + SeraFeatureCard × 6（合规）
    ↓
SeraFAQ
    ↓
SeraCTABar
```

### 3.2 运营 Dashboard
```
SeraSummaryCard
    ↓
SeraKPICard × 6
    ↓
SeraCountdown × N
    ↓
SeraPipeline × 4（按状态分组）
    ↓
SeraTimeline
```

### 3.3 产品功能页
```
SeraHero（精简版）
    ↓
SeraFeatureCard × 3（核心功能）
    ↓
SeraFeatureCard × 3（技术优势）
    ↓
SeraCTABar
```

---

## 4. 组件使用规则

### 4.1 通用规则
- 所有组件支持亮色/深色模式
- 所有组件响应式（桌面 → 移动端）
- 所有交互组件使用 Sera Ease 缓动
- 所有卡片在 hover 时统一动效

### 4.2 命名规则
```css
/* 组件前缀：sera- */
.sera-hero
.sera-feature-card
.sera-faq
.sera-kpi-card
.sera-status-badge
.sera-cta-bar
```

### 4.3 深色模式适配
```css
[data-theme="dark"] .sera-card {
  background: rgba(22,24,29,.6);
}
```

### 4.4 响应式适配
```css
@media (max-width: 900px) {
  .sera-grid-3 { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .sera-card { padding: 20px; }
}
```