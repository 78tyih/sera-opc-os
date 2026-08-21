// SMOP Context Package 编译算法
// 忠实实现 architecture/v2/Sera-Memory-Object-Protocol-V1.md 第五章 5.3「构建算法」

import { getAllObjects } from "./data"
import type { ContextPackage, Relation, SMOPObject } from "./types"

// Context 窗口预算（token）。含系统提示词 + 宪法基座 + 编译后的知识包。
const TOKEN_BUDGET = 12000
// Agent 系统提示词 + 宪法 + 创始人偏好 的基座 token 估算
const BASE_CONTEXT_TOKENS = 3200

const PRIORITY_WEIGHT: Record<string, number> = { critical: 4, high: 3, medium: 2, low: 1 }

function relsOf(o: SMOPObject | undefined): Relation[] {
  return o?.relations ?? []
}

function findTarget(o: SMOPObject | undefined, rel: string): string | undefined {
  return relsOf(o).find(r => r.relation === rel)?.target
}

function estimateTokens(obj: unknown): number {
  const json = JSON.stringify(obj)
  // 混排中英，按 1.8 字符 ≈ 1 token 粗估
  return Math.ceil(json.length / 1.8)
}

export function buildContextPackage(taskId: string): ContextPackage | null {
  const objects = getAllObjects()
  const task = objects.find(o => o.id === taskId && o.type === "Task")
  if (!task) return null

  const trace: string[] = []

  // ① 解析 Task → 项目 + 分配 Agent
  const projectId = findTarget(task, "part_of") ?? "company.sera"
  const agentId = findTarget(task, "assigned_to") ?? ""
  const project = objects.find(o => o.id === projectId)
  const agent = objects.find(o => o.id === agentId)
  trace.push(`① 解析任务「${task.name}」→ 项目「${project?.name ?? "-"}」· 分配「${agent?.name ?? "-"}」`)

  // ② 定位 Project
  const goal = (project?.properties.goal as string | undefined) ?? project?.description ?? ""
  trace.push(`② 定位项目：${project?.name ?? "-"}（${(project?.properties.category as string) ?? "-"} / ${project?.status ?? "-"}）`)

  const decisions = objects.filter(o => o.type === "Decision")
  const rules = objects.filter(o => o.type === "Rule")
  const experiences = objects.filter(o => o.type === "Experience")
  const assets = objects.filter(o => o.type === "Asset")
  const skills = objects.filter(o => o.type === "Skill")

  // ③ Decision：applies_to = project，过滤被 supersedes / 已 replaced
  const supersededIds = new Set(
    decisions.flatMap(d => relsOf(d).filter(r => r.relation === "supersedes").map(r => r.target)),
  )
  const allProjectDecisions = decisions.filter(d =>
    relsOf(d).some(r => r.relation === "applies_to" && r.target === projectId),
  )
  const activeDecisions = allProjectDecisions
    .filter(d => d.status === "active" && !supersededIds.has(d.id))
    .sort((a, b) => b.importance - a.importance)
  trace.push(`③ 决策：applies_to 命中 ${allProjectDecisions.length} 条，过滤 superseded/replaced 后剩 ${activeDecisions.length} 条`)

  // ④ Rule：applies_to = project 或 company，按优先级排序
  const activeRules = rules
    .filter(r => relsOf(r).some(x => x.relation === "applies_to" && (x.target === projectId || x.target === "company.sera")))
    .sort((a, b) => (PRIORITY_WEIGHT[b.properties.priority] ?? 1) - (PRIORITY_WEIGHT[a.properties.priority] ?? 1))
  trace.push(`④ 规则：命中 ${activeRules.length} 条（含公司级宪法规则）`)

  // ⑤ Experience：related_to = project（只保留有 lesson 的）
  const relevantExperiences = experiences
    .filter(e => relsOf(e).some(x => x.relation === "related_to" && x.target === projectId))
    .filter(e => !!e.properties.lesson)
    .sort((a, b) => b.importance - a.importance)
  trace.push(`⑤ 经验：related_to 命中 ${relevantExperiences.length} 条`)

  // ⑥ Asset：part_of = project
  const availableAssets = assets.filter(a => relsOf(a).some(x => x.relation === "part_of" && x.target === projectId))
  trace.push(`⑥ 资产：part_of 命中 ${availableAssets.length} 条`)

  // ⑦ Skill：agent.uses_skill
  const relevantSkills = skills.filter(s => relsOf(agent).some(r => r.relation === "uses_skill" && r.target === s.id))
  trace.push(`⑦ 技能：${agent?.name ?? "-"} uses_skill × ${relevantSkills.length}`)

  // ⑧ 标记 stale（被 supersedes 的决策）
  const staleInformation = decisions
    .filter(d => supersededIds.has(d.id))
    .map(d => {
      const by = decisions.find(x => relsOf(x).some(r => r.relation === "supersedes" && r.target === d.id))
      return {
        id: d.id,
        name: d.name,
        reason: "已被新决策 supersedes，注入时自动忽略",
        supersededBy: by?.id ?? "",
      }
    })
  trace.push(staleInformation.length ? `⑧ 标记 ${staleInformation.length} 条被 supersedes 的旧决策为 stale` : "⑧ 无 stale 信息（无被替代决策）")

  const view = {
    mission: {
      summary: (task.properties.summary as string) ?? task.name,
      project: project?.name ?? "",
      projectId,
      priority: (task.properties.priority as string) ?? "medium",
      status: (task.properties.status as string) ?? "in_progress",
    },
    projectContext: {
      name: project?.name ?? "",
      goal,
      status: project?.status ?? "",
      category: (project?.properties.category as string) ?? "",
    },
    activeDecisions: activeDecisions.map(d => ({
      id: d.id,
      decision: (d.properties.decision as string) ?? d.name,
      reason: (d.properties.reason as string) ?? "",
      constraints: (d.properties.constraints as string[]) ?? [],
      dataSource: d.dataSource,
      importance: d.importance,
    })),
    activeRules: activeRules.map(r => ({
      id: r.id,
      content: (r.properties.content as string) ?? r.name,
      priority: (r.properties.priority as "high" | "medium" | "low") ?? "low",
      scope: (r.properties.scope as string[]) ?? [],
      dataSource: r.dataSource,
    })),
    relevantExperiences: relevantExperiences.map(e => ({
      id: e.id,
      lesson: (e.properties.lesson as string) ?? e.name,
      appliesTo: (e.properties.scope as string[]) ?? [],
      importance: e.importance,
      dataSource: e.dataSource,
    })),
    availableAssets: availableAssets.map(a => ({
      id: a.id,
      name: a.name,
      type: (a.properties.format as string) ?? "asset",
      path: (a.properties.path as string) ?? "",
    })),
    relevantSkills: relevantSkills.map(s => ({
      id: s.id,
      name: s.name,
      proficiency: "required" as const,
    })),
    staleInformation,
  }

  const compiledTokens = estimateTokens(view)
  const tokenEstimate = BASE_CONTEXT_TOKENS + compiledTokens

  return {
    contextId: `ctx.${taskId}.${Date.now()}`,
    targetAgentId: agentId,
    targetAgentName: agent?.name ?? "",
    targetTaskId: taskId,
    compiledAt: new Date().toISOString(),
    ...view,
    tokenEstimate,
    tokenBudget: TOKEN_BUDGET,
    buildTrace: trace,
  }
}