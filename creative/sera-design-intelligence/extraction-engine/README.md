# Extraction Engine

> V4.0 · 事实提取层
> 职责：回答 **“页面实际上用了什么？”**，不回答“为什么这么设计”。

## Boundary

```text
External Page
   ↓
Extraction Backend
   ↓
Raw Artefacts
   ↓
Sera Adapter
   ↓
Extraction Manifest
   ↓
DNA Engine / Analyst
```

Extraction Engine 的输出是 **evidence**，不是 Design Intelligence 的最终判断。

## Default Backend

默认：`designlang`

能力包括 rendered DOM / computed style、DTCG token、color / type / spacing / radius / shadow、component clustering、responsive、hover / focus / active、motion / keyframes、dark mode、accessibility / CSS health、multi-format emitters、MCP，以及后续 drift / visual diff 接口。

Upstream：`https://github.com/Manavarya09/design-extract`

## Preflight

```bash
node --version
npx -y designlang doctor
```

Node.js 版本与 upstream 当前要求保持一致；不要在 Sera 代码中锁死第三方版本号。

## Recommended Run

```bash
python3 adapter.py https://linear.app \
  --out ../case-studies/linear/raw/designlang
```

Adapter 会运行 preflight、完整 extraction、收集并哈希 artefacts、按稳定类别归类，然后写出 `normalized/extraction-manifest.json`。

## Authenticated Pages

只使用运行时参数：

```bash
--cookie-file /local/runtime/path/state.json
```

不把 cookie value 写进 manifest，不提交 cookie file，manifest 只记录 `authenticated: true`。

## Output Contract

见 `extraction-contract.schema.json`。上层系统只依赖 manifest，不依赖 Designlang 的具体输出文件名。

## Artifact Categories

`tokens` · `typography` · `components` · `motion` · `responsive` · `accessibility` · `brand` · `agent_rules` · `screenshots` · `platform` · `report` · `other`

分类只服务检索，不改写原始内容。

## MCP

```bash
npx -y designlang mcp --output-dir ./design-extract-output
```

MCP 适合交互式 Agent；批量归档仍以 `adapter.py + manifest` 为 canonical path。

## Fallback Backend

```text
sera-browser-automation
   ↓
DOM + CSS + screenshot
   ↓
manual artifact directory
   ↓
same extraction-manifest.json
```

Fallback 的目标是继续遵守同一个 Sera Contract。

## Non-goals

本层不负责审美评分、品牌策略、转化策略、Style Router、Design Direction、“应该抄什么”或自动把第三方素材用于生产。