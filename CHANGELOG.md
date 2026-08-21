# Changelog

## V2.0 (2026-08-21)

### 🏗️ 架构升级
- 从 `sera-agent-os` V1.1 升级为 `sera-opc-os` V2.0
- 引入六层架构：Constitution → Organization → Factory → Employee → Learning → Autonomous
- 新增 12 个顶层目录：constitution/, vision/, strategy/, organization/, executive/, departments/, skills/, workflows/, factories/, revenue/, router/, evolution/

### 📄 蓝图文档
- 01-Blueprint.md — 公司级设计规范
- 02-Repo-Spec.md — GitHub 工程规范
- 03-Factory-Blueprint.md — 生产系统设计
- 04-Employee-Blueprint.md — 首批 50 名员工目录

### 🧠 公司宪法
- 新增 company-constitution.md
- 新增 operating-principles.md
- 新增 decision-framework.md

### 🏛️ 组织系统
- 新增 company-map.yaml
- 新增 benchmark-library.md
- 新增 Executive Council 定义

### 🔄 保留内容
- 保留 `sera-agent-os` 全部现有代码和配置
- 保留 `core/`, `runtime/`, `adapters/`, `portfolio/`, `registry/`, `memory/`, `evaluation/`
- 保留 `agents/`, `business/`, `creative/`, `product/`, `control-center/`, `platforms/`