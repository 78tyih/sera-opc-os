---
name: propfirm-eagle-import
purpose: 把 AI 生成的媒体文件（mp4/mov/png/jpg/webp/wav/mp3）通过 Eagle 官方本地 Web API 自动导入 Mac 上的 Eagle「Sera 资源库」并写入 name/tags/annotation/folderId。脚本优先 V2 API（返回 item ID），失败回退 Legacy。
inputs: 媒体文件路径或 staging 目录（~/Movies/PropFirmTV_Eagle_Inbox/，支持子目录）；可选 --name/--tags/--annotation/--folder-id；可选 sidecar（<文件>.eagle.json / 目录级 metadata.json）。
outputs: Eagle item ID（<文件>.eagle.imported.json 回写 eagle_imported/eagle_item_id）；未运行时的 <文件>.eagle.pending.json；sweep 批量导入结果。
workflow: |
  1. 媒体文件落 staging（~/Movies/PropFirmTV_Eagle_Inbox/）或直接指定文件
  2. 二选一：直接 add（即时入库）或丢 staging + 写 sidecar 后统一 sweep
  3. 脚本调 Eagle 本地 API：优先 POST /api/v2/item/add（拿 item ID），失败回退 POST /api/item/addFromPath
  4. Eagle 4.0.0 落文件夹保底：导入成功后自动改写 item 磁盘 metadata.json 的 folders 数组（唯一可靠方式）
  5. 导入成功回写 .eagle.imported.json；Eagle 未运行写 .eagle.pending.json（下次 sweep 重试，不失败生成任务）
tools: Bash（python3 scripts/eagle_import.py）, Read, Write（sidecar/metadata.json）
examples: |
  - python3 scripts/eagle_import.py status
  - python3 scripts/eagle_import.py sweep --dry-run
  - python3 scripts/eagle_import.py add <mp4> --name "X · Y" --tags a,b --annotation "Z" --folder-id MQQ7NGJQOVG5P
iron_rules: |
  - Eagle 本地 API: http://localhost:41595；目标库「Sera 资源库」（物理路径 iCloud，只用于确认不作输出）
  - V2 无批量 add；addFromPaths 批量不返回 ID；无删除端点（删 item 只能 App 手动）
  - tags 始终含 propfirm.tv；脚本从不主动删源文件（仅 --clean 确认导入成功后才删）
  - Eagle 4.0.0 item/add 即便传 folderId 也会丢库根；唯一可靠落文件夹=改写磁盘 metadata.json，不要自己改导入流程
source: ~/.workbuddy/skills/propfirm-eagle-import/SKILL.md
---

# propfirm-eagle-import

## Purpose
把 AI 生成的媒体文件（mp4/mov/png/jpg/webp/wav/mp3）通过 Eagle 官方本地 Web API 自动导入 Mac 上的 Eagle「Sera 资源库」，并写入 name / tags / annotation / folderId。脚本优先 V2 API（直接返回 item ID），失败回退 Legacy。服务于 PropFirm.TV 素材归档等场景。

## Inputs
- 媒体文件路径，或 staging 目录（`~/Movies/PropFirmTV_Eagle_Inbox/`，支持子目录）
- 可选：`--name` / `--tags` / `--annotation` / `--folder-id`
- 可选 sidecar：`<文件>.eagle.json`（name/tags/annotation/folderId）；目录级 `metadata.json`（project/episode/scene/generator/model/topic/prompt/tags）

## Outputs
- Eagle item ID；结果 sidecar `<文件>.eagle.imported.json`（`eagle_imported:true, eagle_item_id, source_file, tags, imported_at`）
- Eagle 未运行时写 `<文件>.eagle.pending.json`（下次 sweep 重试，不失败生成任务）

## Workflow
```
1. 媒体文件落 staging（~/Movies/PropFirmTV_Eagle_Inbox/）或直接指定文件
2. 二选一：
   a) 直接调 add <file>（带 --name/--tags/--annotation/--folder-id）即时入库
   b) 丢 staging + 写 sidecar，随后统一跑 sweep
3. 脚本调 Eagle 本地 API：优先 POST /api/v2/item/add（返回 data.id），失败回退 POST /api/item/addFromPath
4. Eagle 4.0.0 落文件夹保底：导入成功后自动改写 item 磁盘 metadata.json 的 folders 数组
5. 回写 .eagle.imported.json / .eagle.pending.json
```

## Tools
- Bash：`python3 scripts/eagle_import.py status|sweep|pending|add`
- Read / Write：sidecar 与 metadata.json

## Examples
```bash
# 检查 Eagle 是否运行 / 资源库 / API
python3 scripts/eagle_import.py status

# 批量导入 staging 内所有未导入文件
python3 scripts/eagle_import.py sweep
python3 scripts/eagle_import.py sweep --dry-run
python3 scripts/eagle_import.py sweep --clean      # 导入成功后删源文件

# 列出待导入
python3 scripts/eagle_import.py pending

# 单文件即时入库
python3 scripts/eagle_import.py add <mp4> --name "Tradeify · HOME · Official Website · 5s" \
  --tags "PropFirm.TV,Official Website,5s" --annotation "..." --folder-id MQQ7NGJQOVG5P
```

## Iron Rules
- Eagle 本地 API：`http://localhost:41595`（Eagle 打开时自动启动）；目标库「Sera 资源库」（物理路径在 iCloud Drive，只用于确认、不作输出目录）
- **导入优先 V2**：`POST /api/v2/item/add` 直接拿 item ID；**Legacy 回退**：`POST /api/item/addFromPath`；`addFromPaths` 批量但**不返回 ID**；V2 无批量 add
- **无删除端点**（V2/legacy 均 404），删 item 只能进 App 手动操作
- **tags 始终含 `propfirm.tv`**，再按来源/语义追加
- 脚本从不主动删源文件（仅 `--clean` 在确认导入成功后才删）
- **Eagle 4.0.0 坑**：`item/add` 即便传 `folderId` 也会把 item 丢进库根；`moveToFolder` 404；唯一可靠落文件夹方式=直接改写 item 磁盘元数据 `metadata.json` 的 `folders` 数组。导入脚本已内置「磁盘保底」，**不要自己改导入流程**

## Source
`~/.workbuddy/skills/propfirm-eagle-import/SKILL.md`
