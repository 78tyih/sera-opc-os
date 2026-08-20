# Sera Typography — 排版系统

> 版本：v1.0
> 来源：HTX OTC Landing
> 风格：Clean · Hierarchical · Premium

---

## 1. 字体栈

```css
/* 中英文混合 */
font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue",
  "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;

/* 纯英文 */
font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;

/* 等宽（数据、代码） */
font-family: Menlo, Monaco, "SF Mono", monospace;
```

---

## 2. 字号层级

| 层级 | 桌面 | 移动端 | 字重 | 行高 | 字距 |
|---|---|---|---|---|---|
| **Hero 标题** | clamp(44px, 6vw, 64px) | clamp(29px, 8.4vw, 38px) | 800 | 1.14 | -1.5px |
| **板块标题** | clamp(44px, 6vw, 64px) | clamp(27px, 7.4vw, 34px) | 800 | 1.14 | -1.2px |
| **卡片标题** | 17-19px | 15-16.5px | 700 | 1.4 | — |
| **正文** | 14-15px | 13-13.5px | 400 | 1.65 | — |
| **辅助文字** | 13-13.5px | 12-12.5px | 400 | 1.55 | — |
| **标签** | 12.5px | 11.5px | 700 | 1.2 | 2px |
| **按钮** | 14-16px | 13.5-15px | 700 | 1 | — |
| **风险提示** | 12px | 11px | 400 | 1.8 | — |
| **数据强调** | 13.5px | 12.5px | 700 | 1 | 0.5px |

---

## 3. 排版规则

### 3.1 标题系统
- **对比驱动**：主标题显著大于副标题，视觉跳跃明显
- 标题使用 font-weight 800（Extra Bold）
- 标题使用负 letter-spacing 提升紧凑感
- 板块标题与 Hero 标题同字号，保持一致性

### 3.2 标签系统
- 全部 UPPERCASE
- 固定 2px letter-spacing
- 使用品牌色或 text2 色
- 位于板块标题上方，作为语义前缀

### 3.3 正文系统
- 最大行宽 660px（保持可读性）
- 行高 1.65（舒适阅读）
- 不使用 justified 对齐

### 3.4 移动端适配
- 字号使用 clamp() 平滑缩放
- 保持标题层级对比关系
- 不缩小标签 letter-spacing

---

## 4. 视觉层级原则

### 4.1 页面层级（从高到低）
```
Hero 标题（64px 800）→ 板块标题（64px 800）
→ 卡片标题（19px 700）→ 正文（15px 400）
→ 辅助文字（13px 400）→ 风险提示（12px 400）
```

### 4.2 卡片层级
```
卡片标题（17-19px 700）
  ↓ 4px gap
卡片描述（14px 400 text2）
  ↓ 8-12px gap
CTA 文字（14px 700 brand）
```

### 4.3 Section 头部层级
```
标签（12.5px 700 uppercase 2px spacing）
  ↓ 14px gap
标题（44-64px 800 -1.2px spacing）
  ↓ 10px gap
副标题（15px 400 text2）
```

---

## 5. 预设组合

### 5.1 金融产品页面
```html
<!-- Hero -->
<h1 style="font-size:clamp(44px,6vw,64px);font-weight:800;letter-spacing:-1.5px;line-height:1.14">
  Value Proposition
</h1>
<p style="font-size:17px;color:var(--text2);max-width:660px">
  Description
</p>

<!-- Section Header -->
<div class="sec-head">
  <div class="sec-tag">LABEL</div>
  <h2>Section Title</h2>
  <p>Section Subtitle</p>
</div>

<!-- FAQ Question -->
<div class="faq-q" style="font-size:15.5px;font-weight:600">
  Question text
</div>

<!-- Risk Notice -->
<p style="font-size:12px;color:var(--text3);line-height:1.8">
  Risk disclaimer text
</p>
```

### 5.2 数据展示
```css
.data-value {
  font-size: 13.5px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
```