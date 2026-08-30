# Extraction Engine

> V4.1 · 事实提取层
> 职责：回答 **“页面实际上用了什么？”**，不回答“为什么这么设计”。

## Boundary

```text
External Page / Existing Output
   ↓
Extraction Backend / Importer
   ↓
Raw or External Artefacts
   ↓
Sera Extraction Manifest
   ↓
DNA Engine / Analyst
```

Extraction Engine 的输出是 evidence，不是 Design Intelligence 的最终判断。

## Default Backend

默认：`designlang`。它负责 rendered DOM / computed style、DTCG tokens、type / spacing / radius / shadow、components、responsive、interaction、motion、dark mode、accessibility / CSS health、多格式 emitter、MCP 与 native multi-site measurement。

Upstream：`Manavarya09/design-extract`。

## Fresh Extraction

```bash
npx -y designlang doctor
python3 adapter.py https://linear.app \
  --out ../case-studies/linear/raw/designlang
```

`adapter.py` 会运行 preflight、调用 Designlang、保存 raw artefacts、哈希/分类，并写 `normalized/extraction-manifest.json`。

## Import Existing Output

MCP、CI、另一台机器或另一个 Agent 已经跑过 Designlang 时，不要重复抓取：

```bash
python3 import_existing.py \
  --source-dir ./design-extract-output \
  --url https://linear.app \
  --copy-to-raw ../case-studies/linear/raw/designlang \
  --manifest ../case-studies/linear/normalized/extraction-manifest.json \
  --backend-version 13.x \
  --source-repo your-org/evidence-repo \
  --source-commit <sha>
```

Importer 不访问网站，也不会自动声称 `--full/--dark/--responsive/--interactions` 已完成；只有显式声明才会写 `true`。未声明 `--complete` 时，Evidence 默认为 partial。

## Authenticated Pages

只使用运行时 `--cookie-file` / browser state。Cookie/token value 不进入 manifest，不提交 Git。

## Output Contract

见 `extraction-contract.schema.json`。上层系统只依赖 manifest，不依赖 Designlang 的具体文件命名。

Artifact categories：`tokens` · `typography` · `components` · `motion` · `responsive` · `accessibility` · `brand` · `agent_rules` · `screenshots` · `platform` · `report` · `other`。

## MCP

```bash
npx -y designlang mcp --output-dir ./design-extract-output
```

交互式 Agent 可用 MCP；需要进入长期 Memory 时仍先经过 `import_existing.py` / manifest。

## Fallback

```text
designlang fail
   ↓
sera-browser-automation
   ↓
DOM + CSS + screenshot
   ↓
same extraction-manifest contract
```

缺失事实保持 unknown/omitted，不让 LLM 补假值。

## Non-goals

本层不负责审美评分、品牌策略、转化策略、Style Router、Design Direction、“应该抄什么”或自动把第三方品牌资产用于生产。