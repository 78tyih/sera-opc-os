# Claude Code 接入

Anthropic Claude Code 原生支持 Agent Skills（SKILL.md + frontmatter name/description）。

## Skill 目录

- **个人级**：`~/.claude/skills/`
- **项目级**：`.claude/skills/`（仓库内）

## 安装

```bash
# 个人级软链
REPO=~/sera-agent-os
mkdir -p ~/.claude/skills
for d in "$REPO"/core/*/ "$REPO"/business/*/ "$REPO"/creative/*/ "$REPO"/adapters/*/; do
  [ -d "$d" ] && ln -sfn "$d" ~/.claude/skills/$(basename "$d")
done

# 或一键脚本
./install.sh --platform claude-code
```

## Router 调用

Claude Code 内置 Bash，直接执行：

```bash
python3 ~/sera-agent-os/core/sera-agent-router/router.py "帮我做 TradeSpan 产品发布页"
```

## 技能发现

Claude Code 通过 SKILL.md frontmatter 的 `name` + `description`（或 `purpose`）自动发现技能。本仓库所有 SKILL.md 均满足该格式，挂载后直接可用。

## 注意事项

- 每个 skill 目录必须包含 `SKILL.md`（本仓库已满足）
- 会话开始时执行 `sera-context-system` 的 SESSION START（读 `~/SeraContextHub/` 如存在）
- 敏感操作（SSH/推送/支付）遵守各 SKILL.md Iron Rules，需用户确认
