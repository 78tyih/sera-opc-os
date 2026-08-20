---
name: sera-macos-ui
purpose: 完整 macOS UI 自动化 CLI（Peekaboo）：捕获/检查屏幕、定位 UI 元素、驱动输入、管理应用/窗口/菜单。
inputs: macOS UI 操作意图（截图/读取 UI 元素/点击/输入/拖拽/快捷键/管理 app/window/menu）；目标定位参数（--app/--pid/--window-title/--on/--coords）。
outputs: 屏幕截图（含 --annotate 标注）、UI 元素快照（元素 ID）、输入/点击/热键执行结果、应用/窗口/菜单操作结果。
workflow: |
  1. 前置：peekaboo permissions（确保屏幕录制+辅助功能权限）
  2. 定位目标：peekaboo see --annotate（拿元素 ID，如 B1/B3）或 list apps --json
  3. 交互：click --on B1 / type "text" --return / hotkey --keys "cmd,shift,t" 等
  4. 验证：再 see --annotate 确认结果
tools: Bash（peekaboo CLI）
examples: |
  - peekaboo permissions
  - peekaboo list apps --json
  - peekaboo see --app Safari --annotate --path /tmp/see.png
  - peekaboo click --on B3 --app Safari
  - peekaboo type "user@example.com" --app Safari
  - peekaboo menu click --app Safari --item "New Window"
iron_rules: |
  - 需要屏幕录制 + 辅助功能权限
  - 点击前先用 peekaboo see --annotate 识别目标
source: ~/.workbuddy/skills/peekaboo/SKILL.md
---

# peekaboo

## Purpose
完整 macOS UI 自动化 CLI：捕获 / 检查屏幕、定位 UI 元素、驱动输入、管理应用 / 窗口 / 菜单。用于 macOS 界面自动化、UI 测试、截图。

## Inputs
- macOS UI 操作意图：截图（capture/see/image）、元素定位（list/learn）、输入驱动（click/type/press/hotkey/drag/scroll/swipe/paste/move）、系统管理（app/window/menu/dock/space/clipboard/dialog）
- 目标定位参数：`--app` / `--pid` / `--window-title` / `--window-id` / `--window-index` / `--on` / `--id` / `--coords x,y` / `--snapshot`

## Outputs
- 屏幕截图（`--annotate` 标注元素 ID，`--path` 指定输出）
- UI 元素快照（`see` 返回可交互元素 ID）
- 输入 / 点击 / 热键执行结果；应用 / 窗口 / 菜单操作结果

## Workflow
```
1. 前置：peekaboo permissions（屏幕录制 + 辅助功能权限）
2. 定位目标：peekaboo see --annotate（拿元素 ID）或 peekaboo list apps --json
3. 交互：peekaboo click --on B1 / peekaboo type "Hello" --return / peekaboo hotkey --keys "cmd,shift,t"
4. 验证：再 peekaboo see --annotate 确认结果
```

## Tools
- Bash：`peekaboo` CLI
  - Core：bridge / capture / clean / config / image / learn / list / permissions / run / sleep / tools
  - Interaction：click / drag / hotkey / move / paste / press / scroll / swipe / type
  - System：app / clipboard / dialog / dock / menu / menubar / open / space / window
  - Vision：see

## Examples
```bash
# 快速上手
peekaboo permissions
peekaboo list apps --json
peekaboo see --annotate --path /tmp/peekaboo-see.png
peekaboo click --on B1
peekaboo type "Hello" --return

# 定位到具体 app
peekaboo see --app Safari --annotate --path /tmp/see.png
peekaboo click --on B3 --app Safari
peekaboo type "user@example.com" --app Safari

# 截图
peekaboo image --mode screen --screen-index 0 --retina --path /tmp/screen.png

# 应用/菜单操作
peekaboo app launch "Safari" --open https://example.com
peekaboo menu click --app Safari --item "New Window"
peekaboo hotkey --keys "cmd,shift,t"
```

## Iron Rules
- 需要**屏幕录制 + 辅助功能**权限（`peekaboo permissions` 检查）
- 点击 / 输入前先用 `peekaboo see --annotate` 识别目标（拿元素 ID），不要盲操作

## Source
`~/.workbuddy/skills/peekaboo/SKILL.md`
