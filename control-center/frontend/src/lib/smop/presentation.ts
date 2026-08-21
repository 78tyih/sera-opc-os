import type { DataSource, ObjectType, RelationType } from "./types"

export const OBJECT_TYPE_COLOR: Record<ObjectType, string> = {
  Person: "#C9A84C",
  Company: "#C9A84C",
  Project: "#2DD4BF",
  Agent: "#0066FF",
  Skill: "#8A93A6",
  Workflow: "#2692FF",
  Decision: "#F59E0B",
  Experience: "#EF4444",
  Rule: "#A78BFA",
  Asset: "#8B96A8",
  Task: "#10B981",
}

export const OBJECT_TYPE_LABEL: Record<ObjectType, string> = {
  Person: "人",
  Company: "公司",
  Project: "项目",
  Agent: "智能体",
  Skill: "技能",
  Workflow: "工作流",
  Decision: "决策",
  Experience: "经验",
  Rule: "规则",
  Asset: "资产",
  Task: "任务",
}

export const RELATION_LABEL: Record<RelationType, string> = {
  owns: "拥有",
  owned_by: "被拥有",
  belongs_to: "属于",
  has_project: "拥有项目",
  manages: "管理",
  managed_by: "被管理",
  reports_to: "向…汇报",
  assigned_to: "分配给",
  depends_on: "依赖",
  required_by: "被需要",
  uses_skill: "使用技能",
  creates: "产出",
  part_of: "属于",
  led_to: "导致",
  learned_from: "从…学习",
  derived_from: "衍生自",
  supersedes: "替代",
  applies_to: "适用于",
  follows_decision: "遵循决策",
  follows_rule: "遵循规则",
  related_to: "关联",
  triggered: "触发",
  performed_by: "由…执行",
}

// 学习/进化类关系高亮——这是 Sera 区别于普通知识库的关键边
export const EVOLUTION_RELATIONS: RelationType[] = [
  "supersedes",
  "derived_from",
  "led_to",
  "follows_decision",
  "follows_rule",
]

export const RELATION_COLOR: Record<RelationType, string> = {
  owns: "#8A93A6",
  owned_by: "#8A93A6",
  belongs_to: "#6B7280",
  has_project: "#6B7280",
  manages: "#2692FF",
  managed_by: "#2692FF",
  reports_to: "#8A93A6",
  assigned_to: "#2692FF",
  depends_on: "#8A93A6",
  required_by: "#8A93A6",
  uses_skill: "#8A93A6",
  creates: "#10B981",
  part_of: "#6B7280",
  led_to: "#10B981",
  learned_from: "#10B981",
  derived_from: "#A78BFA",
  supersedes: "#EF4444",
  applies_to: "#F59E0B",
  follows_decision: "#F59E0B",
  follows_rule: "#A78BFA",
  related_to: "#8A93A6",
  triggered: "#8A93A6",
  performed_by: "#8A93A6",
}

export const DATA_SOURCE_COLOR: Record<DataSource, string> = {
  registry: "#0066FF",
  "agent-yaml": "#2692FF",
  constitution: "#C9A84C",
  spec: "#F59E0B",
}