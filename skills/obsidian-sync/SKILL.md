---
name: obsidian-sync
purpose: 把 WorkBuddy 生成的内容产物自动归档到 Obsidian Vault（Sera）的 03_AI_Reports/WorkBuddy_Output，自动分类、SHA256 去重、版本化、Front Matter 增强、更新 index 与日志。
inputs: 任务产出的文件（md/docx/pdf/txt/html/json/png/jpg/jpeg/gif/webp/mp4/mov/wav/mp3）或产物目录；可选 --category 强制分类。
outputs: 归档到 Obsidian 的产物文件（含增强 Front Matter）、自动重建的 index.md、追加的 WorkBuddy_sync.log、去重/版本化结果。
workflow: |
  1. 任务产出文件 → 先 present_files 给用户
  2. 调用同步脚本：python3 /Users/a1234/.workbuddy/obsidian-sync/workbuddy_obsidian_sync.py --source <产物目录>（或逐个文件）
  3. 向用户报告：同步数量、分类结果、跳过/版本化情况
  （可选）--category <分类> 强制分类；--dry-run 试运行；--index-only 仅重建 index；--list-categories 查看分类规则
tools: Bash（python3 脚本调用）, Read
examples: |
  - python3 ~/.workbuddy/obsidian-sync/workbuddy_obsidian_sync.py --source ./output
  - python3 ~/.workbuddy/obsidian-sync/workbuddy_obsidian_sync.py --source report.md --category Reports
iron_rules: |
  - 脚本只读源、只写归档根，绝不删除任何文件
  - 去重：SHA256 已在 manifest → Already exists 跳过
  - 版本化：同名不同内容 → xxx_v2_YYYYMMDD.ext，绝不覆盖
  - 分类目录：Reports / Research / Product_Documents / Architecture / Strategy / Meeting / Archive
source: ~/.workbuddy/skills/obsidian-sync/SKILL.md
---

# obsidian-sync

## Purpose
把 WorkBuddy 完成任务后产出的文件自动归档到用户 Obsidian 知识库（Sera Vault）的 `03_AI_Reports/WorkBuddy_Output/`，作为 AI 知识生产节点。只做「归档层」，不侵入模型调用 / 任务执行 / 输出格式。

## Inputs
- 任务产出文件或产物目录（支持的扩展名：`.md .docx .pdf .txt .html .json .png .jpg .jpeg .gif .webp .mp4 .mov .wav .mp3`）
- 可选 `--category` 强制指定分类（自动分类不准时）

## Outputs
- 归档后的文件（MD 自动增强 Front Matter：source/type/created/category/project/tags）
- 每次同步后自动重建的 `index.md`（按分类生成 `[[wikilink]]`）
- 追加的 `WorkBuddy_sync.log`
- 去重（`Already exists` 跳过）/ 版本化（`xxx_v2_YYYYMMDD.ext`）结果

## Workflow
```
1. 任务产出文件 → 先 present_files 给用户
2. 调用脚本：python3 ~/.workbuddy/obsidian-sync/workbuddy_obsidian_sync.py --source <产物目录>
3. 向用户报告：同步数量、分类结果、跳过/版本化情况（脚本输出即结果）
```

## Tools
- Bash（`python3 <脚本> --source ...`）
- Read（查看脚本输出与归档结果）

## Examples
```bash
# 同步整个产物目录（任务完成后的标准动作）
python3 ~/.workbuddy/obsidian-sync/workbuddy_obsidian_sync.py --source <产物目录>

# 同步单个文件
python3 ~/.workbuddy/obsidian-sync/workbuddy_obsidian_sync.py --source "<文件路径>"

# 强制指定分类
python3 ... --source <目录> --category Architecture

# 试运行 / 仅重建 index / 查看分类规则
python3 ... --source <目录> --dry-run
python3 ... --index-only
python3 ... --list-categories
```

## Iron Rules
- 脚本只读源、只写归档根，**绝不删除任何文件**
- SHA256 已在 manifest → 跳过；同名不同内容 → `_v2_YYYYMMDD.ext` 版本化，绝不覆盖
- 项目识别写入 Front Matter `project:`：`PropFirm.TV / TradeSpan / HTX OTC / Panda AI / SeraOS`
- 若其它 AI 工具（Trae 等）也归档到此目录，hash 去重天然防重复

## Source
`~/.workbuddy/skills/obsidian-sync/SKILL.md`
