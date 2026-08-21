# 平台接入总览

Sera OPC OS 的 Skill Registry 是**平台无关**的。任何 Agent 只要遵循标准 SKILL.md 格式 + 正确的目录放置，即可加载全部能力。

```
Sera OPC OS Skill Registry（本仓库）
        │
        ├── WorkBuddy  → ~/.workbuddy/skills/         （原生）
        ├── Codex      → ~/.codex/skills/              （或项目 .codex/skills/）
        ├── Trae       → 项目 .trae/skills/            （或全局配置）
        ├── Claude Code→ ~/.claude/skills/             （原生）
        └── Cursor     → 项目 .cursor/skills/          （或 settings 指定）
```

## 快速开始

```bash
# 一键安装（交互式选择平台）
./install.sh

# 或指定平台
./install.sh --platform workbuddy
./install.sh --platform claude-code
./install.sh --platform codex
./install.sh --platform trae
./install.sh --platform cursor
./install.sh --all
```

## 各平台接入文档

| 平台 | 文档 | Skill 目录 | Router 调用 |
|---|---|---|---|
| WorkBuddy | [workbuddy.md](workbuddy.md) | `~/.workbuddy/skills/` | `python3 <repo>/core/sera-agent-router/router.py "<请求>"` |
| Codex | [codex.md](codex.md) | `~/.codex/skills/` | 同上（Codex 内置 Bash） |
| Trae | [trae.md](trae.md) | 项目 `.trae/skills/` | 同上（Trae 内置 Bash） |
| Claude Code | [claude-code.md](claude-code.md) | `~/.claude/skills/` | 同上（Claude Code 内置 Bash） |
| Cursor | [cursor.md](cursor.md) | 项目 `.cursor/skills/` | 同上（Cursor 内置 Bash） |

## 通用原则

1. **Skill 目录**：把 `core/ business/ creative/ adapters/` 下的 `*/SKILL.md` 以「目录」为单位挂载（每个 skill 是一个目录，含 SKILL.md）
2. **Agent 目录**：`agents/*/` 的 SKILL.md 是 Agent 角色卡，供编排器读取，不强制挂载为 skill
3. **Router**：所有平台共用同一 `router.py`（纯 stdlib），用 `python3` 调用即可，无需安装依赖
4. **Context Hub**：涉及 `sera-context-system` / `sera-state-manager` 时，各平台遵守 `~/SeraContextHub/AGENT_CONTEXT_PROTOCOL.md` 的 SESSION START/END
5. **更新**：`git pull` 后重新运行 `install.sh` 即可同步最新 Skill

## 依赖说明（Layer 0）

部分 Skill 标注了「平台依赖」或「依赖（Layer 0）」——这些来自 WorkBuddy 平台/Connector/Marketplace，各平台需要按官方方式安装对应插件，不从本仓库复制。详见根目录 `README.md` 的「依赖清单」。

## 安装脚本

`../install.sh` 支持 `--platform` 参数与交互选择，自动创建软链。Windows/无软链环境自动回退复制。
