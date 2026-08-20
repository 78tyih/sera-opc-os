# Sera Motion — 动效系统

> 版本：v1.0
> 来源：HTX OTC Landing
> 风格：Subtle · Smooth · Consistent

---

## 1. 核心缓动函数

```css
/* Sera Ease — 所有动效统一使用 */
--ease-sera: cubic-bezier(0.16, 1, 0.3, 1);
```

**特性**：
- 起始快（0.16）：迅速响应用户操作
- 结束缓（1, 0.3）：自然减速，不过度弹跳
- 适用于所有场景：悬停、展开、浮现、弹窗

---

## 2. 动效清单

### 2.1 浮现（Reveal）
```css
.reveal {
  opacity: 0;
  transform: translateY(26px) scale(0.98);
  transition: opacity 0.72s var(--ease-sera),
              transform 0.72s var(--ease-sera);
}
.reveal.in {
  opacity: 1;
  transform: none;
}
```
- 用途：页面滚动元素渐入
- 时长：0.72s
- 方式：从下往上 + 淡入 + 轻微缩放

### 2.2 卡片悬停
```css
.card {
  transition: all 0.3s var(--ease-sera);
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
  border-color: var(--brand);
}
```
- 用途：卡片、按钮、FAQ 条目的悬停反馈
- 时长：0.3s
- 方式：上移 3px + 阴影加深 + 边框变色

### 2.3 CTA 箭头
```css
.arrow-icon {
  transition: transform 0.3s var(--ease-sera);
}
.card:hover .arrow-icon {
  transform: translateX(4px);
}
```
- 用途：CTA 箭头向右滑出
- 时长：0.3s

### 2.4 手风琴展开
```css
.faq-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.35s var(--ease-sera);
}
.faq-item.open .faq-content {
  max-height: 260px;
}
```
- 用途：FAQ 展开/折叠
- 时长：0.35s
- 方式：max-height transition（不依赖 JS）

### 2.5 更多展开
```css
.more-expand {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.5s var(--ease-sera);
}
.more-expand-inner {
  overflow: hidden; min-height: 0;
  opacity: 0; transform: translateY(-8px);
  transition: opacity 0.4s 0.06s var(--ease-sera),
              transform 0.45s 0.06s var(--ease-sera);
}
.more.open .more-expand {
  grid-template-rows: 1fr;
}
.more.open .more-expand-inner {
  opacity: 1; transform: none;
}
```
- 用途：FAQ 更多信息展开
- 时长：0.5s（grid）+ 0.4s（opacity）
- 方式：grid-rows 0fr→1fr + 内容滑入

### 2.6 下滑引导
```css
@keyframes hintFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(9px); }
}
.scroll-hint {
  animation: hintFloat 2.4s ease-in-out infinite;
}
```
- 用途：首屏下滑引导按钮
- 时长：2.4s infinite
- 方式：上下浮动 9px

### 2.7 弹窗出现
```css
@keyframes fzPop {
  from {
    opacity: 0;
    transform: translateY(18px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: none;
  }
}
.modal {
  animation: fzPop 0.35s var(--ease-sera);
}
```
- 用途：表单弹窗出现
- 时长：0.35s
- 方式：上滑 + 淡入 + 轻微放大

### 2.8 步骤滑入
```css
@keyframes stepInFwd {
  from { transform: translateX(-100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
@keyframes stepInBck {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
```
- 用途：多步骤表单切换
- 时长：0.38-0.42s
- 方式：前进向左滑入，后退向右滑入

### 2.9 导航栏阴影
```css
.nav {
  transition: box-shadow 0.3s, background 0.3s;
}
header.scrolled .nav {
  box-shadow: 0 10px 34px rgba(20,30,60,.12);
}
```
- 用途：滚动时导航栏阴影加深
- 时长：0.3s

---

## 3. 动效设计原则

### 3.1 统一性
- **所有动效使用同一缓动函数**（cubic-bezier(.16, 1, .3, 1)）
- 不混合使用 ease-in / ease-out / ease-in-out
- 不引入 bounce / spring 效果

### 3.2 克制性
- 悬停动效仅做上移 + 阴影 + 边框变色
- 不做夸张旋转、缩放、粒子效果
- 不做持续闪烁或脉冲动画

### 3.3 自然性
- 浮现从下往上 + 淡入（符合自然的阅读动线）
- 弹窗从下往上（符合物理世界的层叠逻辑）
- 展开/折叠使用平滑过渡

### 3.4 可访问性
- 使用 `prefers-reduced-motion` 时禁用动画
- 不依赖 JS 驱动动画（CSS 优先）
- 动画时长不超过 0.72s（避免等待感）

---

## 4. 动效性能

```css
/* 所有动效使用 GPU 加速属性 */
transform  /* ✅ GPU 加速 */
opacity    /* ✅ GPU 加速 */
filter     /* ✅ GPU 加速 */

/* 避免 layout 触发的属性 */
left       /* ❌ 触发 layout */
top        /* ❌ 触发 layout */
width      /* ❌ 触发 layout */
height     /* ❌ 触发 layout */
margin     /* ❌ 触发 layout */
```