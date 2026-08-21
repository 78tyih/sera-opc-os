"use client"

import { useState, useRef, useEffect } from "react"
import { motion } from "framer-motion"
import { Play, Pause, ZoomIn, ZoomOut, Info, ArrowRight } from "lucide-react"
import { useLang } from "@/lib/language-provider"
import workflowsData from "@/data/workflows.json"
import projectsData from "@/data/projects.json"

const NODE_ICONS: Record<string, string> = {
  package: "📦", search: "🔍", target: "🎯", palette: "🎨", globe: "🌐",
  "file-text": "📄", video: "🎬", rocket: "🚀", clock: "⏰", brain: "🧠",
  bell: "🔔", edit: "✏️", image: "🖼️", mic: "🎤", monitor: "🖥️", eye: "👁️",
  archive: "📁",
}

type NodeType = "input" | "process" | "output" | "gate"
const NODE_COLORS: Record<NodeType, string> = {
  input: "#10B981", process: "var(--brand)", output: "#8B5CF6", gate: "#F59E0B",
}

interface WorkflowNode {
  id: string; type: NodeType; label: string; agent: string; skill: string; status: string; icon: string
}
interface WorkflowEdge { source: string; target: string }
interface Workflow {
  id: string; name: string; description: string; status: string; lastRun: string
  nodes: WorkflowNode[]; edges: WorkflowEdge[]
}

const NODE_W = 130; const NODE_H = 56; const LAYER_GAP = 40
const NODE_GAP_X = 160; const NODE_GAP_Y = 100

function layoutNodes(nodes: WorkflowNode[]): Map<string, { x: number; y: number }> {
  const pos = new Map<string, { x: number; y: number }>()
  const layers: string[][] = []
  const remaining = new Set(nodes.map(n => n.id))

  while (remaining.size > 0) {
    const layer: string[] = []
    for (const id of remaining) {
      const hasIncoming = nodes.some(n => n.id !== id && remaining.has(n.id))
      if (!hasIncoming || [...remaining].every(rid => rid === id)) {
        layer.push(id)
      }
    }
    if (layer.length === 0) {
      layer.push([...remaining][0])
    }
    layers.push(layer)
    layer.forEach(id => remaining.delete(id))
  }

  layers.forEach((layer, li) => {
    layer.forEach((id, ni) => {
      const offsetX = (layer.length - 1) * NODE_GAP_X / 2
      pos.set(id, {
        x: 80 + ni * NODE_GAP_X - offsetX,
        y: 60 + li * NODE_GAP_Y,
      })
    })
  })

  return pos
}

function WorkflowCanvas({ workflow, selectedNode, onSelectNode }: {
  workflow: Workflow
  selectedNode: string | null
  onSelectNode: (id: string | null) => void
}) {
  const positions = layoutNodes(workflow.nodes)
  const allX = [...positions.values()].map(p => p.x)
  const allY = [...positions.values()].map(p => p.y)
  const minX = Math.min(...allX) - 80
  const maxX = Math.max(...allX) + 80 + NODE_W
  const minY = Math.min(...allY) - 40
  const maxY = Math.max(...allY) + 40 + NODE_H
  const svgW = Math.max(maxX - minX + 80, 600)
  const svgH = Math.max(maxY - minY + 80, 400)

  return (
    <svg
      width={svgW} height={svgH}
      className="w-full"
      style={{ background: "var(--bg-base)", borderRadius: "var(--radius)", minHeight: 400 }}
    >
      <defs>
        <pattern id="grid" width={30} height={30} patternUnits="userSpaceOnUse">
          <path d="M 30 0 L 0 0 0 30" fill="none" stroke="var(--border)" strokeWidth={0.5} opacity={0.4} />
        </pattern>
        <filter id="glow">
          <feGaussianBlur stdDeviation={4} result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />

      {/* Edges */}
      {workflow.edges.map((edge, i) => {
        const from = positions.get(edge.source)
        const to = positions.get(edge.target)
        if (!from || !to) return null
        const fromNode = workflow.nodes.find(n => n.id === edge.source)
        const isDone = fromNode?.status === "completed"
        return (
          <g key={i}>
            <line
              x1={from.x + NODE_W / 2} y1={from.y + NODE_H}
              x2={to.x + NODE_W / 2} y2={to.y}
              stroke={isDone ? "var(--success)" : "var(--border)"}
              strokeWidth={isDone ? 2 : 1.5}
              strokeDasharray={isDone ? "none" : "6 3"}
            />
            <ArrowRight
              className="w-3 h-3"
              style={{
                position: "absolute",
                left: to.x + NODE_W / 2 - 6,
                top: to.y - 6,
                color: isDone ? "var(--success)" : "var(--text-muted)",
              }}
            />
          </g>
        )
      })}

      {/* Nodes */}
      {workflow.nodes.map(node => {
        const pos = positions.get(node.id)
        if (!pos) return null
        const isSelected = selectedNode === node.id
        const isRunning = node.status === "running"
        const color = NODE_COLORS[node.type]
        const bg = isSelected ? "var(--brand-soft)" : "var(--bg-surface)"
        const border = isSelected ? "var(--brand)" : isRunning ? color : "var(--border)"

        return (
          <g
            key={node.id}
            onClick={() => onSelectNode(isSelected ? null : node.id)}
            style={{ cursor: "pointer" }}
          >
            <rect
              x={pos.x} y={pos.y}
              width={NODE_W} height={NODE_H}
              rx={10} ry={10}
              fill={bg}
              stroke={border}
              strokeWidth={isSelected || isRunning ? 2 : 1}
              filter={isRunning ? "url(#glow)" : undefined}
            />
            {/* Type indicator */}
            <rect
              x={pos.x} y={pos.y}
              width={4} height={NODE_H}
              rx={2}
              fill={color}
              style={{ clipPath: "inset(0 0 0 0 round 10px 0 0 10px)" }}
            />
            <text
              x={pos.x + NODE_W / 2}
              y={pos.y + 16}
              textAnchor="middle"
              fill="var(--text-primary)"
              style={{ fontSize: 11, fontWeight: 600 }}
            >
              {node.label}
            </text>
            <text
              x={pos.x + NODE_W / 2}
              y={pos.y + 34}
              textAnchor="middle"
              fill="var(--text-muted)"
              style={{ fontSize: 10 }}
            >
              {node.agent}
            </text>
            {/* Status badge */}
            <circle
              cx={pos.x + NODE_W - 8}
              cy={pos.y + 8}
              r={4}
              fill={node.status === "completed" ? "var(--success)" : node.status === "running" ? "var(--brand)" : "var(--text-muted)"}
            />
            {isRunning && (
              <circle
                cx={pos.x + NODE_W - 8}
                cy={pos.y + 8}
                r={8}
                fill="none"
                stroke="var(--brand)"
                strokeWidth={1}
                opacity={0.5}
              >
                <animate attributeName="r" from={8} to={14} dur="1.5s" repeatCount="indefinite" />
                <animate attributeName="opacity" from={0.5} to={0} dur="1.5s" repeatCount="indefinite" />
              </circle>
            )}
          </g>
        )
      })}
    </svg>
  )
}

export default function CanvasPage() {
  const { t } = useLang()
  const [selectedWf, setSelectedWf] = useState(0)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [inspectorWf, setInspectorWf] = useState<Workflow | null>(null)
  const workflows = workflowsData.workflows as Workflow[]
  const activeWf = workflows[selectedWf]
  const activeProject = projectsData[0] // 牛牛 AI

  const selectedNodeData = activeWf?.nodes.find(n => n.id === selectedNode)

  return (
    <div className="flex h-full">
      {/* Main Canvas Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <div className="flex items-center gap-4 px-6 py-4 border-b" style={{ borderColor: "var(--border)" }}>
          <div className="flex-1">
            <h1 className="text-lg font-bold" style={{ color: "var(--text-primary)" }}>
              {activeProject?.name || "牛牛 AI"} · 全球发射
              <span className="text-xs ml-2 font-normal" style={{ color: "var(--text-muted)" }}>PRJ-20260821-001</span>
            </h1>
            <div className="flex items-center gap-4 mt-1 text-xs" style={{ color: "var(--text-muted)" }}>
              <span>进度 <strong style={{ color: "var(--text-primary)" }}>{activeProject?.progress || 45}%</strong></span>
              <span>周期 <strong style={{ color: "var(--text-primary)" }}>D4/7</strong></span>
              <span>在编 <strong style={{ color: "var(--text-primary)" }}>5</strong></span>
              <span>预算 <strong style={{ color: "var(--text-primary)" }}>$800</strong></span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="w-8 h-8 flex items-center justify-center rounded-lg transition-all" style={{ color: "var(--text-muted)" }}>
              <ZoomIn className="w-4 h-4" />
            </button>
            <button className="w-8 h-8 flex items-center justify-center rounded-lg transition-all" style={{ color: "var(--text-muted)" }}>
              <ZoomOut className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Workflow selector */}
        <div className="flex gap-2 px-6 py-3 border-b" style={{ borderColor: "var(--border)" }}>
          {workflows.map((wf, i) => (
            <button
              key={wf.id}
              onClick={() => { setSelectedWf(i); setSelectedNode(null) }}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs transition-all"
              style={{
                background: i === selectedWf ? "var(--brand-soft)" : "transparent",
                color: i === selectedWf ? "var(--brand)" : "var(--text-muted)",
                border: i === selectedWf ? `1px solid var(--brand)` : "1px solid var(--border)",
              }}
            >
              <span className="w-1.5 h-1.5 rounded-full" style={{
                background: wf.status === "active" ? "var(--success)" : "var(--text-muted)",
              }} />
              {wf.name}
            </button>
          ))}
        </div>

        {/* SVG Canvas */}
        <div className="flex-1 overflow-auto p-6">
          <WorkflowCanvas
            workflow={activeWf}
            selectedNode={selectedNode}
            onSelectNode={setSelectedNode}
          />
          <p className="text-xs mt-3 text-center" style={{ color: "var(--text-muted)" }}>
            工作流由 Workflow OS 驱动；每个节点执行前经 Context Governor 注入公司记忆。
          </p>
        </div>
      </div>

      {/* Inspector Panel */}
      <div className="w-72 border-l shrink-0 flex flex-col" style={{ borderColor: "var(--border)", background: "var(--bg-surface)" }}>
        <div className="flex items-center gap-2 px-4 py-3 border-b" style={{ borderColor: "var(--border)" }}>
          <Info className="w-4 h-4" style={{ color: "var(--text-muted)" }} />
          <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-secondary)" }}>检查器</span>
        </div>

        {selectedNodeData ? (
          <div className="p-4 space-y-4">
            <div>
              <span className="text-[10px] uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>节点</span>
              <p className="text-sm font-bold mt-1" style={{ color: "var(--text-primary)" }}>{selectedNodeData.label}</p>
            </div>
            <div>
              <span className="text-[10px] uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>类型</span>
              <p className="text-sm mt-1" style={{ color: "var(--text-primary)" }}>{selectedNodeData.type}</p>
            </div>
            <div>
              <span className="text-[10px] uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>执行 Agent</span>
              <p className="text-sm mt-1" style={{ color: "var(--text-primary)" }}>{selectedNodeData.agent}</p>
            </div>
            <div>
              <span className="text-[10px] uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>技能</span>
              <p className="text-sm mt-1" style={{ color: "var(--text-primary)" }}>{selectedNodeData.skill}</p>
            </div>
            <div>
              <span className="text-[10px] uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>状态</span>
              <div className="flex items-center gap-2 mt-1">
                <span className="w-2 h-2 rounded-full" style={{
                  background: selectedNodeData.status === "completed" ? "var(--success)" : selectedNodeData.status === "running" ? "var(--brand)" : "var(--text-muted)"
                }} />
                <span className="text-sm capitalize" style={{ color: "var(--text-primary)" }}>{selectedNodeData.status}</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center p-4">
            <p className="text-xs text-center" style={{ color: "var(--text-muted)" }}>
              点击画布节点查看详情<br />
              每个节点代表一个工作流步骤
            </p>
          </div>
        )}
      </div>
    </div>
  )
}