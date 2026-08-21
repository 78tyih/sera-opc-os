# Trae 接入

Trae（字节跳动 AI IDE）支持 Agent Skills 标准格式。

## Skill 目录

- **项目级**：`.trae/skills/`（仓库内，推荐）
- **全局**：`~/.trae/skills/`（如需所有项目可用）

## 安装

```bash
# 项目级挂载（在目标项目仓库内）
REPO=~/sera-opc-os
mkdir -p .trae/skills
for d in "$REPO"/core/*/ "$REPO"/business/*/ "$REPO"/creative/*/ "$REPO"/adapters/*/; do
  [ -d "$d" ] && ln -sfn "$d" .trae/skills/$(basename "$d")
done

# 或一键脚本
./install.sh --platform trae
```

## Router 调用

Trae 内置终端，直接执行：

```bash
python3 ~/sera-agent-os/core/sera-agent-router/router.py "推送今天的 PropFirm 情报"
```

## 注意事项

- Trae 的 Agent 面板加载 `.trae/skills/` 下的 SKILL.md 作为能力
- 与 Trae 自身记忆体系（`~/.trae-cn/memory/`）双轨运行：Sera Registry 收跨平台能力，Trae 本地记忆照常
- 涉及 Windows 远程（sera-compute-control）时，Trae 内 Bash 需能访问 SSH 密钥（同 WorkBuddy 沙箱注意事项）
