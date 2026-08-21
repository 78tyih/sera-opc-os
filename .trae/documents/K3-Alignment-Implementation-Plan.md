# K3 对齐实施计划

## Context

Kimi K3 对 Sera OPC OS 进行了全面点评，提出五个方向的建议。我们做了对抗式审查后，提取出三个最紧迫的落地任务：

1. **K3 对齐声明**：记录砍什么、深什么、度量标准
2. **Kernel V0 增强**：root_cause 黑名单扩展 + 审计日志 + 运行时遥测
3. **产品定位改口**：从 "Agent OS" → "Organizational memory for one-person companies"

实施顺序：1 → 2 → 3（声明先行，代码紧跟，文案收尾）

---

## 任务一：K3 对齐声明

### 新建文件

`architecture/v2/K3-Alignment-Statement.md`

### 内容结构

遵循现有 architecture doc 风格（中文、表格头、`---` 分隔），约 60-80 行，四个部分：

**A. 砍什么**
- 30+ 纯文档目录（autonomous-os/, commercial-os/, intelligence-os/ 等）冻结不再扩展
- "六层架构"叙事从 README 移除，统一为 V1.1 的 4+1+1 模型
- "Agent = 员工" 比喻降级
- Registry JSON 手工维护 → 以 Kernel objects 表为唯一注册表

**B. 深什么**
- root_cause 系统：扩展黑名单、加审计日志、加遥测
- health_check() 表面：暴露运行时度量
- 产品定位：从 "AI 公司操作系统" → "一人公司的组织记忆"

**C. 度量标准**
- `injection_hit_rate`：有 root_cause 的 Experience 被访问比例（目标 > 80%）
- `root_cause_repeat_rate`：同根因跨任务重复频率（目标：逐月下降）
- `rule_maturity_days`：活跃 Rule 的平均存活天数（目标：至少一条 > 30 天）
- `promotion_rate`：Experience → Rule 晋升率（目标：每 20 条经验 ≥ 1 次晋升）

**D. 产品定位**
- 旧：World-Class AI Company Operating System
- 新：Organizational memory for one-person companies
- 一句话：一个人经营公司的记忆内核。把每一次失败变成下一次的上下文。

---

## 任务二：Kernel V0 增强

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `core/sera_memory_kernel/kernel.py` | 扩展黑名单、新增审计日志、新增 4 个函数 |
| `core/sera_memory_kernel/test_kernel.py` | 新增 3 个测试 T7/T8/T9 |
| `core/sera_memory_kernel/__init__.py` | 导出 4 个新函数 |

### 2A. 扩展 GENERIC_ROOT_CAUSE_BLACKLIST

```python
GENERIC_ROOT_CAUSE_BLACKLIST = (
    "整体", "不可信", "都不行",        # 原有
    "不靠谱", "不好用", "质量差", "效果差",
    "不够好", "有问题", "需要改进", "需要优化",
    "体验差", "性能差", "不稳定", "不完善",
    "设计差", "代码质量", "用户体验",
    "失败", "出错", "报错",            # 循环论证
)
```

现有 `staging_gate` 使用子串匹配，以上黑名单均为子串匹配，无需改动匹配逻辑。

### 2B. 新增 root_cause 归因审计日志

在 `learn()` 函数中，成功创建 Experience 后，写入专用事件：

```python
if root_cause:
    _write_event(conn, "root_cause_attribution", exp_id,
                 {"root_cause": root_cause, "task_id": task_id,
                  "result": result, "failure_mode": failure_mode or ""},
                 actor)
```

无需改 DDL —— events 表无 event_type 约束，`root_cause_attribution` 作为新事件类型自然生效。

### 2C. 新增 4 个运行时遥测函数

**`injection_hit_rate(conn=None) -> dict`**
- 统计有 root_cause 的 Experience 中被访问过的比例
- 代理指标：`accessed_at != created_at`（build_context 调 object_get 时会更新）
- 返回：`{total_experiences_with_rc, accessed_experiences_with_rc, hit_rate}`

**`root_cause_repeat_rate(conn=None) -> dict`**
- 统计同一 root_cause 跨 Experience 出现频率
- 返回：`{unique_root_causes, total_experiences, avg_repeat, max_repeat, distribution}`

**`rule_maturity_days(conn=None) -> dict`**
- 统计活跃 Rule 从创建至今的天数
- 返回：`{count, min_days, max_days, avg_days, rules}`

**`health_check(conn=None) -> dict`**
- 聚合以上三个遥测 + stats() 的快照
- 返回：`{status, object_count, event_count, rule_count, db_size_bytes, injection_hit_rate, root_cause_repeat, rule_maturity_days, last_event_at}`
- status: `"healthy"` (rule_count > 0) 或 `"warming"` (rule_count = 0)

### 2D. 测试

**T7: `test_root_cause_blacklist_expanded()`**
- 验证每条新增黑名单词被拒绝
- 验证合法 root_cause（"缺真实交易数据与信任徽章"）通过

**T8: `test_root_cause_audit_log()`**
- learn() 含 root_cause → 查询 events 表 → 验证 event_type='root_cause_attribution'
- 验证 events 表 append-only

**T9: `test_telemetry_and_health_check()`**
- seed TradeSpan → 调用 4 个新函数 → 验证返回值结构正确、数值合理

---

## 任务三：产品定位改口

### 修改文件

| 文件 | 行号 | 旧文本 | 新文本 |
|------|------|--------|--------|
| `README.md` | L3 | `**World-Class AI Company Operating System**` | `**Organizational Memory for One-Person Companies**` |
| `README.md` | L5 | `> 一个由人类 CEO 驱动、AI 员工执行...` | `> 一个人经营公司的记忆内核。把每一次失败变成下一次的上下文。` |
| `README.md` | L28-37 | 六层架构 (Layer 0-5) | 4+1+1 模型（来自 V1.1） |
| `dashboard/public/index.html` | L6 | `<title>Sera OPC OS — Control Center</title>` | `<title>Sera OPC OS — Memory Kernel</title>` |
| `dashboard/public/index.html` | L677 | `Control Center` | `Memory Kernel` |
| `architecture/v2/Sera-Context-Runtime-Learning-OS-V1.md` | L35 | `AI 公司认知循环系统` | `一人公司的组织记忆引擎` |

### 不改的文件

- 已标记 `Superseded` 的旧文档（`architecture/sera-agent-os-v1.md` 等）
- `CHANGELOG.md`（历史记录）
- `HANDOFF.md` / `MIGRATION_PLAN.md`（流程文档）
- Registry JSON（非产品面文本）
- `docs/SKILL-AUDIT-REPORT.md`（事实审计）

---

## 代码规范

Kernel 代码遵循现有约定：
- `conn=None` 参数 + `if conn is None: conn = _get_conn()` 模式
- 返回 dict，不抛异常
- 中文 docstring
- 仅 stdlib + sqlite3
- 使用 `_write_event()` 辅助函数，不直接写 INSERT
- 使用 `_now()` 获取时间戳

---

## 验证

```bash
cd /Users/a1234/projects/TraeWork/6a878c843f663f525fad70cd
python -m pytest core/sera_memory_kernel/test_kernel.py -v
# 期望：9/9 测试通过（原有 6 条 + 新增 3 条）

# 手动验证遥测函数
python -c "
from core.sera_memory_kernel import init_db, _get_conn, seed_tradespan, health_check, injection_hit_rate, root_cause_repeat_rate, rule_maturity_days
conn = _get_conn()
init_db(conn)
# seed 后验证
import json
print(json.dumps(health_check(conn), indent=2, ensure_ascii=False, default=str))
"
```