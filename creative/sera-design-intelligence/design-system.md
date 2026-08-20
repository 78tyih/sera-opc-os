# Sera Design System — 设计系统规范

> 版本：v1.0
> 来源：Sera FinTech Visual Language V1.0
> 适用范围：所有 Sera 产品页面设计

---

## 1. Design Tokens

### 1.1 色彩 Token

```css
/* Brand Colors */
--brand: #0052FF;
--brand-dark: #003ECC;
--brand-soft: #EEF4FF;

/* Neutral Colors */
--bg: #FFFFFF;
--bg-soft: #F6F8FB;
--line: #E8ECF2;
--text: #14181F;
--text2: #5A6272;
--text3: #8A93A6;

/* Semantic Colors */
--success: #16A34A;
--success-bg: #EAF9F0;
--error: #E5484D;
--error-bg: #FFF0F0;
--warning-bg: #FFF8EC;
--warning-border: #F5E3B8;
--warning-text: #8A6D1A;

/* Shadows */
--shadow: 0 2px 12px rgba(20, 30, 60, 0.05);
--shadow-hover: 0 10px 32px rgba(0, 82, 255, 0.10);
--shadow-nav: 0 6px 24px rgba(20, 30, 60, 0.07);
--shadow-modal: 0 24px 64px rgba(10, 25, 80, 0.20);

/* Dark Mode */
--dark-brand: #3E8EFF;
--dark-brand-dark: #62A5FF;
--dark-brand-soft: rgba(62, 142, 255, 0.14);
--dark-bg: #060708;
--dark-bg-soft: rgba(255, 255, 255, 0.05);
--dark-line: rgba(255, 255, 255, 0.1);
--dark-text: #EDEFF3;
--dark-text2: #A2A8B3;
--dark-text3: #797F8B;
--dark-card-bg: rgba(22, 24, 29, 0.6);
```

### 1.2 空间 Token

```css
/* Container */
--wrap-max-width: 1120px;
--nav-max-width: 1072px;
--wrap-padding: 24px;
--wrap-padding-mobile: 16px;

/* Section */
--section-gap: 84px;
--section-gap-mobile: 52px;
--section-head-margin: 50px;

/* Card */
--card-radius: 14px;
--card-radius-lg: 22px;
--card-radius-sm: 12px;
--card-padding: 28px;
--card-padding-mobile: 20px;
--card-gap: 20px;

/* Grid */
--grid-gap: 20px;
--grid-gap-lg: 40px;
--grid-gap-sm: 14px;
```

### 1.3 动效 Token

```css
--ease-sera: cubic-bezier(0.16, 1, 0.3, 1);
--duration-reveal: 0.72s;
--duration-hover: 0.3s;
--duration-expand: 0.35s;
--duration-modal: 0.35s;
--duration-float: 2.4s;
```

### 1.4 字体 Token

```css
--font-stack: -apple-system, BlinkMacSystemFont, "Helvetica Neue",
  "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;

--fs-hero: clamp(44px, 6vw, 64px);
--fs-section: clamp(44px, 6vw, 64px);
--fs-card-title: 17px;
--fs-body: 14px;
--fs-aux: 13px;
--fs-tag: 12.5px;
--fs-risk: 12px;

--fw-hero: 800;
--fw-card-title: 700;
--fw-tag: 700;
--fw-body: 400;

--ls-hero: -1.5px;
--ls-section: -1.2px;
--ls-tag: 2px;

--lh-hero: 1.14;
--lh-body: 1.65;
```

---

## 2. 通用样式

### 2.1 Reset
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: var(--font-stack);
  -webkit-font-smoothing: antialiased;
  line-height: 1.65;
}
```

### 2.2 容器
```css
.wrap {
  max-width: var(--wrap-max-width);
  margin: 0 auto;
  padding: 0 var(--wrap-padding);
}
@media (max-width: 640px) {
  .wrap { padding: 0 var(--wrap-padding-mobile); }
}
```

### 2.3 Section 标准
```css
section { padding: var(--section-gap) 0; }
.sec-head {
  text-align: center;
  margin-bottom: var(--section-head-margin);
}
.sec-tag {
  font-size: var(--fs-tag);
  font-weight: var(--fw-tag);
  color: var(--brand);
  letter-spacing: var(--ls-tag);
  text-transform: uppercase;
  margin-bottom: 14px;
}
.sec-head h2 {
  font-size: var(--fs-section);
  font-weight: var(--fw-hero);
  letter-spacing: var(--ls-section);
}
.sec-head p {
  color: var(--text2);
  margin-top: 10px;
  font-size: 15px;
}
@media (max-width: 640px) {
  section { padding: var(--section-gap-mobile) 0; }
  .sec-head h2 { font-size: clamp(27px, 7.4vw, 34px); }
}
```

### 2.4 卡片通用
```css
.card {
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid var(--line);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  transition: all var(--duration-hover) var(--ease-sera);
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
  border-color: var(--brand);
}
[data-theme="dark"] .card {
  background: var(--dark-card-bg);
}
@media (max-width: 640px) {
  .card { padding: var(--card-padding-mobile); }
}
```

### 2.5 按钮
```css
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  background: var(--brand);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 14px 32px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  transition: all var(--duration-hover) var(--ease-sera);
}
.btn-primary:hover {
  background: var(--brand-dark);
  transform: translateY(-2px);
  box-shadow: 0 10px 26px rgba(0, 82, 255, 0.4);
}
```

### 2.6 表单
```css
.field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.field input,
.field select,
.field textarea {
  border: 1.5px solid var(--line);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 14px;
  font-family: inherit;
  color: var(--text);
  background: #fff;
  outline: none;
  transition: all 0.2s;
}
.field input:focus,
.field select:focus,
.field textarea:focus {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(0, 82, 255, 0.12);
}
```

---

## 3. 响应式断点

```css
/* Desktop (>900px) */
/* 默认样式 */

/* Tablet (≤900px) */
@media (max-width: 900px) {
  .grid-3, .grid-2 { grid-template-columns: 1fr; }
  .nav-links { display: none; }
  section { padding: 60px 0; }
}

/* Mobile (≤640px) */
@media (max-width: 640px) {
  :root {
    --wrap-padding: 16px;
    --section-gap: 52px;
    --card-padding: 20px;
  }
  section { padding: 52px 0; }
  .hero h1 { font-size: clamp(29px, 8.4vw, 38px); }
  .sec-head h2 { font-size: clamp(27px, 7.4vw, 34px); }
}
```

---

## 4. 深色模式

```css
[data-theme="dark"] {
  --brand: #3E8EFF;
  --brand-dark: #62A5FF;
  --brand-soft: rgba(62, 142, 255, 0.14);
  --bg: #060708;
  --bg-soft: rgba(255, 255, 255, 0.05);
  --line: rgba(255, 255, 255, 0.1);
  --text: #EDEFF3;
  --text2: #A2A8B3;
  --text3: #797F8B;
  --shadow: 0 2px 12px rgba(0, 0, 0, 0.35);
  --shadow-hover: 0 12px 34px rgba(62, 142, 255, 0.18);
  color-scheme: dark;
}
```

---

## 5. 浏览器兼容

```css
/* 毛玻璃效果 fallback */
@supports not (backdrop-filter: blur(14px)) {
  .card { background: rgba(255, 255, 255, 0.95); }
  [data-theme="dark"] .card { background: rgba(22, 24, 29, 0.95); }
}
```

---

## 6. 无障碍

```css
/* 焦点样式 */
:focus-visible {
  outline: 2px solid var(--brand);
  outline-offset: 2px;
}

/* 减少动效 */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```