---
name: browser-use
purpose: 浏览器自动化：导航、点击、输入、滚动、截图、数据提取、多标签、多会话、云浏览器。常驻 daemon 保持浏览器跨命令开启（~50ms 延迟）。
inputs: 浏览器操作意图（打开 URL/点击/输入/滚动/截图/提取）；目标网页地址；元素索引（来自 state）。
outputs: 页面状态（URL/标题/可点击元素索引）、截图（PNG/base64/全页）、交互结果、提取的数据。
workflow: |
  1. 前置：browser-use doctor 验证安装
  2. 模式选择：open（默认无头）→ connect（用户 Chrome，保留登录）→ cloud connect（云浏览器）→ --profile（指定 Chrome profile）
  3. Navigate：browser-use open <url>
  4. Inspect：browser-use state（拿可点击元素索引）
  5. Interact：browser-use click <index> / input <index> "text" / type / keys / select / upload / hover ...
  6. Verify：每次交互后 browser-use state 或 screenshot 确认
  7. 失败时 browser-use close 清会话后重试
tools: Bash（browser-use CLI）
examples: |
  - browser-use open https://example.com
  - browser-use state
  - browser-use click 5
  - browser-use input 3 "user@example.com"
  - browser-use screenshot /tmp/page.png --full
iron_rules: |
  - 所有浏览器交互必须走 browser-use CLI；禁止伪造 URL/标题/元素文本，务必用 state/screenshot 验证
  - 禁止生成 Chrome 扩展/Tampermonkey/Selenium/Puppeteer 代码绕过
  - 每次交互后立即验证再继续下一步
source: ~/.workbuddy/skills/browser-use/SKILL.md
---

# browser-use

## Purpose
浏览器自动化：导航、点击、输入、滚动、截图、数据提取、多标签、多会话、云浏览器。`browser-use` 常驻 daemon 保持浏览器跨命令开启，约 50ms 延迟/调用。用于网页测试、表单填充、截图、数据提取。

## Inputs
- 浏览器操作意图（打开 URL / 点击 / 输入 / 滚动 / 截图 / 提取数据）
- 目标网页地址；元素索引（来自 `browser-use state`）

## Outputs
- 页面状态（URL、标题、可点击元素索引）
- 截图（指定路径 PNG / base64 / `--full` 全页）
- 交互结果（点击 / 输入 / 选择 / 上传等）
- 提取的数据

## Workflow
```
1. 前置：browser-use doctor（验证安装）
2. 模式选择：
   open <url>                       # 默认：无头 Chromium
   --headed open <url>              # 可见窗口（调试）
   connect                          # 连接用户 Chrome（保留登录/cookies）
   cloud connect                    # 云浏览器（零配置，需 API key）
   --profile "Default" open <url>   # 指定 Chrome profile
3. Navigate：browser-use open <url>
4. Inspect：browser-use state（返回可点击元素索引）
5. Interact：click/input/type/keys/select/upload/hover/dblclick/rightclick/scroll/tab
6. Verify：每次交互后 state 或 screenshot 确认
7. 失败：browser-use close 清断会话后重试
```

## Tools
- Bash：`browser-use` CLI（open/back/scroll/tab/state/screenshot/click/type/input/keys/select/upload/hover/dblclick/rightclick/connect/cloud/profile/doctor/close）

## Examples
```bash
# 导航 + 检查
browser-use open https://example.com
browser-use state                 # URL, title, 可点击元素索引

# 交互（用 state 返回的索引）
browser-use click 5
browser-use input 3 "user@example.com"
browser-use keys "Enter"

# 截图
browser-use screenshot /tmp/page.png
browser-use screenshot /tmp/full.png --full

# 连接用户 Chrome（保留登录态）
browser-use connect
```

## Iron Rules
- 所有浏览器交互必须通过 `browser-use` CLI 执行；**禁止伪造 URL、页面标题或元素文本**——用 `state` / `screenshot` 验证
- **禁止**生成 Chrome 扩展、Tampermonkey 脚本、Selenium 或 Puppeteer 代码作为绕过方案
- **每次交互后立即验证**（`state` 或 `screenshot`）再执行下一步
- `connect` 找不到调试 Chrome 时给用户两个选项：启用真实 Chrome 远程调试，或用托管 Chromium + 其 Chrome profile

## Source
`~/.workbuddy/skills/browser-use/SKILL.md`
