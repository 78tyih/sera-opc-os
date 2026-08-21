// Sera Memory Object Protocol (SMOP) — 前端类型定义
// 忠实映射 architecture/v2/Sera-Memory-Object-Protocol-V1.md

export type ObjectType =
  | "Person"
  | "Company"
  | "Project"
  | "Agent"
  | "Skill"
  | "Workflow"
  | "Decision"
  | "Experience"
  | "Rule"
  | "Asset"
  | "Task"

export type DataSource = "registry" | "agent-yaml" | "constitution" | "spec"

export type ObjectStatus = "active" | "draft" | "archived" | "deprecated" | "replaced"

export type RelationType =
  | "owns"
  | "owned_by"
  | "belongs_to"
  | "has_project"
  | "manages"
  | "managed_by"
  | "reports_to"
  | "assigned_to"
  | "depends_on"
  | "required_by"
  | "uses_skill"
  | "creates"
  | "part_of"
  | "led_to"
  | "learned_from"
  | "derived_from"
  | "supersedes"
  | "applies_to"
  | "follows_decision"
  | "follows_rule"
  | "related_to"
  | "triggered"
  | "performed_by"

export interface Relation {
  source: string
  relation: RelationType
  target: string
  weight: number
}

export interface SMOPObject {
  id: string
  type: ObjectType
  name: string
  description: string
  status: ObjectStatus
  importance: number
  confidence: number
  owner: string
  dataSource: DataSource
  properties: Record<string, any>
  relations: Relation[]
}

export interface DecisionView {
  id: string
  decision: string
  reason: string
  constraints: string[]
  dataSource: DataSource
  importance: number
}

export interface RuleView {
  id: string
  content: string
  priority: "high" | "medium" | "low"
  scope: string[]
  dataSource: DataSource
}

export interface ExperienceView {
  id: string
  lesson: string
  appliesTo: string[]
  importance: number
  dataSource: DataSource
}

export interface AssetView {
  id: string
  name: string
  type: string
  path: string
}

export interface SkillView {
  id: string
  name: string
  proficiency: "required" | "recommended"
}

export interface StaleView {
  id: string
  name: string
  reason: string
  supersededBy: string
}

export interface ContextPackage {
  contextId: string
  targetAgentId: string
  targetAgentName: string
  targetTaskId: string
  compiledAt: string
  mission: {
    summary: string
    project: string
    projectId: string
    priority: string
    status: string
  }
  projectContext: {
    name: string
    goal: string
    status: string
    category: string
  }
  activeDecisions: DecisionView[]
  activeRules: RuleView[]
  relevantExperiences: ExperienceView[]
  availableAssets: AssetView[]
  relevantSkills: SkillView[]
  staleInformation: StaleView[]
  tokenEstimate: number
  tokenBudget: number
  buildTrace: string[]
}