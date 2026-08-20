# HTX OTC — Reproduction Prompt

> 用途：直接提供给 AI Agent（Claude Code / Codex / Trae / DeepSeek）生成类似风格的金融 Landing Page
> 风格：Sera FinTech Premium · Institutional Trust

---

## Prompt

```markdown
Create a premium fintech landing page inspired by the HTX OTC Desk style.

## Design Requirements

### Style
- Institutional trust feeling, premium financial services
- Clean white / light background with glass-morphism cards
- Dark mode support (independent color mapping, not inversion)
- Subtle, unified motion throughout
- Professional, restrained, not flashy

### Color Palette
- Primary brand: #0052FF (light mode) / #3E8EFF (dark mode)
- Background: #FFFFFF (light) / #060708 (dark)
- Card background: rgba(255,255,255,.62) with backdrop-filter:blur(14px) (light)
- Card background: rgba(22,24,29,.6) with backdrop-filter:blur(14px) (dark)
- Text primary: #14181F (light) / #EDEFF3 (dark)
- Text secondary: #5A6272 (light) / #A2A8B3 (dark)
- Border: #E8ECF2 (light) / rgba(255,255,255,.1) (dark)
- Shadows: 0 2px 12px rgba(20,30,60,.05) (default) / 0 10px 32px rgba(0,82,255,.10) (hover)

### Typography
- Font stack: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif
- Hero heading: clamp(44px, 6vw, 64px), font-weight 800, letter-spacing -1.5px
- Section heading: clamp(44px, 6vw, 64px), font-weight 800, letter-spacing -1.2px
- Card title: 17-19px, font-weight 700
- Body: 14-15px, font-weight 400
- Labels: 12.5px, font-weight 700, uppercase, letter-spacing 2px
- Risk notice: 12px minimum readable size

### Layout
- Content max-width: 1120px, centered
- Section padding: 84px desktop / 52px mobile
- Grid: 3-column for features, 2-column for FAQ/trust, 1-column auto on mobile
- Cards: 14px border-radius, 28px padding, glass-morphism background
- Card hover: translateY(-3px) + shadow-hover + brand border

### Page Structure
1. Hero: Large heading + supporting description + dual CTA cards + trust signal + scroll hint
2. Feature Section: 3-column card grid with icons
3. Trust / Compliance Section: 2-column cards with left brand border
4. FAQ: 2-column accordion with "more" expand
5. CTA Bar: Primary CTA button
6. Footer: Risk notice + copyright

### Components
- Feature cards: icon (44x44) + title + description + hover elevation
- FAQ: accordion with max-height transition, arrow rotation on open
- Trust signals: subtle badges showing KYC/compliance
- Scroll hint: glass button with float animation

### Motion
- All motion uses: cubic-bezier(0.16, 1, 0.3, 1) ("Sera Ease")
- Reveal animation: 0.72s, translateY(26px) + opacity 0→1, on scroll
- Card hover: 0.3s, translateY(-3px) + shadow + border color
- FAQ accordion: 0.35s max-height transition
- Modal: 0.35s, translateY(18px) + scale(0.97) → 1
- Scroll hint: 2.4s ease-in-out infinite float

### Copywriting Style
- Professional, restrained, clear
- No aggressive claims (no "guaranteed returns", "instant profit")
- Trust signals visible in first viewport
- Risk disclaimer at footer in 12px

### Conversion Pattern
- Dual CTA at hero (buy/sell direction choice)
- Progressive form (3 steps max, 3 fields per step)
- Escape hatch: "Contact us" alternative on every form
- FAQ intercept before final CTA
```

---

## 简化版 Prompt（快速生成）

```markdown
Create a fintech landing page with:
- Premium institutional trust feeling
- Glass-morphism cards, clean white/dark backgrounds
- Blue accent (#0052FF), large bold headings (64px max)
- 3-column feature grid, 2-column FAQ
- Subtle hover elevation on cards
- Smooth reveal animations (0.72s, ease-sera)
- KYC/trust signals visible in hero
- Dual CTA entrance (buy/sell direction)
- Dark mode with independent color mapping
```

---

## 适用 Agent

| Agent | 使用方式 |
|---|---|
| Claude Code | 直接粘贴 Prompt + 项目上下文 |
| Codex | 粘贴到 Codex，请求生成 HTML 页面 |
| Trae | 粘贴到 Trae，请求生成完整页面 |
| DeepSeek | 粘贴 Prompt，请求生成代码 |
| Cursor | 使用 Composer + 粘贴 Prompt |