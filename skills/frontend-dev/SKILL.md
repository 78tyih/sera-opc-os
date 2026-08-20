---
name: frontend-dev
purpose: 全栈前端开发：高级 UI 设计 + 电影级动画 + AI 生成媒体素材 + 说服力文案 + 视觉艺术。构建完整、生产级、视觉冲击力强的网页（落地页/营销站/产品页/仪表盘/生成艺术），真实媒体、高级动效、强文案。
inputs: 自然语言请求（如 "build a landing page for a music streaming app"）；页面类型；品牌信息；文案素材。
outputs: 完整网页项目（HTML/CSS/JS 或 React/Next.js 等框架工程，含本地生成的 image/video/audio 资产）、转化文案、生成艺术（PDF/PNG 或 p5.js HTML）。
workflow: |
  Phase 1 Design Architecture：分析请求→设设计参数(DESIGN_VARIANCE/MOTION_INTENSITY/VISUAL_DENSITY)→规划版块与素材需求
  Phase 2 Motion Architecture：按 Tool Selection Matrix 选动画工具；按性能护栏规划动效序列
  Phase 3 Asset Generation：解析素材需求→精写提示词(先给用户确认)→scripts/ 生成→保存本地 assets/（禁止占位图 URL）
  Phase 4 Copywriting：按 AIDA/PAS/FAB 框架写真实文案（禁止 Lorem ipsum）
  Phase 5 Build UI：脚手架 + 按 Design/Motion 规则构建各版块，集成素材与文案
  Phase 6 Quality Gates：终检清单（无占位 URL、全部素材本地、依赖已装、动效合规）
tools: Bash（npm/node、scripts/minimax_{tts,music,video,image}.py）, Write（代码）, Read（references/ 按需）
examples: |
  - /frontend-dev 建一个音乐流媒体 app 的落地页
  - npm install framer-motion gsap lottie-react three @react-three/fiber @react-three/drei
  - python3 scripts/minimax_image.py --prompt "..." --ratio 16:9 --output assets/images/hero.webp
iron_rules: |
  - 禁止占位图 URL（unsplash/picsum/placeholder 等），全部素材本地生成；禁止 Lorem ipsum
  - 只用 GPU 属性动画(transform/opacity/filter/clip-path)；NEVER 用 Inter；NEVER 混用 GSAP+Framer 于同一组件
  - 素材生成前必须向用户确认提示词；ANTI-EMOJI：用 Phosphor/Radix 图标
  - 尊重 prefers-reduced-motion；移动端禁用视差/3D
source: ~/.workbuddy/skills/frontend-dev/SKILL.md
---

# frontend-dev

## Purpose
全栈前端开发：高级 UI 设计 + 电影级动画 + AI 生成媒体素材 + 说服力文案 + 视觉艺术。构建完整、生产级、视觉冲击力强的网页（真实媒体、高级动效、强文案）。适用于落地页、营销站、产品页、仪表盘、生成艺术、电影级滚动动画等。

## Inputs
- 自然语言请求（如 "build a landing page for a music streaming app"）
- 页面类型与上下文；品牌信息；文案素材；媒体需求

## Outputs
- 完整网页项目（Pure HTML 或 React/Next.js / Vue / Svelte / Astro 工程）
- 本地生成的 image / video / audio 资产（`{type}-{descriptor}-{timestamp}.{ext}` 命名）
- 转化文案（AIDA/PAS/FAB 框架）；生成艺术（静态 PDF/PNG 或交互 p5.js HTML）

## Workflow（6 阶段）
```
Phase 1 Design Architecture — 分析请求 → 设设计参数 → 规划版块与素材需求
Phase 2 Motion Architecture  — 按 Tool Selection Matrix 选动画工具 → 规划动效（性能护栏）
Phase 3 Asset Generation     — 解析素材需求 → 精写提示词(先给用户确认) → scripts/ 生成 → 保存本地
Phase 4 Copywriting          — AIDA/PAS/FAB 写真实文案（禁止 Lorem ipsum）
Phase 5 Build UI             — 脚手架 + 构建各版块，集成素材与文案
Phase 6 Quality Gates        — 终检清单（无占位 URL / 素材全本地 / 依赖已装 / 动效合规）
```

## Tools
- Bash：`npm` / `node`；`scripts/minimax_tts.py` / `minimax_music.py` / `minimax_video.py` / `minimax_image.py`（需 `MINIMAX_API_KEY`）
- Write / Read：代码与 `references/`（motion-recipes、asset-prompt-guide、voice-catalog、troubleshooting 等按需读取）

## Examples
```bash
# 调用方式
/frontend-dev 建一个音乐流媒体 app 的落地页

# 依赖
npm install framer-motion gsap lottie-react three @react-three/fiber @react-three/drei

# 生成素材（先给用户确认提示词）
python3 scripts/minimax_image.py --prompt "cinematic hero shot..." --ratio 16:9 --output assets/images/hero.webp
```

## Iron Rules（强制，违反即阻断）
- **禁止占位图 URL**（unsplash、picsum、placeholder、placehold、lorem.space、dummyimage）；Phase 5 中所有 `<img>/<video>/<source>/background-image` 必须引用本地资产；交付前 grep 检查
- 素材生成提示词**必须先向用户确认**；图片提示词 NEVER 包含文字
- **只用 GPU 属性动画**：transform / opacity / filter / clip-path；NEVER 动画 width/height/top/left/margin/padding/font-size
- **NEVER 用 Inter**（用 Geist/Outfit/Satoshi）；NEVER 混用 GSAP + Framer Motion 于同一组件；重库（Lottie/GSAP/Three.js）必须懒加载
- **ANTI-EMOJI**：NEVER 用 emoji，用 Phosphor/Radix 图标
- 遵守 `prefers-reduced-motion`；移动端（pointer:coarse）禁用视差/3D；GSAP pin 在 <768px 禁用
- 每个含 GSAP/observer 的 `useEffect` 必须 `return () => ctx.revert()`
- 状态实现：Loading(skeleton) / Empty / Error / 触觉反馈(`scale-[0.98]`) 必须齐全

## Source
`~/.workbuddy/skills/frontend-dev/SKILL.md`
