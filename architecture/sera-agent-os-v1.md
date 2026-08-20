# Sera Agent OS Architecture V1.0

- **Version**: 1.0
- **Date**: 2026-08-21
- **Author**: Sera
- **Purpose**: Design a cross-agent personal AI operating system.

## Compatible Agents

- WorkBuddy
- Codex
- Trae
- Claude Code
- Cursor
- Future Agent Systems

---

## 1. Vision

Sera Agent OS is a personal AI operating system. Its purpose: transform isolated AI tools into a unified personal intelligence system.

The system separates:

1. Intelligence Layer
2. Memory Layer
3. Skill Layer
4. Execution Layer
5. Platform Adapter Layer

The goal: **"Build once, execute everywhere."**

A Skill should not belong to WorkBuddy, Codex, Trae, or any single AI platform. **A Skill belongs to Sera Agent OS.**

---

## 2. Core Philosophy

### Traditional AI Workflow

```
User → ChatGPT → One conversation → Discarded knowledge
```

Problems: no memory · no reuse · no workflow inheritance · no cross-agent collaboration.

### Sera Agent OS

```
User → Agent Router → Skill Registry → Domain Expert → Execution Runtime → Knowledge Update
```

Result: every AI agent becomes a worker inside the same operating system.

---

## 3. System Architecture

```
                    Sera Agent OS
                         User
                          |
                          ↓
              Agent Orchestrator Layer
                    |
        ----------------------------
        |            |             |
   Codex        WorkBuddy       Trae
        ----------------------------
                          |
                          ↓
              Skill Registry Layer
                          |
        --------------------------------
        Core Skills | Business Skills | Creative Skills | Platform Skills
                          |
                          ↓
              Memory System
                          |
        --------------------------------
        Obsidian Vault | Context Hub | Project State | Decision Logs
                          |
                          ↓
              Compute Layer
        Mac | Serawin | Cloud GPU | API Services
```

---

## 4. Core System Layer

### 4.1 Agent Orchestrator — `sera-agent-orchestrator`

Manage: task routing · agent selection · skill selection · execution planning · conflict detection.

Example — User: "Create PropFirm TV video"

Router: 1. propfirm-product-manager → 2. content-factory → 3. video-pipeline → 4. serawin-compute → 5. obsidian-sync

Output: completed production package.

### 4.2 Memory System — `sera-memory-system`

Create shared intelligence memory.

Components:
- **Context Hub**: user preferences, system rules, active projects
- **Obsidian Knowledge Base**: reports, documents, decisions, research
- **Project Memory**: current status, next actions, historical decisions

Principle: *"Agents forget. Systems remember."*

### 4.3 Skill Registry — `sera-skill-registry`

Manage all capabilities. Every Skill follows `SKILL.md` structure:

`name · description · purpose · inputs · outputs · workflow · dependencies · examples · version`

---

## 5. Core Skill Layer

### 5.1 Compute Control — `sera-compute-control`

Control physical execution machines.

```
Mac → Tailscale → Serawin Windows → ComfyUI → Generated Assets
```

Capabilities: SSH · remote execution · GPU workload · file transfer

### 5.2 Knowledge Sync — `sera-knowledge-sync`

Synchronize AI output → Obsidian → Knowledge Base.

Capabilities: markdown archive · duplicate detection · folder routing · metadata generation

---

## 6. Business Intelligence Layer

### 6.1 PropFirm Intelligence — `sera-intelligence-monitor`

Monitor: PropFirm rules · promotions · competitor changes · market intelligence.

Pipeline: `Collector → Parser → Classifier → Report → Notification`

### 6.2 PropFirm Product Manager — `sera-propfirm-product-manager`

Expert knowledge: product design · pricing · competitor analysis · user research · landing page strategy

### 6.3 OTC BD Agent — `sera-otc-bd-agent`

Handle: customer qualification · communication · pricing strategy · risk assessment · CRM workflow

### 6.4 Trading Research Agent — `sera-trading-research`

Analyze: market structure · trading strategies · ATAS · order flow · quantitative research

---

## 7. Creative Production Layer

### 7.1 Content Factory — `sera-content-factory`

Website/product material generation.

```
Website Capture → Brand Extraction → Scene Planning → Asset Generation → Library Storage
```

### 7.2 Video Pipeline — `sera-video-pipeline`

AI video production.

```
Script → Storyboard → Voice → Digital Human → Animation → Editing → Publishing
```

Tools: HeyGen · ElevenLabs · HyperFrames · Flova

### 7.3 Design Studio — `sera-design-studio`

Unified design intelligence.

Capabilities: UI design · poster · presentation · branding · Figma review

---

## 8. Platform Adapter Layer

Adapters are not core intelligence. They connect external services.

Examples: `sera-lark-suite` · `sera-wecom-suite` · `sera-github` · `sera-browser-automation` · `sera-mail-hub`

---

## 9. Skill Development Rules

Every new Skill must contain `SKILL.md` with:

1. Purpose
2. When to use
3. Input
4. Output
5. Workflow
6. Dependencies
7. Examples

---

## 10. Repository Structure

```
sera-agent-os/
├── README.md
├── architecture/
│   └── sera-agent-os-v1.md
├── core/
│   ├── agent-orchestrator
│   ├── memory-system
│   ├── skill-registry
│   └── compute-control
├── business/
│   ├── propfirm-manager
│   ├── otc-bd
│   ├── intelligence-monitor
│   └── trading-research
├── creative/
│   ├── content-factory
│   ├── video-pipeline
│   └── design-studio
├── adapters/
│   ├── lark
│   ├── github
│   ├── gmail
│   └── browser
└── templates/
    ├── SKILL.template.md
    └── workflow.yaml
```

---

## 11. Development Roadmap

- **Phase 1**: Create Repository — generate Core Skills, README, Templates
- **Phase 2**: Extract personal Skills from WorkBuddy — priority: context-hub, obsidian-sync, serawin-remote, propfirm-feed, video pipeline, content factory
- **Phase 3**: Create Domain Experts — PropFirm PM, OTC BD, Trading Analyst, AI Video Producer, Design Reviewer
- **Phase 4**: Connect Codex, Trae, WorkBuddy, Claude into the same Skill Registry

---

## Final Goal

Sera Agent OS becomes **a personal AI operating system** — not a collection of prompts, not a collection of tools, but **a living intelligence infrastructure**.
