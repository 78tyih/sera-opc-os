---
name: figma-review
version: 1.0.0
author: Sera
category: creative
status: active
compatible:
  - WorkBuddy
  - Codex
  - Trae
  - Claude-Code
  - Cursor
---

# figma-review

## Purpose
设计稿审查 Skill：对 UI / 海报 / 品牌 / 网页设计稿进行系统化质量审查——视觉层级、品牌一致性、布局规范、可交付性。作为 design-agent 的质量门禁。

## When to use
- 「审查这个设计稿」
- 「检查这版 UI 是否符合品牌规范」
- 「这个海报的视觉层级对不对」
- 「设计稿可以交付了吗」（QC 检查）

## Inputs
- 设计稿（图片 / Ardot 画布 / Figma 链接 / HTML）
- 品牌规范（色板 / 字体 / 间距 / Design Token）
- 审查维度偏好（默认全维度）

## Outputs
- 结构化审查报告：逐维度通过/问题 + 具体修复建议
- 总评：`pass` / `needs_work`（含优先级排序的修改清单）

## Workflow
```
1. 读设计稿 + 品牌规范（Design Token / 色板 / 字体）
2. 逐维度检查：
   a. 视觉层级：主次分明？焦点清晰？信息密度合理？
   b. 品牌一致性：用色/字体/间距符合规范？无撞色无越界？
   c. 布局规范：对齐/栅格/留白正确？响应式考虑？
   d. 可交付性：资源齐备？切图/导出就绪？文案无占位？
3. 输出审查报告（pass / needs_work + 修复清单）
4. needs_work → 回写设计 Agent 修复（一次定向修正，不循环）
```

## 审查维度
| 维度 | 检查项 |
|---|---|
| 视觉层级 | 主标题→副标题→正文递减；对比度足够；焦点元素唯一 |
| 品牌一致性 | 颜色取自规范色板（≤1 accent）；字体匹配；间距用 Token |
| 布局规范 | 对齐到栅格；留白节奏一致；无元素重叠/溢出 |
| 可交付性 | 无占位符（Lorem/unsplash）；资源本地化；响应式断点覆盖 |
| 动效合规 | GPU 属性动画；prefers-reduced-motion 尊重（含动效时） |

## Dependencies
- `sera-design-studio`（产出方，审查对象来源）
- 品牌规范（色板/字体/Token，design-agent 知识）

## Examples
- 「审查 agents/design-agent 出的这版落地页」→ 输出逐维度报告
- 「这版海报品牌色用对了吗」→ 对照规范色板检查
