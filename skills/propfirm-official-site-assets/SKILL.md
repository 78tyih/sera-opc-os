---
name: propfirm-official-site-assets
purpose: PropFirm.TV 考试盘官网素材工厂——完整 pipeline：capture 官网真实界面（滚动+交互态）→ 提取事实/品牌色 → HyperFrames 编排 5s 无声 B-roll（HOME/ACCOUNT/RULES/FUNDED/PAYOUT 五件套，每条一种交互语言）→ lint/check → draft render → 导入 Eagle。
inputs: 目标考试盘官网 URL；firm key（lucid/tradeify/takeprofittrader/fundednext/fff/apex/tradeday/blue-guardian/topstep 之一）；已采集的截图（capture-home/interactions）；FACTS/overlay/DESIGN 数据文件。
outputs: 每家 5 条 5s 无声 1080p30 B-roll mp4（PFTV_<DisplayName>_<MODULE>_5s_v<NNN>.mp4）、lint/check 报告、Eagle 导入结果（.eagle.imported.json）、manifest.json 更新。
workflow: |
  1. 环境准备：export PATH/NODE_PATH/HYPERFRAMES_SKIP_SKILLS；BU_CDP_URL（如需交互 capture）
  2. Step1 基础 capture：npx hyperframes capture "<url>" -o capture-home --skip-vision --json（滚动截图+visible-text+tokens）
  3. Step2 交互态 capture：常驻无头 Chrome（run_in_background）+ browser-use < scripts/interaction_capture.py（tab 切换/FAQ/客服/footer/CTA hover）
  4. Step3 事实提取：visible-text.txt → content/<firm>/FACTS.md（16 字段，只写文本真实出现）+ overlay.json
  5. Step4 品牌色：tokens.json colors 按 HSV 选 overlay_accent → DESIGN.md
  6. Step5 生成 5 条 composition：写 configs/<firm>.json → 拷素材 → python3 scripts/gen_comps.py <firm>
  7. Step6 门禁：npx hyperframes lint .（0 errors）+ npx hyperframes check .（pass）
  8. Step7 Render：npx hyperframes render . -c compositions/<module>.html -q draft -f 30 -o renders/...
  9. Step8 抽帧核对：ffmpeg 抽帧 + Read 看图（overlay 不遮核心/无弹窗污染/无黑帧）
  10. Step9 Eagle 导入：python3 ~/.workbuddy/skills/propfirm-eagle-import/scripts/eagle_import.py add <mp4> --name ... --tags ... --annotation ... --folder-id <folderId>
  11. Step10 回写 manifest + 更新 memory + present_files 给用户
tools: Bash（npx hyperframes / ffmpeg / python3 / browser-use CDP）, Read（看截图与文本）, Write（FACTS/overlay/DESIGN/configs）
examples: |
  - npx hyperframes capture "https://www.topstep.com" -o capture-home --skip-vision --json
  - FIRM=topstep URL=https://www.topstep.com browser-use < scripts/interaction_capture.py
  - python3 scripts/gen_comps.py tradeify && cd hyperframes/tradeify/tradeify-official && npx hyperframes lint . && npx hyperframes check .
  - npx hyperframes render . -c compositions/HOME.html -q draft -f 30 -o renders/PFTV_Tradeify_HOME_5s_v001.mp4
iron_rules: |
  - 用户硬规范：素材 5s；一镜头 1-3 个画面变动；overlay_accent 跟随官网品牌色（不用 PFTV 蓝）；每条一种交互语言 5 条互不重复；overlay 数字只能来自官网 capture 文本（未确认标 UNVERIFIED）；全部无声 1080p30
  - 固定 9 家名单不可替换；未来新网站同一流水线（firm key 换成新名）
  - 促销信息（折扣码等时效性）只允许出现在官网画面里，不写进 Overlay 文字
  - Cloudflare 拦的站（lucid/apex）需用户配合真实 Chrome 授权，被拦在 manifest 记 capture_status.blocked，不伪造
source: ~/.workbuddy/skills/propfirm-official-site-assets/SKILL.md
---

# propfirm-official-site-assets

## Purpose
PropFirm.TV 考试盘官网素材工厂：把考试盘（futures prop firm）官网真实界面做成短视频 B-roll 素材库。完整 pipeline：capture 官网真实界面（滚动+交互态）→ 提取事实/品牌色 → HyperFrames 编排 5s 无声 B-roll（HOME/ACCOUNT/RULES/FUNDED/PAYOUT 五件套）→ lint/check → draft render → 导入 Eagle。本 skill 是自包含交接手册。

## Inputs
- 目标考试盘官网 URL；firm key（9 家固定名单之一）
- 已采集截图（`sources/<firm>/capture-home/`、`interactions/`）
- `content/<firm>/FACTS.md`、`overlay.json`、`design/<firm>/DESIGN.md`

## Outputs
- 每家 5 条 5s 无声 B-roll mp4（`renders/<firm>/PFTV_<DisplayName>_<MODULE>_5s_v<NNN>.mp4`）
- lint / check 报告（0 error + pass）
- Eagle 导入结果（`.eagle.imported.json`，含 eagle_item_id）
- `manifest.json` 全库清单更新

## Workflow（逐家 10 步）
```
BASE=~/projects/propfirm-tv-video-factory/official-sites

Step 1  基础 capture：npx hyperframes capture "<url>" -o capture-home --skip-vision --json
Step 2  交互态 capture：常驻无头 Chrome(run_in_background) + FIRM=<firm> URL=<url> browser-use < scripts/interaction_capture.py
Step 3  事实提取：visible-text.txt → FACTS.md（16 字段，铁律=只写文本真实出现）+ overlay.json
Step 4  品牌色：tokens.json colors 按 HSV 选 overlay_accent → DESIGN.md
Step 5  生成 5 条 composition：scripts/configs/<firm>.json → 拷素材 → python3 scripts/gen_comps.py <firm>
Step 6  门禁：npx hyperframes lint .（0 errors）+ npx hyperframes check .（pass）
Step 7  Render：npx hyperframes render . -c compositions/<module>.html -q draft -f 30 -o renders/...
Step 8  抽帧核对：ffmpeg 抽帧 + Read 看图
Step 9  Eagle 导入：python3 ~/.workbuddy/skills/propfirm-eagle-import/scripts/eagle_import.py add <mp4> ...
Step 10 回写 manifest + 更新 memory + present_files
```

**五件套交互语言映射**（每条一种，避免同质）：
| 模块 | 交互语言 |
|---|---|
| HOME | 滑动展示（4 屏 smooth scroll） |
| ACCOUNT | 左右点击（有 Tab 时实点切换）或滑动（无 Tab 站） |
| RULES | 信息提取（双规则卡逐行展开） |
| FUNDED | 浮动展示（步骤卡蛇形浮入） |
| PAYOUT | 横向平移（数字横移扫卡+见证墙） |

## Tools
- Bash：`npx hyperframes`（capture/lint/check/render）、`ffmpeg`、`python3`（gen_comps.py、eagle_import.py）、`browser-use`（CDP 版）
- Read：看截图 / visible-text.txt / contact-sheet
- Write：FACTS.md / overlay.json / DESIGN.md / scripts/configs/<firm>.json

## Examples
```bash
# 环境
export PATH="/Users/a1234/.workbuddy/binaries/node/versions/22.22.2/bin:$PATH"
export NODE_PATH=/Users/a1234/.workbuddy/binaries/node/workspace/node_modules
export HYPERFRAMES_SKIP_SKILLS=1

# Step 1
cd $BASE/sources/topstep && npx hyperframes capture "https://www.topstep.com" -o capture-home --skip-vision --json

# Step 7
cd $BASE/hyperframes/tradeify/tradeify-official
npx hyperframes render . -c compositions/HOME.html -q draft -f 30 -o $BASE/renders/PFTV_Tradeify_HOME_5s_v001.mp4

# Step 9
python3 ~/.workbuddy/skills/propfirm-eagle-import/scripts/eagle_import.py add <mp4> \
  --name "Tradeify · HOME · Official Website · 5s" --tags "PropFirm.TV,Official Website,5s" --folder-id MSXQ224S3OIBH
```

## Iron Rules
- **用户硬规范（2026-08-18 定稿）**：素材 ~5s；一镜头只承载 1–3 个画面变动；Overlay 强调色跟随官网品牌色（`overlay_accent`，不用 PFTV 蓝）；每条素材一种交互语言 5 条互不重复；Overlay 数字只能来自官网 capture 文本（未确认标 UNVERIFIED 或留空）；全部无声 1080p30
- 固定 9 家名单（用户人工定义，不可替换）：lucid / tradeify / takeprofittrader / fundednext / fff / apex / tradeday / blue-guardian / topstep
- 促销信息（折扣码等有时效性）只允许出现在官网画面里，不写进 Overlay 文字
- Cloudflare 拦的站（lucid/apex）需真实 Chrome 授权；被拦在 manifest 记 `capture_status.blocked`，不伪造
- Composition 资源路径必须根相对（`assets/shots/x.png`）；避免同一属性同一时间两个 tween
- 营销弹窗/横幅污染过的截图一律重拍干净版（污染会进视频）

## Source
`~/.workbuddy/skills/propfirm-official-site-assets/SKILL.md`
