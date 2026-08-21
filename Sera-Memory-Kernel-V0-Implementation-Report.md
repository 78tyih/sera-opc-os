# Sera Memory Kernel V0 — Implementation Report

> **Date**: 2026-08-21
> **Spec**: V2 (验收版)
> **Repo**: github.com/78tyih/sera-opc-os
> **Branch**: `feat/kernel-v0`
> **PR**: #1 (feat/kernel-v0 → main)
> **Reviewer**: Kimi K3

---

## 1. File Structure

```
core/sera_memory_kernel/
├── __init__.py          # 包入口，导出全部 public API
├── kernel.py            # 核心实现 (351 行 ≤ 600)
├── seed.py              # TradeSpan 种子数据
└── test_kernel.py       # 6 条验收测试
```

## 2. Implementation Summary

| Module | Lines | Description |
|--------|-------|-------------|
| `kernel.py` | 351 | 三表 DDL + FTS5 + append-only triggers + Staging Gate + Context Governor + 晋升机制 + 6 个 public API |
| `seed.py` | 70 | TradeSpan 真实场景数据注入 (7 objects, 6 relations) |
| `test_kernel.py` | 406 | 6 条验收测试，覆盖 spec V2 全部验收标准 |
| `__init__.py` | 12 | 包入口 |

## 3. Core APIs

| API | Status | Signature |
|-----|--------|-----------|
| `init_db()` | Done | `(conn?) → Connection` |
| `object_store()` | Done | `(conn, id, type, name, data_state, scope, ...) → id \| error` |
| `object_get()` | Done | `(conn, id) → dict \| None` |
| `relate()` | Done | `(conn, source, target, type, weight?)` |
| `search()` | Done | `(conn, query, limit?) → list[str]` — FTS5 MATCH → LIKE fallback |
| `build_context()` | Done | `(task_id, budget_tokens?, conn?) → dict` — Context Governor |
| `learn()` | Done | `(task_id, result, lesson, root_cause?, ...) → dict` — 含 promotion check |
| `confirm()` | Done | `(experience_id, actor, ...) → dict` — 增量 confidence + promotion check |
| `stats()` | Done | `(conn?) → dict` — 按 type/data_state/authority 聚合 |

## 4. Key Design Decisions

### 4.1 Staging Gate (6 checks)
- ID 格式: 点分隔小写 (`^[a-z0-9]+(\.[a-z0-9-]+)+$`)
- 枚举合法性: type/data_state/scope/status/authority 全部 CHECK 约束
- Authority 防伪: agent 不能以 founder 身份写入
- 范围校验: importance/confidence 必须在 [0, 1]
- Experience 专项: 失败经验必须提供 root_cause
- 泛化根因黑名单: "整体", "不可信", "都不行"

### 4.2 Context Governor
- Founder Rules 无条件下发 (不受 budget 限制)
- Experience 按 data_state 收集 (不受 status 限制，确保 draft 经验也能注入)
- Rank scoring: importance(0.4) + recency(0.25) + relation_weight(0.20) + confidence(0.15) + authority bonus
- 7 个 budget 分桶，超出截断并标记 `truncated` + `omitted_count`

### 4.3 Promotion 机制
- 条件: ≥3 独立任务, 每条经验 confidence≥0.7, 无更高 authority 矛盾 Rule
- 触发路径: `learn()` 和 `confirm()` 内部自动调用 `_promotion_check()`
- 结果: 创建新 Rule 对象 + `derived_from` 关系 + `promote` event
- 原经验对象保持不变 (data_state 不改名)

### 4.4 Events (append-only)
- 3 个触发器: events_no_update, events_no_delete, 违反则 RAISE(ABORT)
- 所有写入操作 (create/access/relate/confirm/promote) 均写 event

### 4.5 衰减 (Rule 30-day auto-downgrade 缺陷修复)
- `_recency()` 只影响 `rank_score`，never `status`
- Rule 退役只有 supersedes 或 founder 人审两条路

## 5. Test Results — 6/6 PASS

```
[PASS] T1: 记忆闭环 — root_cause 跨任务传递
[PASS] T2: draft 经验注入 — status=draft 的 Experience 仍出现在 build_context 中
[PASS] T3: 晋升真实触发 — 新 Rule 对象存在，原 Experience 未改名，derived_from 边存在
[PASS] T4: Staging Gate 拦截 — 4 种非法写入全部被拒绝，库中无残留
[PASS] T5: 搜索可用 — FTS 命中 3 条, LIKE 命中 2 条
[PASS] T6: events append-only — UPDATE/DELETE 抛异常；无静默死亡代码路径

=== All 6 tests PASSED ===
```

### T5 特别注意
- `search("TradeSpan")` → FTS5 MATCH (3 条命中, degraded=false)
- `search("信任")` → LIKE 兜底 (2 条命中, degraded=true)

## 6. stats() Output

```json
{
  "objects": 7,
  "relations": 6,
  "events": 13,
  "by_type": {
    "Decision": 2, "Experience": 1, "Project": 1, "Rule": 1, "Task": 2
  },
  "by_data_state": {
    "learned": 1, "rule": 1, "structured": 5
  },
  "by_authority": {
    "agent": 1, "founder": 4, "project": 2
  }
}
```

## 7. Spec Compliance Checklist

| Spec V2 Requirement | Status | Notes |
|---------------------|--------|-------|
| SQLite 三表 (objects/relations/events) | ✅ | 含 CHECK 约束 |
| FTS5 全文搜索 | ✅ | + LIKE 降级兜底 |
| Append-only events | ✅ | 3 个触发器 |
| Staging Gate (6 checks) | ✅ | 含泛化根因黑名单 |
| Context Governor (budget 控制) | ✅ | 7 分桶 + Founder Rules 豁免 |
| learn() → build_context() 闭环 | ✅ | T1 验证 |
| Draft 经验注入 | ✅ | T2 回归 |
| 晋升机制 (≥3 tasks × ≥0.7) | ✅ | T3 验证 |
| 衰减只影响 rank_score | ✅ | T6 验证无静默死亡 |
| 种子数据 (TradeSpan-only) | ✅ | seed.py |
| 零依赖 (stdlib + sqlite3) | ✅ | |
| kernel.py ≤ 600 行 | ✅ | 351 行 |
| 文档冻结 (7 天) | ✅ | 未修改任何架构文档 |

## 8. Known Issues / Deviations

- **None.** All spec V2 requirements are met. 6/6 tests pass.

## 9. PR Link

https://github.com/78tyih/sera-opc-os/pull/1

### e892d6b Commit 更正

`e892d6b` (`feat: 借鉴 K3 前端结构重构控制中心 + 文档冻结+Kernel V0 修订`):
该 commit 实际以前端重构 (借鉴 K3 结构) 和文档修订 (Kimi K3 审计建议) 为主，
Kernel V0 部分仅为不完整草稿。本 PR 的 Kernel V0 实现是独立、完整的重新实现，
应取代 e892d6b 中的 Kernel V0 草稿。