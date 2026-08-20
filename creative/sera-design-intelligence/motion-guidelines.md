# Sera Motion Guidelines — 动效指南

> 版本：v1.0
> 风格：Subtle · Smooth · Consistent · Purposeful

---

## 1. 核心缓动

```css
/* Sera Ease — 整个系统中唯一使用的缓动函数 */
--ease-sera: cubic-bezier(0.16, 1, 0.3, 1);
```

### 为什么是这个曲线？

```
起始快（0.16）：用户操作后立即得到反馈
结束缓（1, 0.3）：自然减速，不过度弹跳
```

不弹跳、不拖沓、不花哨。

---

## 2. 动效矩阵

| 场景 | 动效 | 时长 | 属性 | 触发 |
|---|---|---|---|---|
| **页面加载** | 从下往上浮现 | 0.72s | opacity + translateY | scroll |
| **卡片悬停** | 上移 + 阴影 | 0.3s | transform + box-shadow | hover |
| **按钮悬停** | 上移 + 阴影 | 0.25s | transform + box-shadow | hover |
| **CTA 箭头** | 向右滑出 | 0.3s | translateX | hover |
| **手风琴展开** | 高度过渡 | 0.35s | max-height | click |
| **更多内容展开** | 网格展开 + 滑入 | 0.5s | grid-rows + opacity | click |
| **弹窗出现** | 上滑 + 放大 | 0.35s | opacity + translateY + scale | click |
| **步骤切换** | 水平滑入 | 0.38-0.42s | translateX + opacity | click |
| **导航栏** | 阴影渐变 | 0.3s | box-shadow | scroll |
| **引导箭头** | 上下浮动 | 2.4s infinite | translateY | auto |

---

## 3. 动效实现

### 3.1 浮现 Reveal
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

### 3.2 卡片悬停
```css
.card {
  transition: all 0.3s var(--ease-sera);
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 32px rgba(0,82,255,.10);
  border-color: #0052FF;
}
```

### 3.3 手风琴展开
```css
.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.35s var(--ease-sera);
}
.accordion.open .accordion-content {
  max-height: 260px;
}
```

### 3.4 弹窗出现
```css
@keyframes modalIn {
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
  animation: modalIn 0.35s var(--ease-sera);
}
```

### 3.5 浮动引导
```css
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(9px); }
}
.scroll-hint {
  animation: float 2.4s ease-in-out infinite;
}
```

---

## 4. 动效原则

### 4.1 统一性
- 所有动效使用同一缓动函数
- 不混合 ease-in / ease-out / ease-in-out
- 不引入 bounce / spring 效果

### 4.2 克制性
- 悬停仅上移 3px + 阴影加深
- 不做夸张旋转、缩放、粒子效果
- 不做持续闪烁或脉冲动画
- 动效服务于功能，不分散注意力

### 4.3 自然性
- 浮现从下往上（符合阅读动线）
- 弹窗从下往上（符合物理层叠逻辑）
- 展开/折叠使用平滑过渡
- 进入方向与用户预期一致

### 4.4 性能
```css
/* ✅ 优先使用 GPU 加速属性 */
transform
opacity
filter

/* ❌ 避免触发 layout 的属性 */
left, top, width, height, margin
```

### 4.5 可访问性
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 5. 动效用例

### 5.1 Landing Page
| 元素 | 动效 | 时序 |
|---|---|---|
| 页面标题 | 浮现 | 页面加载后立即 |
| 卡片 | 浮现 | 滚动到视口时 |
| FAQ | 手风琴 | 用户点击时 |
| 弹窗 | 弹窗出现 | 用户点击触发时 |
| 引导箭头 | 浮动 | 持续 |

### 5.2 Dashboard
| 元素 | 动效 | 时序 |
|---|---|---|
| 进度条 | 宽度填充 | 页面加载时 |
| 倒计时 | 秒级刷新 | 持续 |
| 任务卡片 | 悬停 | 用户 hover 时 |
| 状态切换 | 颜色过渡 | 状态变化时 |

### 5.3 表单
| 元素 | 动效 | 时序 |
|---|---|---|
| 弹窗出现 | 弹窗出现 | 点击触发时 |
| 步骤切换 | 水平滑入 | 点击下一步/上一步 |
| 输入框聚焦 | 边框 + 阴影 | 用户聚焦时 |
| 校验错误 | 抖动 | 校验失败时 |
| 提交成功 | 图标出现 | 提交成功时 |