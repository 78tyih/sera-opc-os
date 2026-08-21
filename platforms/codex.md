# Codex 接入

OpenAI Codex CLI 支持 Agent Skills 标准格式（SKILL.md + frontmatter）。

## Skill 目录

- **用户级**：`~/.codex/skills/`
- **项目级**：`.codex/skills/`（仓库内）

## 安装

```bash
# 软链用户级
REPO=~/sera-opc-os
mkdir -p ~/.codex/skills
for d in "$REPO"/core/*/ "$REPO"/business/*/ "$REPO"/creative/*/ "$REPO"/adapters/*/; do
  [ -d "$d" ] && ln -sfn "$d" ~/.codex/skills/$(basename "$d")
done

# 或一键脚本
./install.sh --platform codex
```

## Router 调用

Codex 内置 Bash，直接执行：

```bash
python3 ~/sera-agent-os/core/sera-agent-router/router.py "复盘这周的交易"
```

## 配置建议

在 `~/.codex/config.toml` 中授权 Bash 与文件读写：

```toml
[permissions]
allow = ["Bash(python3 *)", "Read", "Write"]
```

## 注意事项

- Codex 会话开始时读取 `~/SeraContextHub/AGENT_CONTEXT_PROTOCOL.md`（如存在）执行 SESSION START
- 凭证敏感操作（如 serawin SSH、企微推送）需用户确认，遵守各 SKILL.md 的 Iron Rules
