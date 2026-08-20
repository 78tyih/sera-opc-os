# Cursor 接入

Cursor（Anysphere AI IDE）通过规则文件加载 Agent Skills 标准格式。

## Skill 目录

- **项目级**：`.cursor/skills/`（推荐，随仓库分发）
- **全局**：`~/.cursor/skills/`（所有项目）

## 安装

```bash
# 项目级挂载
REPO=~/sera-agent-os
mkdir -p .cursor/skills
for d in "$REPO"/core/*/ "$REPO"/business/*/ "$REPO"/creative/*/ "$REPO"/adapters/*/; do
  [ -d "$d" ] && ln -sfn "$d" .cursor/skills/$(basename "$d")
done

# 或一键脚本
./install.sh --platform cursor
```

## Router 调用

Cursor 内置终端，直接执行：

```bash
python3 ~/sera-agent-os/core/sera-agent-router/router.py "设计一个品牌海报"
```

## 注意事项

- Cursor Rules（`.cursor/rules/`）可补充：声明 Sera Registry 路径与 Router 调用约定
- Agent 模式（Composer）下可指定挂载 Skill 作为上下文
- 与 Cursor 自身 memory 双轨运行，Sera Registry 收跨平台能力
