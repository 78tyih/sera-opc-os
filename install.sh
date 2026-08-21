#!/bin/bash
# Sera OPC OS — 一键安装脚本
# 把 Skill Registry 挂载到指定 AI 平台的 skills 目录
#
# 用法：
#   ./install.sh                  # 交互式选择平台
#   ./install.sh --all            # 安装到所有平台
#   ./install.sh --platform workbuddy|codex|trae|claude-code|cursor
#   ./install.sh --repo <path>    # 指定仓库路径（默认脚本所在目录）
#   ./install.sh --copy           # 用复制代替软链（Windows/无软链环境）
#
set -euo pipefail

# 仓库路径
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="symlink"
PLATFORMS_ALL="workbuddy codex trae claude-code cursor"

# ---- 解析参数 ----
REQUESTED=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) REQUESTED="$PLATFORMS_ALL" ;;
    --platform) REQUESTED="$2"; shift ;;
    --repo) REPO="$2"; shift ;;
    --copy) MODE="copy" ;;
    -h|--help) grep "^#" "$0" | head -20; exit 0 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
  shift
done

# ---- 平台目录映射 ----
dir_for() {
  case "$1" in
    workbuddy)  echo "$HOME/.workbuddy/skills" ;;
    codex)      echo "$HOME/.codex/skills" ;;
    trae)       echo "$HOME/.trae/skills" ;;
    claude-code) echo "$HOME/.claude/skills" ;;
    cursor)     echo "$HOME/.cursor/skills" ;;
    *) echo "" ;;
  esac
}

# ---- 挂载单个 skill 目录 ----
mount_skill() {
  local src="$1" dest="$2"
  local name
  name="$(basename "$src")"
  if [[ "$MODE" == "symlink" ]] && ln -sfn "$src" "$dest/$name" 2>/dev/null; then
    echo "  ✓ symlink  $name"
  else
    mkdir -p "$dest/$name"
    cp -r "$src/." "$dest/$name/"
    echo "  ✓ copy     $name"
  fi
}

# ---- 挂载一个平台 ----
install_platform() {
  local platform="$1"
  local dest
  dest="$(dir_for "$platform")"
  if [[ -z "$dest" ]]; then
    echo "✗ 未知平台: $platform"; return 1
  fi

  echo "==> 安装到 $platform → $dest"
  mkdir -p "$dest"

  local count=0
  for group in core business creative adapters; do
    for d in "$REPO/$group"/*/; do
      # 跳过非 skill 目录（如 router 的 workflows 子目录）
      [[ -f "$d/SKILL.md" ]] || continue
      mount_skill "$d" "$dest"
      count=$((count+1))
    done
  done
  echo "  ✔ $platform: $count 个 Skill 已挂载"
}

# ---- 交互选择 ----
if [[ -z "$REQUESTED" ]]; then
  echo "选择要安装的平台："
  select p in $PLATFORMS_ALL "全部" "退出"; do
    case "$p" in
      退出) exit 0 ;;
      全部) REQUESTED="$PLATFORMS_ALL"; break ;;
      *) REQUESTED="$p"; break ;;
    esac
  done
fi

echo "Sera OPC OS Installer"
echo "  仓库: $REPO"
echo "  模式: $MODE"
echo ""

for p in $REQUESTED; do
  install_platform "$p"
done

echo ""
echo "✔ 完成。各平台接入文档见: $REPO/platforms/"
echo "  Router 快速验证: python3 $REPO/core/sera-agent-router/router.py --test"
