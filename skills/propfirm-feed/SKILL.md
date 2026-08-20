---
name: propfirm-feed
purpose: PropFirm.TV Intelligence 用户资讯推送管线。采集原始情报入库 → 白名单过滤/优惠门禁/内部情报隔离/分类 → 中文格式化 → 推送企业微信。
inputs: JSON 原始情报文件（爬虫/手工采集）；config/settings.json（webhook、dry_run、白名单类别、排除关键词、firms 列表）。
outputs: raw_intel 入库记录 → feed_items（过滤/门禁/隔离/分类后）→ 企业微信 webhook 推送（受 dry_run 控制）。
workflow: |
  1. cd /Users/a1234/WorkBuddy/2026-08-17-03-48-26/propfirm-feed
  2. $PY main.py init            # 初始化数据库 + 登记 firms
  3. $PY main.py ingest <json>   # 导入 JSON 原始情报到 raw_intel
  4. $PY main.py process         # 处理 raw 情报 → feed_items（过滤/门禁/隔离/分类）
  5. $PY main.py publish         # 推送待发 feed_items 到企业微信（受 dry_run 控制）
  6. 或一键：$PY main.py run <json_path>
tools: Bash（python3）, Read, Write（编辑 settings.json）
examples: |
  - $PY main.py run samples/offers.json   # 一键跑全管线
  - $PY main.py ingest intel.json && $PY main.py process && $PY main.py publish
  - $PY samples/seed_demo.py              # 插入演示 offers（验证门禁用）
iron_rules: |
  - 白名单类别：RULE/PRODUCT/PAYOUT/PLATFORM/ACCOUNT/RISK/审核过的 DEAL
  - 优惠门禁：DEAL 必须 our_code_verified && our_price_verified && promotion_active 三关全过
  - 内部情报隔离：绝不展示竞品 Affiliate/Creator/Referral Code、市场底价、佣金、商务条件等；用户端只展示 PropFirm.TV 自己的 code 和 referral url
  - Severity 仅 INFO/IMPORTANT/WARNING/CRITICAL；Actionability 仅 ACTION_REQUIRED/CHECK_REQUIRED/AWARENESS
  - 微信推送默认 dry_run=true；确认无误后把 settings.json 的 dry_run 改为 false 才真发
source: ~/.workbuddy/skills/propfirm-feed/SKILL.md
---

# propfirm-feed

## Purpose
PropFirm.TV Intelligence 用户资讯推送管线：面向 PropFirm.TV 普通交易员用户的企业微信资讯推送。采集原始情报入库 → 白名单过滤 / 优惠门禁 / 内部情报隔离 / 分类 → 中文格式化 → 推送企业微信。

## Inputs
- JSON 原始情报文件（`ingest <json_path>`；爬虫/手工采集的原始数据）
- `config/settings.json`：webhook、dry_run、白名单类别、排除关键词、firms 列表

## Outputs
- `raw_intel` 表：原始情报入库
- `feed_items` 表：过滤 / 门禁 / 隔离 / 分类后的待发条目
- 企业微信 webhook 推送（受 `dry_run` 控制，默认只预览不真发）

## Workflow
```
项目根：/Users/a1234/WorkBuddy/2026-08-17-03-48-26/propfirm-feed/
PY=/Users/a1234/.workbuddy/binaries/python/versions/3.13.12/bin/python3

$PY main.py init                    # 初始化数据库 + 登记 firms
$PY main.py ingest <json_path>      # 导入 JSON 原始情报到 raw_intel
$PY main.py process                 # 处理 raw 情报 → feed_items
$PY main.py publish                 # 推送待发 feed_items 到企业微信（受 dry_run 控制）
$PY main.py run <json_path>         # 一键：init + ingest + process + publish
$PY samples/seed_demo.py            # 插入演示 offers（验证门禁用）
```

数据流：`Collector(采集) → raw_intel 表 → Pipeline(过滤→门禁→隔离→分类) → feed_items 表 → 企业微信 webhook`

## Tools
- Bash（python3 调用 main.py）
- Read / Write（查看与编辑 `config/settings.json`）

## Examples
```bash
cd /Users/a1234/WorkBuddy/2026-08-17-03-48-26/propfirm-feed
PY=/Users/a1234/.workbuddy/binaries/python/versions/3.13.12/bin/python3
$PY main.py run samples/offers.json      # 一键跑全管线
$PY main.py ingest intel.json && $PY main.py process && $PY main.py publish
```

## Iron Rules（硬约束）
1. **白名单类别**：只允许 RULE / PRODUCT / PAYOUT / PLATFORM / ACCOUNT / RISK / 审核过的 DEAL
2. **优惠门禁**：DEAL 必须 `our_code_verified && our_price_verified && promotion_active` 三关全过才发布，任一为 false 禁止推送
3. **内部情报隔离**：绝不向用户展示竞品 Affiliate/Creator/Referral Code、市场底价、佣金、商务条件、未经验证的宣称。用户端只展示 PropFirm.TV 自己的 code 和 referral url
4. **Severity**：仅 INFO / IMPORTANT / WARNING / CRITICAL；**Actionability**：仅 ACTION_REQUIRED / CHECK_REQUIRED / AWARENESS。禁止 NO_ACTION
5. **默认排除噪音**：Giveaway / Quiz / AMA / 直播 / 励志 / 出金截图 / 慈善 / 品牌宣传等
6. **推送前确认**：微信推送默认 `dry_run=true`（只预览不真发）；确认无误后把 `config/settings.json` 的 `dry_run` 改为 `false` 才会真发

## Source
`~/.workbuddy/skills/propfirm-feed/SKILL.md`
