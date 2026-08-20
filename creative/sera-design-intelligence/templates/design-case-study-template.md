# Design Case Study — <项目名称>

> 模板版本：2.0.0
> 类型：Design Reverse Engineering
> 使用说明：每个 Case Study 必须包含以下 12 个章节。填写时保持分析深度，不要只描述表面。

---

## 00. Metadata

```yaml
name: <项目名称>
category: <fintech | saas | ai | content | dashboard>
source: <项目来源>
url: <项目链接>
industry: <行业>
style: <风格标签>
created: <分析日期>
version: 2.0.0
```

---

## 01. Business Goal

### 这个产品解决什么问题？

> 一句话说明产品价值。

### 商业模式

```
- 产品形态：<SaaS / 交易平台 / 内容 / 工具>
- 收入来源：<订阅 / 交易费 / 广告 / 免费>
- 用户获取：<渠道>
```

### 设计目标

```
核心目标：<设计要达成的业务指标>
关键结果：<设计对业务的量化影响>
```

---

## 02. Target Audience

### 用户画像

```
- 画像 1：<描述>
- 画像 2：<描述>
- 画像 3：<描述>
```

### 用户决策路径

```
认知 → 考虑 → 决策 → 使用
  ↓      ↓      ↓      ↓
<各阶段用户关注点>
```

### 设计对用户的影响

```
- 认知阶段：<吸引注意力的设计>
- 考虑阶段：<建立信任的设计>
- 决策阶段：<降低门槛的设计>
- 使用阶段：<引导行动的设计>
```

---

## 03. Conversion Strategy

### 转化漏斗

```
Attention（注意）
    ↓  <转化率估值>
Understanding（理解）
    ↓  <转化率估值>
Trust（信任）
    ↓  <转化率估值>
Action（行动）
```

### 转化路径

```
路径 A（主路径）：
<步骤 1> → <步骤 2> → <步骤 3>

路径 B（备用路径）：
<步骤 1> → <步骤 2>

路径 C（逃生出口）：
<步骤 1> → 人工联系
```

### 转化设计模式

| 模式 | 位置 | 说明 |
|---|---|---|
| <模式名> | <位置> | <说明> |
| <模式名> | <位置> | <说明> |

---

## 04. Visual DNA

### Brand Personality

```
- 特质 1
- 特质 2
- 特质 3
- 特质 4
```

### Emotional Keywords

```
- 关键词 1
- 关键词 2
- 关键词 3
```

### Positioning

```
品牌定位一句话描述。
```

### 设计 DNA 评分

```yaml
trust_level: <1-10>
technology_level: <1-10>
luxury_level: <1-10>
playfulness_level: <1-10>
minimalism_level: <1-10>
```

---

## 05. Visual System

### Color System

```yaml
primary:
  hex: <主色>
  usage: <用途>

secondary:
  hex: <辅色>
  usage: <用途>

background:
  - name: <背景色名>
    hex: <色值>
    usage: <用途>

text:
  - name: <文字色名>
    hex: <色值>
    usage: <用途>

semantic:
  success: <色值>
  error: <色值>
  warning: <色值>
```

### Typography

```yaml
font_stack: <字体栈>
headings:
  size: <字号>
  weight: <字重>
  spacing: <字距>
body:
  size: <字号>
  weight: <字重>
  line_height: <行高>
```

### Spacing & Grid

```yaml
unit: <基础间距单位>
section_gap: <板块间距>
card_padding: <卡片内边距>
content_max_width: <内容最大宽度>
columns: <列数>
gap: <间距>
```

### Icon & Illustration Style

```yaml
icon_style: <linear | filled | outline>
icon_stroke: <描边宽度>
illustration_style: <风格描述>
illustration_palette: <用色>
```

---

## 06. UI Pattern Library

### Section 结构

```text
01 Hero（模式：<金融信任型 / SaaS 产品型 / AI 产品型>）
02 Navigation
03 Feature Section
04 Product Demo
05 Trust Section
06 Process / Timeline
07 FAQ
08 CTA
09 Footer
```

### 每 Section 分析

**Hero**

```
模式：<模式名>
结构：
┌──────────────────────────────┐
│                              │
│  大标题                      │
│  副标题                      │
│  CTA                         │
│  信任信号                    │
└──────────────────────────────┘

特点：
- <特 1>
- <特 2>
参考 pattern：<hero-section-patterns.md 中的模式>
```

**Feature Section**

```
布局：<3列 / 2列 / 混合>
内容：<卡片 / 列表 / 图文>
交互：<悬停 / 点击 / 滚动>
```

**Trust Section**

```
信任信号类型：<数据 / 客户 / 认证 / 合规>
布局方式：<网格 / 条状 / 嵌入>
```

**CTA**

```
位置：<页面底部 / 固定 / 弹窗>
样式：<填充 / 边框 / 文字>
文案模式：<行动导向 / 价值导向>
```

---

## 07. Component Extraction

### 提取组件

| 组件 | 用途 | 结构 | 状态 | 可复用性 |
|---|---|---|---|---|
| `<组件名>` | `<用途>` | `<结构>` | `✅ v1` | `<高/中/低>` |
| `<组件名>` | `<用途>` | `<结构>` | `✅ v1` | `<高/中/低>` |

### 组件详情

**<组件名>**

```
结构：
┌──────────────────────────┐
│  <元素 1>                │
│  <元素 2>                │
│  <元素 3>                │
└──────────────────────────┘

交互：<hover / click / scroll>
状态：<default / hover / active / disabled>
依赖：<依赖的组件>
```

### 可复用组件筛选

| 组件 | 跨项目复用性 | 适用场景 |
|---|---|---|
| <组件> | 高 | 所有金融产品页 |
| <组件> | 中 | 需要信任展示的页面 |
| <组件> | 低 | 仅限本项目 |

---

## 08. Motion System

### 动效清单

| 动效 | 时长 | 触发 | 方式 | 用途 |
|---|---|---|---|---|
| `<动效名>` | `<时长>` | `<触发>` | `<方式>` | `<用途>` |

### 核心缓动

```css
/* 缓动函数 */
<easing-function>
```

### 动效原则

```
- 原则 1
- 原则 2
- 原则 3
```

---

## 09. Copywriting Structure

### Headline 模式

```
结构：<模式>
示例：<原文>
分析：<为什么有效>
```

### Subheadline 模式

```
结构：<模式>
示例：<原文>
分析：<为什么有效>
```

### CTA 文案模式

```
结构：<模式>
示例：<原文>
分析：<为什么有效>
```

### 转化逻辑

```
用户路径：
注意 → 理解 → 信任 → 行动
                          ↓
<各阶段文案策略>
```

---

## 10. Reproduction Prompt

> 以下 Prompt 可直接用于 AI Agent（Claude Code / Codex / Trae / DeepSeek）生成类似风格页面。

```markdown
Create a <类型> page inspired by <项目名> style.

## Design Requirements

### Style
- <风格要求 1>
- <风格要求 2>
- <风格要求 3>

### Color Palette
- Primary: <色值>
- Background: <色值>
- Text: <色值>
- Accent: <色值>

### Typography
- Font: <字体>
- Headings: <字号+字重>
- Body: <字号+字重>

### Layout
- <布局要求 1>
- <布局要求 2>

### Components
- <组件 1>
- <组件 2>
- <组件 3>

### Motion
- <动效要求 1>
- <动效要求 2>
```

---

## 11. Reusable Skill

### 提取的 Design Skill

```yaml
skill_name: <从本案提取的技能名>
based_on: <项目名>
type: <visual-style | layout-style | component-set>
best_for: <适用场景>
core_rules:
  - <规则 1>
  - <规则 2>
  - <规则 3>
```

### 注册到 Style Registry

```json
{
  "id": "<style-id>",
  "name": "<style-name>",
  "trust_level": <1-10>,
  "technology_level": <1-10>,
  "luxury_level": <1-10>,
  "recommended_for": ["<场景>"]
}
```

---

## 12. Assets

### 资产清单

| 类型 | 路径 | 说明 |
|---|---|---|
| Logo | `assets/logo/` | Logo 文件 |
| Colors | `assets/colors/tokens.json` | 色彩 Token |
| Icons | `assets/icons/` | 图标集 |
| Images | `assets/images/` | 截图/素材 |
| Fonts | `assets/fonts/` | 字体文件 |
| Components | `assets/components/` | 组件代码 |

### Asset Graph 关系

```
<Style Name>
  ├── logo/ → brand-logo.svg
  ├── colors/ → tokens.json
  ├── components/ → hero.html
  │                    └── feature-card.html
  ├── images/ → hero-screenshot.png
  └── references/ → case-study-analysis.md
```

---

## 13. Key Learnings

### 成功的决策

```
- 决策 1
- 决策 2
- 决策 3
```

### 需要改进的方面

```
- 改进 1
- 改进 2
```

### 新增设计规则

```
- 规则 1（适用于未来项目）
- 规则 2
- 规则 3
```