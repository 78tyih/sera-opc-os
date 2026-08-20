# Sera Project Portfolio

> 版本：1.2.0
> 管理 Sera Agent OS 所有项目资产

---

## 目录结构

```
portfolio/
├── projects/          # 项目目录（每个项目一个子目录）
│   ├── niuniu-ai/
│   ├── tradespan/
│   ├── propfirm-tv/
│   ├── htx-otc/
│   └── deltapex/
├── registry/          # 项目注册表
│   └── projects.json
├── templates/         # 项目模板
│   ├── PROJECT_PROFILE.md
│   └── PROJECT_DECISION.md
├── archive/           # 已归档/已停止项目
└── analytics/         # 项目分析与报告
```

## 项目生命周期

```
Idea → CEO Decision → Profile → Active → Launch → Archive
  |         |              |         |        |        |
  |       HOLD/STOP    Pending     Active   Done    Archived
```

## 状态定义

| 状态 | 说明 |
|------|------|
| `idea` | 初步想法，未评估 |
| `evaluating` | CEO Agent 正在评估 |
| `hold` | 暂缓，等待条件触发 |
| `active` | 活跃执行中 |
| `launched` | 已发布 |
| `archived` | 已归档 |

## 使用方式

```bash
# CEO Agent 评估新项目
python3 core/sera-agent-router/router.py --plan "评估牛牛 AI 项目"

# 查看项目组合状态
cat portfolio/registry/projects.json

# 查看项目详情
cat portfolio/projects/{project-name}/PROJECT_PROFILE.md
```