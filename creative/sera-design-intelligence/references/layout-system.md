# Sera Layout System — 布局系统

> 版本：v1.0
> 来源：HTX OTC Landing
> 风格：Clean · Modular · Responsive

---

## 1. 容器系统

### 1.1 容器层级
```
body
  header (fixed, z-index 100)
    .nav (max-width: 1072px, centered)
  section (padding: 84px 0)
    .wrap (max-width: 1120px, padding: 0 24px)
      .sec-head (text-align: center)
      .content-grid (grid/flex)
  footer (padding: 40px 0 48px)
```

### 1.2 尺寸规范
| 层级 | 桌面 | 移动端 |
|---|---|---|
| `.wrap` max-width | 1120px | 100% |
| `.wrap` padding | 0 24px | 0 16px |
| `.nav` max-width | 1072px | 100% |
| Section padding | 84px 0 | 52px 0 |
| 首屏 padding | 96px top, 280px bottom | 82px top, 110px bottom |

---

## 2. 栅格系统

### 2.1 三列栅格
```css
/* 服务介绍、合作模式、流程步骤 */
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
@media (max-width: 900px) {
  .grid-3 { grid-template-columns: 1fr; }
}
```

### 2.2 双列栅格
```css
/* 合规卡片、FAQ */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 900px) {
  .grid-2 { grid-template-columns: 1fr; }
}
```

### 2.3 双入口卡片（Hero）
```css
.track-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}
@media (max-width: 900px) {
  .track-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}
```

### 2.4 表单布局
```css
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.field.full { grid-column: 1 / -1; }  /* 占满整行 */
```

---

## 3. Section 标准结构

```html
<section id="section-name">
  <div class="wrap">
    <!-- Section Header -->
    <div class="sec-head">
      <div class="sec-tag">SECTION_LABEL</div>
      <h2>Section Title</h2>
      <p>Section description text</p>
    </div>
    <!-- Content Area -->
    <div class="content-grid">
      <!-- Cards / Content -->
    </div>
  </div>
</section>
```

### CSS 标准
```css
section { padding: 84px 0; }
.sec-head { text-align: center; margin-bottom: 50px; }
.sec-tag {
  font-size: 12.5px; font-weight: 700;
  color: var(--brand); letter-spacing: 2px;
  text-transform: uppercase; margin-bottom: 14px;
}
.sec-head h2 {
  font-size: clamp(44px, 6vw, 64px);
  font-weight: 800; letter-spacing: -1.2px;
}
.sec-head p {
  color: var(--text2); margin-top: 10px; font-size: 15px;
}
```

---

## 4. 卡片系统

### 4.1 标准卡片
```css
.card {
  background: rgba(255,255,255,.62);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid var(--line);
  border-radius: var(--radius, 14px);
  padding: 28px;
  transition: all 0.3s cubic-bezier(.16,1,.3,1);
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
  border-color: var(--brand);
}
```

### 4.2 卡片变体
| 变体 | 圆角 | 内边距 | 特点 |
|---|---|---|---|
| 标准卡片 | 14px | 28px | 通用信息展示 |
| 入口卡片 | 22px | 22px 24px | Hero 双入口 |
| 合规卡片 | 12px | 26px 28px | 左侧 4px 品牌色边框 |
| 表单卡片 | 16px | 38px | 表单容器 |
| 弹窗卡片 | 22px | 30px | 弹窗内容 |

### 4.3 深色模式卡片
```css
[data-theme="dark"] .card {
  background: rgba(22,24,29,.6);
}
```

---

## 5. 响应式断点

### 5.1 断点定义
| 断点 | 说明 | 变化 |
|---|---|---|
| >900px | 桌面 | 完整布局 |
| ≤900px | 平板 | grid 降级、导航隐藏 |
| ≤640px | 手机 | 缩小字号、间距 |

### 5.2 移动端适配
```css
@media (max-width: 900px) {
  section { padding: 60px 0; }
  .wrap { padding: 0 24px; }
  .nav-links { display: none; }
  .track-grid,
  .cmp-grid,
  .form-grid { grid-template-columns: 1fr; }
  .svc-grid,
  .modes-grid,
  .inst-flow { grid-template-columns: 1fr; }
  .faq-cols { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  section { padding: 52px 0; }
  .wrap { padding: 0 16px; }
  .hero h1 { font-size: clamp(29px, 8.4vw, 38px); }
  .sec-head h2 { font-size: clamp(27px, 7.4vw, 34px); }
  .card { padding: 20px; }
}
```

---

## 6. 间距系统

### 6.1 垂直间距
| 层级 | 桌面 | 移动 |
|---|---|---|
| Section 间距 | 84px | 52px |
| Section 头部底部 | 50px | 34px |
| 卡片内部 | 28px | 20px |
| 标题下方 | 22px (Hero) / 14px (Section) | 16px / 10px |
| 标签下方 | 14px | 10px |
| 页脚间距 | 40px 0 48px | 32px 0 40px |

### 6.2 水平间距（gap）
| 场景 | 桌面 | 移动 |
|---|---|---|
| 3 列栅格 | 20px | — |
| 2 列栅格 | 20px | — |
| 双入口卡片 | 40px | 20px |
| 表单字段 | 18px | 14px |
| 导航链接 | 20px | — |

---

## 7. 布局模式库

### 7.1 Hero 全屏首屏
```
┌──────────────────────────────────────────┐
│  导航栏                                  │
│                                          │
│                                          │
│             主标题 (64px 800)            │
│                    ↓                     │
│             副标题 (17px)                │
│                    ↓                     │
│       ┌──────────┐  ┌──────────┐        │
│       │ 买 U 入口 │  │ 卖 U 入口 │        │
│       └──────────┘  └──────────┘        │
│                    ↓                     │
│           KYC 提示 (13px)               │
│                    ↓                     │
│             下滑引导按钮                  │
└──────────────────────────────────────────┘
```

### 7.2 卡片矩阵 Section
```
┌──────────────────────────────────────────┐
│              LABEL                        │
│            Section Title                  │
│          Section Subtitle                 │
│                                          │
│ ┌────────┐  ┌────────┐  ┌────────┐      │
│ │ Card 1 │  │ Card 2 │  │ Card 3 │      │
│ └────────┘  └────────┘  └────────┘      │
└──────────────────────────────────────────┘
```

### 7.3 双列 FAQ Section
```
┌──────────────────────────────────────────┐
│              FAQ                          │
│          Questions & Answers              │
│                                          │
│ ┌──────────────┐  ┌──────────────┐       │
│ │ Q1  ▶      │  │ Q4  ▶      │       │
│ │ Q2  ▶      │  │ Q5  ▶      │       │
│ │ Q3  ▶      │  │ Q6  ▶      │       │
│ └──────────────┘  └──────────────┘       │
│                                          │
│            [更多信息 ▼]                   │
└──────────────────────────────────────────┘
```

### 7.4 CTA 条
```
┌──────────────────────────────────────────┐
│                                          │
│        [ 联系 OTC Desk → ]               │
│                                          │
└──────────────────────────────────────────┘
```