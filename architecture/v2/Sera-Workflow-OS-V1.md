# Sera Workflow OS V1

## AI 公司业务流程操作系统

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Engineering Design |
| Owner | Sera COO |
| Layer | Execution (Layer 3) |
| Dependencies | Organization OS V1, SMOP V1, Memory Engine V1 |
| Target | DeepSeek / Trae / Codex Direct Execution |

---

# 0. Executive Summary

## 问题

我们已经有了：

- **Memory Graph** — 公司知道什么
- **Memory Engine** — 公司记住什么
- **SMOP** — 公司如何理解对象
- **Organization OS** — 公司如何组织员工

但缺少最核心的一层：**公司如何自动运转。**

一个 AI 公司不能靠人手动触发每个步骤。

需要：

```
"我需要做一个产品视频"

→ 自动触发 Research → Script → Visual → Production → Review → Publish

→ 全自动完成
```

## 类比

| 系统 | 解决的问题 |
|------|-----------|
| 传统公司 | SOP、流程管理、审批流 |
| Linux | systemd 服务编排 |
| Kubernetes | Pod 编排、健康检查、自动重试 |
| Temporal / Airflow | 工作流引擎 |
| **Sera Workflow OS** | **AI 公司业务流程自动执行** |

## 核心定义

**Workflow OS** 是 Sera OPCOS 中定义、触发、执行、监控和优化业务流程的系统。

它解决：

```
"我有员工和知识，但如何让它们自动产出价值？"
```

---

# 一、核心架构

## 1.1 整体流程

```
                   Business Need
                        │
                        ▼
              ┌─────────────────────┐
              │   Workflow OS       │
              │   (业务流程引擎)     │
              └─────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │  Trigger   │ │  Pipeline  │ │  Monitor   │
   │  System    │ │  Engine    │ │  & Alert   │
   └────────────┘ └────────────┘ └────────────┘
          │             │             │
          ▼             ▼             ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │  Event     │ │  Agent     │ │  Error     │
   │  Sources   │ │  Pipeline  │ │  Recovery  │
   └────────────┘ └────────────┘ └────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │  Human     │ │  Tool      │ │  Memory    │
   │  Approval  │ │  Execution │ │  Logging   │
   └────────────┘ └────────────┘ └────────────┘
```

## 1.2 Workflow 生命周期

```
                    ┌──────────┐
                    │  draft   │  (定义中)
                    └────┬─────┘
                         │ activate
                         ▼
                    ┌──────────┐
                    │  active  │──────────┐
                    └────┬─────┘          │
                         │ trigger        │ deactivate
                         ▼                ▼
                    ┌──────────┐     ┌──────────┐
                    │ running  │     │ inactive │
                    └────┬─────┘     └──────────┘
                    ┌────┴────┐
                    │         │
                    ▼         ▼
              ┌────────┐ ┌────────┐
              │completed│ │ failed │
              └────────┘ └────────┘
```

## 1.3 Workflow 的 7 要素

```
一个完整的 Workflow 由 7 部分组成：

1. Trigger     — 什么事件启动
2. Pipeline    — 步骤序列
3. Agents      — 谁执行
4. Gates       — 审批关卡
5. Tools       — 用什么工具
6. Recovery    — 出错怎么办
7. Output      — 产出什么
```

---

# 二、Workflow Object Schema

## 2.1 Workflow Object

```json
{
  "id": "workflow.video.production",
  "type": "Workflow",
  "name": "视频生产工作流",
  "description": "从选题到发布的全自动视频生产流程",

  "status": "active",
  "importance": 0.9,
  "confidence": 0.95,

  "created_at": "2026-08-01T00:00:00Z",
  "updated_at": "2026-08-21T00:00:00Z",
  "owner": "person.sera",

  "properties": {
    "category": "media",
    "department": "dept.media",
    "version": "2.1.0",
    "avg_duration_minutes": 240,
    "total_executions": 47,
    "success_rate": 0.85,
    "quality_check_passed": true,

    "triggers": [
      {
        "id": "trigger.new-topic",
        "type": "event",
        "source": "slack.command",
        "condition": "command == '/produce-video'",
        "params": {
          "topic": "string (required)",
          "style": "string (default: 'fintech')",
          "duration": "number (default: 60)"
        }
      },
      {
        "id": "trigger.scheduled",
        "type": "schedule",
        "cron": "0 9 * * 1-5",
        "description": "工作日早 9 点自动检查是否有待处理选题"
      }
    ],

    "pipeline": [
      {
        "step_id": "step.research",
        "name": "研究选题",
        "agent_role": "role.researcher",
        "description": "收集和分析选题素材",
        "inputs": ["trigger.params.topic"],
        "outputs": ["research_report"],
        "timeout_minutes": 30,
        "retry_count": 2,
        "approval_required": false
      },
      {
        "step_id": "step.script",
        "name": "撰写脚本",
        "agent_role": "role.script.writer",
        "description": "基于研究报告撰写视频脚本",
        "inputs": ["step.research.output.research_report"],
        "outputs": ["script_markdown"],
        "timeout_minutes": 45,
        "retry_count": 2,
        "approval_required": true,
        "approval_by": "person.sera",
        "approval_timeout_hours": 24
      },
      {
        "step_id": "step.visual",
        "name": "设计视觉",
        "agent_role": "role.visual.designer",
        "description": "根据脚本设计视觉元素",
        "inputs": ["step.script.output.script_markdown"],
        "outputs": ["visual_assets"],
        "timeout_minutes": 60,
        "retry_count": 1,
        "approval_required": false
      },
      {
        "step_id": "step.production",
        "name": "制作视频",
        "agent_role": "role.video.producer",
        "description": "合成最终视频",
        "inputs": ["step.visual.output.visual_assets", "step.script.output.script_markdown"],
        "outputs": ["video_file.mp4"],
        "timeout_minutes": 120,
        "retry_count": 1,
        "approval_required": false
      },
      {
        "step_id": "step.publish",
        "name": "发布",
        "agent_role": "role.publisher",
        "description": "上传到发布平台",
        "inputs": ["step.production.output.video_file.mp4"],
        "outputs": ["publish_url"],
        "timeout_minutes": 15,
        "retry_count": 3,
        "approval_required": true,
        "approval_by": "person.sera",
        "approval_timeout_hours": 48
      }
    ],

    "error_recovery": {
      "max_retries_per_step": 3,
      "step_failure_action": "retry_and_escalate",
      "escalate_to": "person.sera",
      "escalate_after_retries": 3,
      "pipeline_failure_action": "rollback_to_last_checkpoint",
      "checkpoint_enabled": true
    },

    "outputs": {
      "primary": "video_file.mp4",
      "secondary": ["publish_url", "thumbnail.png", "transcript.md"],
      "archive_to": "memory.asset.video"
    }
  },

  "relations": [
    {"type": "managed_by", "target": "agent.media.director", "weight": 1.0},
    {"type": "uses_skill", "target": "skill.hyperframes", "weight": 0.9},
    {"type": "uses_skill", "target": "skill.script-writing", "weight": 0.8},
    {"type": "uses_skill", "target": "skill.motion-design", "weight": 0.7},
    {"type": "creates", "target": "asset.video.output", "weight": 1.0},
    {"type": "belongs_to", "target": "dept.media", "weight": 1.0}
  ],

  "tags": ["media", "video", "production", "active"]
}
```

## 2.2 WorkflowStep Object

每个步骤也是一个独立 Object，支持更细粒度的控制。

```json
{
  "id": "step.script.writing",
  "type": "WorkflowStep",
  "name": "脚本撰写步骤",
  "description": "Agent 根据研究材料撰写视频脚本",

  "status": "active",
  "importance": 0.7,
  "confidence": 0.9,

  "properties": {
    "workflow_id": "workflow.video.production",
    "step_order": 2,
    "agent_role": "role.script.writer",
    "timeout_minutes": 45,
    "retry_count": 2,
    "retry_delay_seconds": 30,

    "input_schema": {
      "type": "object",
      "required": ["research_report"],
      "properties": {
        "research_report": {"type": "string", "description": "研究报告内容"}
      }
    },

    "output_schema": {
      "type": "object",
      "required": ["script_markdown"],
      "properties": {
        "script_markdown": {"type": "string", "description": "视频脚本 Markdown"},
        "duration_estimate": {"type": "number", "description": "预计视频时长(秒)"}
      }
    },

    "agent_instructions": "基于研究报告，撰写一个 60 秒的金融视频脚本。风格要求：专业、可信、简洁。包含开场、正文、CTA 三部分。",

    "approval": {
      "required": true,
      "approval_by": "person.sera",
      "timeout_hours": 24,
      "auto_approve_if_no_response": false
    },

    "error_handling": {
      "on_timeout": "retry",
      "on_failure": "retry_and_escalate",
      "on_invalid_output": "retry_with_feedback"
    }
  },

  "relations": [
    {"type": "part_of", "target": "workflow.video.production", "weight": 1.0},
    {"type": "executed_by", "target": "role.script.writer", "weight": 1.0}
  ]
}
```

## 2.3 WorkflowRun Object（执行实例）

每次 Workflow 的执行都是一个独立的 Run Object。

```json
{
  "id": "run.video.20260821.001",
  "type": "WorkflowRun",
  "name": "视频生产 #20260821-001",
  "description": "PropFirm TV 视频: '如何选择外汇经纪商'",

  "status": "running",
  "importance": 0.7,
  "confidence": 1.0,

  "created_at": "2026-08-21T09:00:00Z",
  "updated_at": "2026-08-21T09:45:00Z",
  "owner": "person.sera",

  "properties": {
    "workflow_id": "workflow.video.production",
    "workflow_version": "2.1.0",
    "trigger": {
      "type": "slack.command",
      "source": "#content-planning",
      "input": {
        "topic": "如何选择外汇经纪商",
        "style": "fintech",
        "duration": 60
      }
    },

    "current_step": "step.script",
    "steps_completed": 1,
    "total_steps": 5,

    "step_results": [
      {
        "step_id": "step.research",
        "status": "completed",
        "started_at": "2026-08-21T09:00:00Z",
        "completed_at": "2026-08-21T09:25:00Z",
        "duration_minutes": 25,
        "agent": "agent.researcher.v2",
        "output": {
          "research_report": "外汇经纪商选择指南...",
          "sources": ["https://...", "https://..."]
        },
        "cost": 0.08
      },
      {
        "step_id": "step.script",
        "status": "running",
        "started_at": "2026-08-21T09:30:00Z",
        "agent": "agent.script.writer",
        "estimated_completion": "2026-08-21T10:15:00Z"
      }
    ],

    "metrics": {
      "total_cost_so_far": 0.08,
      "elapsed_minutes": 45,
      "estimated_remaining_minutes": 180,
      "estimated_total_cost": 0.65
    }
  },

  "relations": [
    {"type": "instance_of", "target": "workflow.video.production", "weight": 1.0},
    {"type": "triggered_by", "target": "event.content-planning.20260821", "weight": 1.0},
    {"type": "produces", "target": "asset.video.pending", "weight": 0.5}
  ]
}
```

---

# 三、Trigger System（触发系统）

## 3.1 触发类型

```
Workflow OS 支持 4 类触发：

1. Event Trigger（事件驱动）
2. Schedule Trigger（定时）
3. API Trigger（外部调用）
4. Chain Trigger（链式触发）
```

### 3.1.1 Event Trigger

```json
{
  "trigger_id": "trigger.new-topic",
  "type": "event",
  "source": "slack.command",
  "condition": "command == '/produce-video'",
  "params": {
    "topic": {"type": "string", "required": true, "from": "command_args[0]"},
    "style": {"type": "string", "default": "fintech"},
    "duration": {"type": "number", "default": 60}
  }
}
```

支持的事件源（V1）：

| 事件源 | 示例 | 说明 |
|--------|------|------|
| slack.command | `/produce-video "topic"` | Slack 斜杠命令 |
| slack.message | #content-planning 频道新消息 | 频道消息触发 |
| github.push | push 到 main 分支 | 代码推送触发 |
| github.pr | PR merged | PR 合并触发 |
| smop.object | 新 Decision 创建 | 决策触发工作流 |
| email.received | 收到特定主题邮件 | 邮件触发 |
| webhook | 外部 HTTP POST | 通用 Webhook |

### 3.1.2 Schedule Trigger

```json
{
  "trigger_id": "trigger.daily-report",
  "type": "schedule",
  "cron": "0 18 * * 5",
  "timezone": "Asia/Shanghai",
  "description": "每周五下午 6 点生成周报",
  "params": {
    "period": "weekly",
    "format": "markdown"
  }
}
```

### 3.1.3 API Trigger

```json
{
  "trigger_id": "trigger.api-produce",
  "type": "api",
  "endpoint": "POST /api/v1/workflow/video-production/trigger",
  "auth": "api-key",
  "params": {
    "topic": {"type": "string", "required": true},
    "style": {"type": "string", "default": "fintech"}
  }
}
```

### 3.1.4 Chain Trigger

一个 Workflow 完成后自动触发另一个 Workflow。

```json
{
  "trigger_id": "trigger.publish-after-production",
  "type": "chain",
  "source_workflow": "workflow.video.production",
  "source_status": "completed",
  "target_workflow": "workflow.social.publish",
  "param_mapping": {
    "source.output.video_file": "target.input.video",
    "source.output.thumbnail": "target.input.thumbnail",
    "source.output.script": "target.input.caption"
  }
}
```

## 3.2 Trigger 注册表

```json
{
  "id": "trigger.registry.media",
  "type": "TriggerRegistry",
  "name": "Media 部门触发器注册表",

  "properties": {
    "department": "dept.media",
    "triggers": [
      {
        "id": "trigger.new-topic",
        "workflow": "workflow.video.production",
        "type": "event",
        "source": "slack.command /produce-video",
        "status": "active",
        "last_triggered": "2026-08-21T09:00:00Z",
        "total_triggers": 47
      },
      {
        "id": "trigger.daily-content-check",
        "workflow": "workflow.content.planning",
        "type": "schedule",
        "cron": "0 9 * * 1-5",
        "status": "active",
        "last_triggered": "2026-08-21T09:00:00Z",
        "total_triggers": 156
      }
    ]
  }
}
```

---

# 四、Pipeline Engine（流水线引擎）

## 4.1 执行模型

Pipeline Engine 是 Workflow OS 的核心，负责按顺序执行步骤。

```
Pipeline 执行算法：

function execute_pipeline(workflow, input):
    run = create_workflow_run(workflow, input)
    checkpoint = {}

    for step in workflow.pipeline:
        run.current_step = step.step_id

        // 1. 解析输入
        step_input = resolve_inputs(step.inputs, run.step_results, input)

        // 2. 分配 Agent
        agent = assign_agent(step.agent_role, run)

        // 3. 执行
        result = execute_step(agent, step, step_input, checkpoint)

        // 4. 检查结果
        if result.status == "failed":
            result = handle_step_failure(step, result, run)
            if result.status == "failed":
                return fail_pipeline(run, result)

        // 5. 检查审批
        if step.approval_required:
            result = wait_for_approval(step, result, run)
            if result.status == "rejected":
                return fail_pipeline(run, result)

        // 6. 保存 checkpoint
        checkpoint[step.step_id] = result.output
        run.step_results.append(result)

        // 7. 记录到 Memory
        log_step_to_memory(run, step, result)

    return complete_pipeline(run)
```

## 4.2 Step 执行细节

### 执行上下文

每个步骤执行时，Agent 收到的上下文：

```json
{
  "workflow_id": "workflow.video.production",
  "run_id": "run.video.20260821.001",
  "step_id": "step.script",
  "step_name": "撰写脚本",

  "workflow_context": {
    "trigger": {"topic": "如何选择外汇经纪商", "style": "fintech"},
    "project": "project.propfirm-tv",
    "department": "dept.media"
  },

  "inputs": {
    "research_report": "外汇经纪商选择指南... (来自 step.research)"
  },

  "memory_context": {
    "project": {"name": "PropFirm TV", "goal": "构建 prop trading 媒体平台"},
    "decisions": [
      {"id": "decision.video.react-gsap", "content": "使用 React + GSAP 生成动效"},
      {"id": "decision.video.style", "content": "专业金融风格，蓝色调"}
    ],
    "rules": [
      {"id": "rule.financial.trust-first", "content": "可信度 > 炫技"}
    ],
    "experiences": [
      {"id": "experience.video.ui-failure", "lesson": "纯 AI 视频缺乏 UI 可信度"}
    ]
  },

  "available_tools": ["smop.read", "memory.search", "github.write", "filesystem.read"],

  "timeout_minutes": 45,
  "attempt": 1
}
```

### 步骤输出

```json
{
  "step_id": "step.script",
  "status": "completed",
  "started_at": "2026-08-21T09:30:00Z",
  "completed_at": "2026-08-21T10:12:00Z",
  "duration_minutes": 42,
  "agent": "agent.script.writer.v2",
  "attempt": 1,
  "cost": 0.12,

  "output": {
    "script_markdown": "# 如何选择外汇经纪商\n\n## 开场\n...",
    "duration_estimate": 65,
    "key_points": ["监管合规", "交易成本", "平台稳定性"]
  },

  "artifacts": [
    {"type": "memory", "action": "created", "id": "experience.script.20260821"},
    {"type": "asset", "action": "saved", "path": "run/video-001/script.md"}
  ]
}
```

## 4.3 Agent 分配算法

```json
// 步骤执行前的 Agent 分配
{
  "step_id": "step.script",
  "required_role": "role.script.writer",

  "candidates": [
    {
      "agent": "agent.script.writer.v2",
      "score": 0.93,
      "skill_match": 0.95,
      "availability": 0.90,
      "past_success_on_this_workflow": 0.92,
      "cost": 0.12
    },
    {
      "agent": "agent.script.writer.v1",
      "score": 0.72,
      "skill_match": 0.80,
      "availability": 0.95,
      "past_success_on_this_workflow": 0.70,
      "cost": 0.08
    }
  ],

  "selected": "agent.script.writer.v2",
  "reason": "更高的技能匹配度和历史成功率"
}
```

---

# 五、Human Approval Gate（审批关卡）

## 5.1 审批模型

某些步骤需要人类确认才能继续。

```
Pipeline 执行到审批步骤
       │
       ▼
创建 Approval Request
       │
       ▼
发送通知（Slack / Email / Dashboard）
       │
       ▼
等待审批（超时时间可配置）
       │
   ┌───┴───┐
   │       │
   ▼       ▼
Approved  Rejected
   │       │
   │       ▼
   │   记录原因
   │   提供反馈
   │   Agent 修改后重试
   │       │
   ▼       ▼
继续执行  终止流程
```

## 5.2 ApprovalRequest Object

```json
{
  "id": "approval.script.20260821.001",
  "type": "ApprovalRequest",
  "name": "脚本审批: 如何选择外汇经纪商",

  "status": "pending",
  "importance": 0.8,
  "confidence": 1.0,

  "created_at": "2026-08-21T10:12:00Z",
  "updated_at": "2026-08-21T10:12:00Z",

  "properties": {
    "workflow_id": "workflow.video.production",
    "run_id": "run.video.20260821.001",
    "step_id": "step.script",

    "requested_by": "agent.script.writer.v2",
    "requested_to": "person.sera",
    "approval_type": "content_review",

    "details": {
      "title": "审核视频脚本",
      "description": "请审核以下视频脚本，确认内容准确性和风格一致性",
      "content_url": "https://sera.ai/run/video-001/script.md",
      "preview": "外汇经纪商选择指南 - 60秒金融视频脚本..."
    },

    "decision": null,
    "decision_reason": null,
    "decision_at": null,
    "timeout_at": "2026-08-22T10:12:00Z",
    "auto_approve_on_timeout": false,

    "notification_channels": ["slack", "email"],
    "escalation": {
      "enabled": true,
      "after_hours": 12,
      "escalate_to": "agent.media.director"
    }
  },

  "relations": [
    {"type": "part_of", "target": "run.video.20260821.001", "weight": 1.0},
    {"type": "requested_by", "target": "agent.script.writer.v2", "weight": 1.0},
    {"type": "requires_action_from", "target": "person.sera", "weight": 1.0}
  ]
}
```

## 5.3 审批通知模板

```markdown
## ⏳ 审批请求: 视频脚本审核

**工作流:** 视频生产工作流
**项目:** PropFirm TV
**步骤:** 脚本撰写
**提交人:** Script Writer Agent v2

---

**脚本预览:**

如何选择外汇经纪商 - 60秒金融视频脚本

> 选择外汇经纪商是交易者最重要的决策之一...
> ...

---

**操作:**

✅ [批准脚本](https://sera.ai/approve/approval.script.20260821.001)
❌ [拒绝并反馈](https://sera.ai/reject/approval.script.20260821.001)

**超时:** 24 小时 (2026-08-22 10:12)
**升级:** 12 小时后通知 Media Director
```

## 5.4 审批在 Pipeline 中的行为

```json
// 审批被拒绝时的流程
{
  "step_id": "step.script",
  "approval_status": "rejected",
  "rejection": {
    "reason": "脚本中关于监管的部分需要更详细",
    "feedback": "请补充 FCA 和 CySEC 的具体监管要求",
    "rejected_by": "person.sera",
    "rejected_at": "2026-08-21T14:00:00Z"
  },
  "action_taken": {
    "type": "retry_with_feedback",
    "retry_agent": "agent.script.writer.v2",
    "retry_input": {"feedback": "请补充 FCA 和 CySEC 的具体监管要求"},
    "retry_count": 1,
    "max_retries": 3
  }
}
```

---

# 六、Error Recovery & Retry Strategy

## 6.1 错误分类

| 错误类型 | 示例 | 处理策略 |
|---------|------|---------|
| timeout | Agent 超过 45 分钟无响应 | 自动重试，分配新 Agent |
| invalid_output | 输出不符合 Schema | 重试 + 提供 Schema 说明 |
| agent_failure | Agent 调用 API 失败 | 自动重试，切换 Model |
| tool_failure | GitHub push 失败 | 重试，检查 Tool 状态 |
| memory_error | Memory Engine 不可用 | 重试，降级到本地缓存 |
| approval_timeout | 人类 24 小时未审批 | 升级，通知更高级别 |
| pipeline_failure | 多个步骤连续失败 | 终止流程，人工介入 |

## 6.2 重试策略

```yaml
# retry-config.yaml
retry_strategies:
  # 策略 1: 快速重试
  fast_retry:
    max_retries: 3
    delay_seconds: 10
    backoff: "fixed"
   適用: timeout, tool_failure

  # 策略 2: 渐进重试
  progressive_retry:
    max_retries: 3
    delay_seconds: [30, 120, 300]
    backoff: "exponential"
   適用: memory_error, api_rate_limit

  # 策略 3: 带反馈重试
  feedback_retry:
    max_retries: 3
    delay_seconds: 60
    feedback: true
   適用: invalid_output, approval_rejected

  # 策略 4: 升级重试
  escalate_retry:
    max_retries: 2
    delay_seconds: 300
    escalate_after: 2
    escalate_to: "person.sera"
   適用: agent_failure, pipeline_failure
```

## 6.3 Checkpoint 机制

自动保存每个步骤的中间结果，失败时可以从最近的 checkpoint 恢复。

```json
{
  "run_id": "run.video.20260821.001",
  "checkpoints": [
    {
      "step_id": "step.research",
      "status": "completed",
      "output": {"research_report": "..."},
      "saved_at": "2026-08-21T09:25:00Z"
    },
    {
      "step_id": "step.script",
      "status": "completed",
      "output": {"script_markdown": "..."},
      "saved_at": "2026-08-21T10:12:00Z"
    }
  ],
  "last_checkpoint": "step.script",
  "recovery_point": "step.visual"
}
```

## 6.4 失败处理流程

```
步骤失败
    │
    ├── 判断错误类型
    │
    ├── timeout / tool_failure
    │   → 快速重试 (最多 3 次)
    │   → 成功 → 继续
    │   → 失败 → 升级
    │
    ├── invalid_output / approval_rejected
    │   → 反馈重试 (最多 3 次)
    │   → 每次提供具体反馈
    │   → 成功 → 继续
    │   → 失败 → 升级
    │
    ├── memory_error / api_rate_limit
    │   → 渐进重试 (最多 3 次)
    │   → 成功 → 继续
    │   → 失败 → 降级运行
    │
    └── agent_failure / pipeline_failure
        → 升级重试 (最多 2 次)
        → 失败 → 通知人类
        → 创建 FailureReport
```

## 6.5 FailureReport Object

```json
{
  "id": "failure.video.20260821.001",
  "type": "FailureReport",
  "name": "视频生产失败报告 #20260821-001",

  "status": "active",
  "importance": 0.8,
  "confidence": 1.0,

  "properties": {
    "workflow_id": "workflow.video.production",
    "run_id": "run.video.20260821.001",
    "failed_step": "step.production",

    "failure_summary": "视频合成步骤连续失败 3 次",
    "failure_reason": "Hyperframes 渲染引擎返回空文件",
    "failure_type": "tool_failure",

    "retry_history": [
      {"attempt": 1, "status": "failed", "reason": "Timeout", "duration": 120},
      {"attempt": 2, "status": "failed", "reason": "Empty output", "duration": 85},
      {"attempt": 3, "status": "failed", "reason": "Render error", "duration": 90}
    ],

    "recovery_actions": [
      {"action": "escalated_to", "target": "person.sera", "at": "2026-08-21T15:00:00Z"},
      {"action": "created_memory", "target": "experience.render.failure", "detail": "Hyperframes 渲染引擎需要检查"}
    ],

    "checkpoint_available": true,
    "recovery_point": "step.visual",
    "estimated_recovery_cost": 0.15,
    "total_cost_of_failure": 0.45
  },

  "relations": [
    {"type": "reports", "target": "run.video.20260821.001", "weight": 1.0},
    {"type": "escalated_to", "target": "person.sera", "weight": 1.0},
    {"type": "created_experience", "target": "experience.render.failure", "weight": 0.9}
  ]
}
```

---

# 七、Workflow 监控与 Dashboard

## 7.1 实时状态

```json
// GET /api/v1/workflow/status
{
  "total_workflows": 8,
  "active_workflows": 5,
  "running_runs": 3,
  "pending_approvals": 2,

  "running": [
    {
      "run_id": "run.video.20260821.001",
      "workflow": "视频生产",
      "current_step": "视觉设计",
      "progress": "3/5",
      "elapsed": "45m",
      "estimated_remaining": "2h",
      "cost_so_far": "$0.08"
    }
  ],

  "pending_approvals": [
    {
      "id": "approval.script.20260821.001",
      "workflow": "视频生产",
      "step": "脚本审核",
      "waiting_for": "person.sera",
      "timeout_in": "22h"
    }
  ],

  "recent_failures": [
    {
      "run_id": "run.video.20260820.003",
      "failed_step": "发布",
      "reason": "YouTube API 限流",
      "resolved": true
    }
  ]
}
```

## 7.2 Workflow 统计

```json
// GET /api/v1/workflow/stats
{
  "workflow_id": "workflow.video.production",
  "period": "2026-08",

  "total_runs": 47,
  "successful": 39,
  "failed": 8,
  "success_rate": 0.83,

  "avg_duration_minutes": 240,
  "avg_cost": 0.65,
  "avg_steps": 5,

  "step_breakdown": [
    {"step": "research", "avg_duration": 25, "success_rate": 0.98},
    {"step": "script", "avg_duration": 42, "success_rate": 0.92},
    {"step": "visual", "avg_duration": 55, "success_rate": 0.88},
    {"step": "production", "avg_duration": 90, "success_rate": 0.85},
    {"step": "publish", "avg_duration": 12, "success_rate": 0.95}
  ],

  "failure_analysis": {
    "top_reasons": [
      {"reason": "渲染超时", "count": 4, "percentage": 50},
      {"reason": "API 限流", "count": 2, "percentage": 25},
      {"reason": "审批超时", "count": 1, "percentage": 12.5},
      {"reason": "无效输出", "count": 1, "percentage": 12.5}
    ]
  }
}
```

---

# 八、完整 Workflow 示例

## 8.1 视频生产工作流（完整流程）

```
触发: Slack 命令 /produce-video "如何选择外汇经纪商"
  │
  ▼
Step 1: 研究 (Research Agent, 25min)
  ├── 收集选题资料
  ├── 分析竞品内容
  └── 输出: 研究报告
  │
  ▼
Step 2: 脚本 (Script Writer, 42min)
  ├── 基于研究报告撰写脚本
  ├── 调用 Memory 查询历史经验
  ├── 遵循 Design Decision 和 Rule
  └── 输出: 脚本 Markdown
  │
  ▼
 ⏳ 审批关卡 (person.sera, 24h timeout)
  ├── 通过 → 继续
  └── 拒绝 → 带反馈重试
  │
  ▼
Step 3: 视觉 (Visual Designer, 55min)
  ├── 根据脚本设计 UI 元素
  ├── 使用品牌色板和字体
  └── 输出: 视觉素材
  │
  ▼
Step 4: 制作 (Video Producer, 90min)
  ├── 使用 Hyperframes 合成视频
  ├── 叠加动效和过渡
  ├── 添加背景音乐和字幕
  └── 输出: MP4 视频文件
  │
  ▼
 ⏳ 审批关卡 (person.sera, 48h timeout)
  ├── 通过 → 继续
  └── 拒绝 → 返回 Step 4 修改
  │
  ▼
Step 5: 发布 (Publisher, 12min)
  ├── 上传到 YouTube / Twitter / 网站
  ├── 生成缩略图
  └── 输出: 发布链接
  │
  ▼
结束: 记录到 Memory
  ├── 创建 Experience (成功)
  ├── 更新 Asset 列表
  ├── 更新 Workflow Run 状态
  └── 发送完成通知到 Slack
```

## 8.2 网站部署工作流

```json
{
  "id": "workflow.website.deploy",
  "type": "Workflow",
  "name": "网站部署工作流",
  "description": "代码 Push 后自动构建和部署",

  "triggers": [
    {
      "id": "trigger.github-push",
      "type": "event",
      "source": "github.push",
      "condition": "branch == 'main' && repo == 'tradespan'"
    }
  ],

  "pipeline": [
    {
      "step_id": "step.build",
      "agent_role": "role.devops",
      "description": "构建前端项目",
      "timeout_minutes": 10,
      "retry_count": 2
    },
    {
      "step_id": "step.test",
      "agent_role": "role.qa",
      "description": "运行自动化测试",
      "timeout_minutes": 15,
      "retry_count": 1
    },
    {
      "step_id": "step.deploy",
      "agent_role": "role.devops",
      "description": "部署到 Vercel",
      "timeout_minutes": 5,
      "retry_count": 3
    }
  ]
}
```

## 8.3 日报生成工作流

```json
{
  "id": "workflow.daily.report",
  "type": "Workflow",
  "name": "每日报告生成",
  "description": "每天自动生成日报并推送",

  "triggers": [
    {
      "id": "trigger.daily",
      "type": "schedule",
      "cron": "0 18 * * 1-5",
      "timezone": "Asia/Shanghai"
    }
  ],

  "pipeline": [
    {
      "step_id": "step.collect",
      "agent_role": "role.operator",
      "description": "收集当天所有 Workflow 执行数据",
      "timeout_minutes": 5
    },
    {
      "step_id": "step.analyze",
      "agent_role": "role.analyst",
      "description": "分析数据，提取关键指标",
      "timeout_minutes": 10
    },
    {
      "step_id": "step.generate",
      "agent_role": "role.operator",
      "description": "生成日报 Markdown",
      "timeout_minutes": 5,
      "approval_required": false
    },
    {
      "step_id": "step.push",
      "agent_role": "role.integrator",
      "description": "推送到 Slack 和飞书",
      "timeout_minutes": 3
    }
  ]
}
```

---

# 九、Workflow OS 与其它层的集成

## 9.1 完整架构（所有 5 层）

```
┌──────────────────────────────────────────────────────────┐
│                    Founder                                │
│                  person.sera                              │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│                 Sera Intelligence                         │
└────────────────────────┬─────────────────────────────────┘
                         │
=============================================================
  Layer 4: Organization OS (组织管理)
  ─────────────────────────────────────────────────────────
  - 公司结构 / 部门 / 角色 / Agent 员工 / 绩效 / 晋升
=============================================================
                         │
┌────────────────────────▼─────────────────────────────────┐
│  Layer 3: Workflow OS (业务流程)         ← 当前层        │
│  ───────────────────────────────────────────────────────  │
│  - Trigger System (事件/定时/API/链式)                    │
│  - Pipeline Engine (步骤执行 / Agent 分配)                │
│  - Human Approval Gate (审批关卡 / 通知 / 升级)           │
│  - Error Recovery (重试 / Checkpoint / 降级 / 升级)       │
│  - Monitoring (Dashboard / 统计 / 失败分析)               │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│  Layer 1-2: Memory System (记忆系统)                      │
│  ───────────────────────────────────────────────────────  │
│  - SMOP (对象协议: Object Schema / Context Package)       │
│  - Memory Engine (存储: SQLite + LanceDB + Filesystem)    │
│  - Memory Graph (数据: 12 Entity / 16 Relation)           │
└──────────────────────────────────────────────────────────┘
```

## 9.2 Workflow OS 使用的 SMOP 端点

```
Workflow OS 作为 SMOP 和 Organization OS 的消费者：

POST /smop/context/build
  → 为每个 Step 的 Agent 构建执行上下文

GET /smop/object/{id}
  → 获取 Workflow / Step / Agent 对象

POST /smop/object/store
  → 创建 WorkflowRun / ApprovalRequest / FailureReport

POST /smop/learn
  → 每次 Workflow 完成后提交经验

POST /smop/decision
  → 记录 Workflow 执行中的决策

POST /org/agent/assign
  → 分配 Agent 给步骤（Organization OS 协议）
```

## 9.3 Workflow 执行后的 Memory 自动更新

```
每次 Workflow 完成后，自动执行：

1. 创建 Experience
   {
     task: "视频生产: 如何选择外汇经纪商",
     result: "success",
     duration: 240,
     cost: 0.65,
     lesson: extract_lesson_from_run()
   }

2. 更新 Agent Performance
   agent.video.producer.metrics.task_count += 1
   agent.video.producer.metrics.success_rate = recalc()

3. 更新 Workflow 统计
   workflow.video.production.avg_duration = recalc()
   workflow.video.production.success_rate = recalc()

4. 创建 Asset
   asset.video.output = { path: "...", workflow_run: "..." }

5. 触发 Chain Workflow（如果有）
   if workflow.chain:
     trigger_next_workflow(workflow.chain.target)
```

---

# 十、V1 实现范围

## 10.1 核心功能（必须实现）

| 功能 | 优先级 | 说明 |
|------|--------|------|
| Workflow Object 定义 | P0 | 完整的 Workflow Schema |
| Step 执行引擎 | P0 | 按顺序执行步骤 |
| Agent 分配 | P0 | 根据 Role 分配 Agent |
| 输入/输出解析 | P0 | 步骤间数据传递 |
| 超时控制 | P0 | Timeout 后重试 |
| 基础重试 | P0 | 失败后自动重试 |
| WorkflowRun 追踪 | P0 | 记录执行状态 |

## 10.2 扩展功能（V1 可选）

| 功能 | 优先级 | 说明 |
|------|--------|------|
| Approval Gate | P1 | 人类审批关卡 |
| Trigger 系统 | P1 | 事件/定时/API 触发 |
| Checkpoint 恢复 | P1 | 从失败点恢复 |
| Chain Workflow | P2 | 工作流串联 |
| Dashboard | P2 | 实时监控面板 |
| 失败分析 | P2 | 自动分析失败原因 |
| 审批升级 | P2 | 超时后自动升级 |

## 10.3 实现路线图

```
Phase 1 (Week 1-2): Core Engine
  - Workflow Object Schema 实现
  - Step 执行引擎（顺序执行）
  - Agent 分配（按 Role 匹配）
  - 输入/输出解析
  - 基础 WorkflowRun 追踪

Phase 2 (Week 3-4): Reliability
  - 超时控制 + 自动重试
  - Checkpoint 机制
  - 错误分类 + 分级处理
  - FailureReport 生成

Phase 3 (Week 5-6): Completeness
  - Approval Gate 系统
  - Trigger 系统（Event + Schedule）
  - Chain Workflow
  - 通知集成（Slack / Email）

Phase 4 (Week 7-8): Intelligence
  - Dashboard / 监控
  - 失败分析 + 自动优化建议
  - 与 Memory 的经验回写
  - Workflow 执行统计
```

---

# 附录 A: 所有 Object 类型总览

| Layer | Object 类型 | 用途 |
|-------|------------|------|
| Memory | Entity (12 types) | 静态数据 |
| SMOP | Object (base) | 对象协议 |
| Organization | Organization | 公司实体 |
| Organization | Department | 部门 |
| Organization | Role | 岗位标准 |
| Organization | Agent | 数字员工 |
| Organization | Team | 临时项目组 |
| Organization | Performance | 绩效记录 |
| Workflow | Workflow | 业务流程定义 |
| Workflow | WorkflowStep | 步骤定义 |
| Workflow | WorkflowRun | 执行实例 |
| Workflow | ApprovalRequest | 审批请求 |
| Workflow | FailureReport | 失败报告 |
| Workflow | TriggerRegistry | 触发器注册表 |

# 附录 B: Workflow 设计原则

```
1. 每个 Workflow 必须有一个明确的 Output
2. 每个 Step 必须有一个明确的 Agent Role
3. 每个 Step 必须定义 Timeout
4. 每个 Step 必须定义 Retry Strategy
5. 审批关卡必须有时限
6. 关键步骤必须有 Checkpoint
7. 每次执行必须记录到 Memory
8. 失败必须生成 FailureReport
9. Workflow 必须有版本号
10. Workflow 必须有对应的 Department
```

---

*Document Version: 1.0*
*Last Updated: 2026-08-21*
*Next: Sera OPCOS Integration & Implementation Guide V1*