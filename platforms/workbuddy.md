# WorkBuddy 接入

WorkBuddy 原生支持 Agent Skills，是 Sera OPC OS 的主阵地。

## Skill 目录

- **用户级**（所有项目可用）：`~/.workbuddy/skills/`
- **项目级**（仅当前项目）：`{workspace}/.workbuddy/skills/`

## 安装

```bash
# 方式 A：软链（推荐，git pull 后自动同步）
REPO=~/sera-opc-os
for d in "$REPO"/core/*/ "$REPO"/business/*/ "$REPO"/creative/*/ "$REPO"/adapters/*/; do
  [ -d "$d" ] && ln -sfn "$d" ~/.workbuddy/skills/$(basename "$d")
done

# 方式 B：一键脚本
./install.sh --platform workbuddy
```

## Router 调用

```bash
python3 ~/sera-agent-os/core/sera-agent-router/router.py "做一条 PropFirm.TV 视频"
```

WorkBuddy 的 Bash 工具可直接执行，输出 JSON 编排链后按序调度各 Skill。

## 与 Context Hub 集成

- `sera-context-system`（原 context-hub）遵循 `~/SeraContextHub/AGENT_CONTEXT_PROTOCOL.md`
- 工作区 `.workbuddy/memory/` 照常写；Hub 只收跨项目长期内容（双写原则）

## 注意

- 软链目标目录不存在时先 `mkdir -p ~/.workbuddy/skills`
- 重启 WorkBuddy 后新 Skill 生效
- 已有同名旧 Skill（如旧版 context-hub）需先删除，避免冲突
