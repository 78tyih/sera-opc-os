# Sera Agent OS — Agent Handoff

> 交接方：WorkBuddy（2026-08-21 03:45）· 接收方：Trae / 任意 Agent
> 仓库：`github.com/78tyih/sera-agent-os`（PRIVATE）· 本地：`~/sera-agent-os/`

---

## 0. 交接提示词（复制给 Trae 的第一条消息）

```
你是 Sera Agent OS 的接续维护者。

先做 3 件事建立上下文：
1. cd ~/sera-agent-os && cat README.md && cat HANDOFF.md
2. python3 core/sera-agent-router/router.py --plan-test   # 验证 Router 健康（应 12/12 通过）
3. ls agents/*/ && ls core/*/                            # 确认 5 Agent × 6 文件 Contract 齐全

然后按 HANDOFF.md「待办清单」继续推进（从 P0 开始，逐项完成并 commit/push，
提交信息用英文，完成后打 tag 升级版本线）。

重要约束：
- Skill 不属于任何平台，属于 Sera Agent OS；所有新 Skill 遵循 templates/SKILL.template.md
- Agent 标准 = 6 文件 Contract（agent.yaml/system.md/memory-policy.yaml/skill-map.yaml/evaluation.yaml）
- 模型路由看 runtime/model-router.yaml（research→DeepSeek / coding→Codex / design→Trae / automation→WorkBuddy / image-video→Serawin）
- 破坏性操作（改名/删除/推送前）先向用户确认；不确定就问，不要猜
```

---

## 1. 系统状态摘要

| 项 | 状态 |
|---|---|
| 仓库 | `github.com/78tyih/sera-agent-os`（PRIVATE） |
| 版本线 | v1.0.0-foundation → v1.1 → v1.1.0 → v1.2 → v2.0 |
| 架构 | core 9 + agents 5 + business 3 + creative 4 + adapters 6 + platforms 5 |
| Router | 三层规划（Intent→Agent Planner→Execution），`--test`/`--plan-test` 均 12/12 通过 |
| 5 个 Agent | propfirm / otc / trading / video / design — 全部 active，各 6 文件 Contract |
| 模型路由 | `runtime/model-router.yaml`（已建配置，未落地执行） |
| 评估体系 | `evaluation/`（agent-score.yaml，未开始记录） |
| Memory/State | 目录与 README 已建（memory/ vs state/），策略在 agents/*/memory-policy.yaml |
| 平台接入 | platforms/ 5 平台文档 + install.sh（一键软链） |

## 2. 目录速览

```
sera-agent-os/
├── architecture/          # 架构文档（V1.0 + V1.1 评审）
├── core/                  # 9 个系统 Skill
│   ├── sera-agent-orchestrator/   # 编排器（引擎=router）
│   ├── sera-agent-router/         # Router 三层规划（router.py + routes.yaml + workflows/）
│   ├── sera-agent-registry/       # Agent 注册表
│   ├── sera-memory-system/        # 共享记忆
│   ├── sera-state-manager/        # 工作状态
│   ├── sera-skill-registry/       # Skill 注册表
│   ├── sera-context-system/       # ← 原 context-hub
│   ├── sera-knowledge-sync/       # ← 原 obsidian-sync
│   └── sera-compute-control/      # ← 原 serawin-remote
├── agents/                # 5 Agent × 6 文件（Contract 标准）
├── business/  creative/  adapters/   # Skill 层
├── platforms/             # 5 平台接入文档
├── evaluation/            # 评估体系
├── runtime/               # model-router.yaml
├── memory/  state/        # 记忆/状态分离
├── templates/             # SKILL/agent/workflow 模板
└── install.sh             # 一键安装
```

## 3. 健康检查命令

```bash
cd ~/sera-agent-os
python3 core/sera-agent-router/router.py --test         # 单层路由 12/12
python3 core/sera-agent-router/router.py --plan-test    # 三层规划 12/12
python3 core/sera-agent-router/router.py --plan "帮我做 TradeSpan 产品发布页"  # 演示三层输出
git log --oneline | head -5                            # 确认版本历史
git status -s                                          # 确认工作区干净
```

## 4. 待办清单（V1.2+）

### P0 — Agent 改名（评审建议，解耦 PropFirm 单一业务）
- [ ] `propfirm-agent` → `sera-business-agent`（未来含 propfirm/crypto/market 子域）
- [ ] `video-agent` → `sera-content-agent`（视频只是输出之一：文章/海报/视频/网页）
- [ ] `design-agent` → `sera-design-director`（设计负责人，非执行者）
- [ ] 同步更新：目录名 / agent.yaml name / SKILL.md frontmatter / routes.yaml / README / registry
- 注意：改名波及 router.py 的 EXECUTION_STEPS 与 routes.yaml 的 pipeline 引用，需回归 `--test`/`--plan-test`

### P1 — 模型路由落地执行
- [ ] 为 5 个 Agent 按 `runtime/model-router.yaml` 声明实际使用的模型/平台
- [ ] 各平台接入时（platforms/*.md）补模型路由章节
- [ ] 实测：同一任务用不同模型跑，记录到 evaluation/agent-score.yaml

### P2 — Skill 生命周期管理
- [ ] 定义 Skill 生命周期状态（active / deprecated / archived）
- [ ] 注册表 `sera-skill-registry` 增加状态字段
- [ ] 废弃 Skill 归档流程（移到 archive/ 或标记 deprecated）

### P3 — Evaluation 实际运行
- [ ] 任务完成后按 agents/*/evaluation.yaml 维度打分（1-5）
- [ ] 汇总写入 evaluation/agent-score.yaml
- [ ] 定期模型对比报告（DeepSeek vs GPT vs Codex 驱动同一 Agent）

## 5. 关键约定（铁律）

1. **Skill 属于 Sera Agent OS**，不属于任何平台；新 Skill 必须含 `SKILL.md`（Purpose/When to use/Inputs/Outputs/Workflow/Dependencies/Examples/Iron Rules）
2. **Agent = 6 文件 Contract**，缺一不算注册完成
3. **Memory 与 State 分离**：Memory=过去知道什么（长期）；State=现在正在发生什么（短期）
4. **Router 优先级**：compute（serawin 强信号）> video > multi-agent > 领域 > fallback
5. 破坏性操作（改名/删除/推送前）先向用户确认；敏感数据（竞品 code/底价/凭证）绝不外泄
6. 提交信息用英文；版本升级用 tag（下个：v1.2.0 或 v2.1，按改动范围定）

## 6. 参考链接

- 架构：`architecture/sera-agent-os-v1.md`（V1.0）、`architecture/sera-agent-os-v1.1-upgrade.md`（V1.1 评审）
- 审计：`docs/SKILL-AUDIT-REPORT.md`（151 Skill 四层分类）
- 模板：`templates/SKILL.template.md`、`templates/agent.yaml`、`templates/workflow.yaml`

---

*Handoff 生成：2026-08-21 · WorkBuddy → Trae*
