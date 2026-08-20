# Sera Asset Library — 资产库索引

> 版本：2.0.0
> 新增：Asset Graph 关系网络

---

## 资产库结构

```
assets/
│
└── <case-name>/
    ├── logo/           ← Logo 源文件（SVG / PNG / White variant）
    ├── icons/          ← 图标集（SVG sprite / Individual SVGs）
    ├── colors/         ← 色彩 Token（JSON / CSS variables）
    ├── images/         ← 截图 / 素材（Hero / Background / Shots）
    ├── fonts/          ← 字体文件（WOFF2 / OTF / TTF）
    └── components/     ← 组件代码（HTML / CSS / JS snippets）
```

---

## Asset Graph（资产关系网络）

每个 Style 的资产之间存在层级关系，形成可导航的资产图：

### htx-otc-v1 Asset Graph

```
sera-fintech-premium
│
├── [logo] ──────────────────────────────────── brand-logo.svg
│
├── [colors] ─── tokens.json
│   ├── primary: #0052FF
│   ├── dark_bg: #060708
│   └── semantic: #16A34A / #E5484D
│
├── [components]
│   ├── hero.html ──────────────── 依赖: logo.svg, tokens.json
│   ├── feature-card.html ──────── 依赖: tokens.json, icons/
│   ├── faq.html ───────────────── 依赖: tokens.json
│   └── cta-bar.html ───────────── 依赖: tokens.json
│
├── [images]
│   ├── hero-screenshot.png ────── 对应: hero.html
│   └── section-feature.png ────── 对应: feature-card.html
│
└── [references]
    ├── analysis.md ─────────────── 分析整个 Style
    ├── extracted-rules.md ──────── 提取的设计规则
    └── reproduction-prompt.md ──── 可复现 Prompt
```

### 关系类型

| 关系 | 说明 | 示例 |
|---|---|---|
| `contains` | 包含关系 | Style → Component |
| `depends_on` | 依赖关系 | Component → Color Token |
| `corresponds_to` | 对应关系 | Screenshot → Component |
| `references` | 引用关系 | Analysis → Style |

---

## 资产索引

| 案例 | Logo | Icons | Colors | Images | Fonts | Components | References |
|---|---|---|---|---|---|---|---|
| htx-otc-v1 | ⏳ | ⏳ | ⏳ | ⏳ | — | ⏳ | ✅ 3 docs |
| propfirm-tv | — | — | — | — | — | — | — |
| tradespan | — | — | — | — | — | — | — |

---

## 资产命名规范

### 文件命名

```
logo/
  brand-logo.svg
  brand-logo-white.svg
  brand-icon.svg

icons/
  icon-set.svg         ← SVG sprite（推荐）
  icon-arrow.svg
  icon-check.svg

colors/
  tokens.json           ← Design Token（JSON 格式）
  tokens.css            ← CSS Variables（备用）

images/
  hero-screenshot.png
  section-feature.png
  section-faq.png
  background-pattern.svg

components/
  hero.html
  feature-card.html
  faq.html
  cta-bar.html
```

### Token JSON 格式

```json
{
  "brand": {
    "primary": "#0052FF",
    "dark": "#003ECC",
    "soft": "#EEF4FF"
  },
  "neutral": {
    "bg": "#FFFFFF",
    "bg-soft": "#F6F8FB",
    "line": "#E8ECF2",
    "text": "#14181F",
    "text2": "#5A6272",
    "text3": "#8A93A6"
  },
  "semantic": {
    "success": "#16A34A",
    "error": "#E5484D",
    "warning-bg": "#FFF8EC",
    "warning-border": "#F5E3B8"
  }
}
```

---

## 与 Eagle 的连接

```
Sera Design Intelligence
    ↓
Asset Manager Agent
    ↓
Eagle（本地素材管理）
    ↓
assets/ 目录同步
```

### 导入规则

1. 截图 → Eagle 分类为 "Sera Design References"
2. Logo/Icon → Eagle 分类为 "Sera Design Assets"
3. Color Token → 同步到 Eagle 色彩标签
4. 组件代码 → 保留在 assets/components/ 目录