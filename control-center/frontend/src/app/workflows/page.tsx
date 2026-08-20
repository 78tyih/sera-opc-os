"use client"

import { useCallback, useMemo, useState } from "react"
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
  type NodeProps,
  type Edge,
  type Node,
  useNodesState,
  useEdgesState,
} from "@xyflow/react"
import "@xyflow/react/dist/style.css"
import { motion } from "framer-motion"
import { Play, Pause, RotateCcw, Clock, CheckCircle2, Loader2, Bot, Package, Search, Target, Palette, Globe, FileText, Video, Rocket, Bell, Brain, Edit, Image, Mic, Monitor, Eye, Archive } from "lucide-react"
import { useLang } from "@/lib/language-provider"
import workflowsData from "@/data/workflows.json"

const iconMap: Record<string, React.ElementType> = {
  package: Package, search: Search, target: Target, palette: Palette,
  globe: Globe, "file-text": FileText, video: Video, rocket: Rocket,
  bell: Bell, brain: Brain, edit: Edit, image: Image, mic: Mic,
  monitor: Monitor, eye: Eye, archive: Archive, clock: Clock,
}

const statusIcons: Record<string, React.ElementType> = {
  completed: CheckCircle2,
  running: Loader2,
  pending: Clock,
}

type WorkflowNodeData = {
  label: string
  agent: string
  skill: string
  status: string
  icon: string
}

type WorkflowNodeType = Node<WorkflowNodeData, 'workflowNode'>

function WorkflowNode({ data }: NodeProps<WorkflowNodeType>) {
  const StatusIcon = statusIcons[data.status] || Clock
  const NodeIcon = iconMap[data.icon] || Bot

  return (
    <div className={`workflow-node ${data.status} px-4 py-3 min-w-[180px]`}>
      <Handle type="target" position={Position.Top} style={{ background: "var(--border-strong)", width: 8, height: 8, border: "2px solid var(--bg-base)" }} />
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0`}
          style={{
            background: data.status === "completed" ? "rgba(16, 185, 129, 0.1)" :
                        data.status === "running" ? "var(--brand-soft)" : "var(--bg-surface-hover)"
          }}>
          <NodeIcon className="w-4 h-4" style={{
            color: data.status === "completed" ? "var(--success)" :
                   data.status === "running" ? "var(--brand)" : "var(--text-muted)"
          }} />
        </div>
        <div className="min-w-0">
          <div className="text-sm font-medium truncate" style={{ color: "var(--text-primary)" }}>{data.label}</div>
          <div className="text-[10px] truncate" style={{ color: "var(--text-muted)" }}>{data.agent}</div>
        </div>
        <div className="shrink-0">
          <StatusIcon className="w-4 h-4" style={{
            color: data.status === "completed" ? "var(--success)" :
                   data.status === "running" ? "var(--brand)" : "var(--text-muted)"
          }} />
        </div>
      </div>
      <div className="mt-2 flex items-center gap-1.5">
        <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "var(--bg-surface-hover)", color: "var(--text-muted)", border: "1px solid var(--border)" }}>
          {data.skill}
        </span>
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: "var(--border-strong)", width: 8, height: 8, border: "2px solid var(--bg-base)" }} />
    </div>
  )
}

const nodeTypes = { workflowNode: WorkflowNode }

function WorkflowCanvas({ workflow }: { workflow: typeof workflowsData.workflows[0] }) {
  const initialNodes: WorkflowNodeType[] = useMemo(() => workflow.nodes.map((n) => ({
    id: n.id,
    type: 'workflowNode' as const,
    position: { x: 0, y: 0 },
    data: { label: n.label, agent: n.agent, skill: n.skill, status: n.status, icon: n.icon },
  })), [workflow.nodes])

  const initialEdges: Edge[] = useMemo(() => workflow.edges.map(e => ({
    id: `${e.source}-${e.target}`,
    source: e.source,
    target: e.target,
    style: { stroke: "var(--border-strong)", strokeWidth: 2 },
    animated: true,
    type: "smoothstep",
  })), [workflow.edges])

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onLayout = useCallback(() => {
    const spacing = { x: 280, y: 160 }
    const layers: { id: string; label: string }[][] = []
    let currentLayer: { id: string; label: string }[] = []
    const visited = new Set<string>()

    const hasIncoming = new Set(workflow.edges.map(e => e.target))
    workflow.nodes.forEach(n => {
      if (!hasIncoming.has(n.id)) {
        currentLayer.push({ id: n.id, label: n.label })
        visited.add(n.id)
      }
    })
    layers.push([...currentLayer])

    while (visited.size < workflow.nodes.length) {
      const nextLayer: { id: string; label: string }[] = []
      currentLayer.forEach(n => {
        workflow.edges.filter(e => e.source === n.id).forEach(e => {
          if (!visited.has(e.target)) {
            nextLayer.push({ id: e.target, label: workflow.nodes.find(wn => wn.id === e.target)?.label || e.target })
            visited.add(e.target)
          }
        })
      })
      if (nextLayer.length === 0) break
      layers.push(nextLayer)
      currentLayer = nextLayer
    }

    const newNodes = nodes.map(node => {
      for (let y = 0; y < layers.length; y++) {
        const x = layers[y].findIndex(l => l.id === node.id)
        if (x !== -1) {
          const totalWidth = (layers[y].length - 1) * spacing.x
          return { ...node, position: { x: totalWidth / 2 - (layers[y].length - 1 - x) * spacing.x / 2 + 300, y: y * spacing.y + 80 } }
        }
      }
      return node
    })
    setNodes(newNodes)
  }, [nodes, workflow])

  setTimeout(onLayout, 100)

  return (
    <div className="h-[500px] rounded-xl border overflow-hidden" style={{ borderColor: "var(--border)" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.3}
        maxZoom={2}
        defaultEdgeOptions={{ type: "smoothstep", style: { stroke: "var(--border-strong)", strokeWidth: 2 }, animated: true }}
      >
        <Background color="var(--border)" gap={20} size={1} />
        <Controls style={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8 }} />
        <MiniMap
          style={{ background: "var(--bg-surface)", border: "1px solid var(--border)", borderRadius: 8 }}
          nodeColor="var(--brand)"
          maskColor="rgba(11, 15, 25, 0.8)"
        />
      </ReactFlow>
    </div>
  )
}

export default function WorkflowsPage() {
  const { t } = useLang()
  const [activeWorkflow, setActiveWorkflow] = useState(workflowsData.workflows[0])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>{t("workflows.title")}</h1>
          <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>{t("workflows.subtitle")}</p>
        </div>
        <div className="flex items-center gap-2">
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            className="btn-brand flex items-center gap-2 px-3 py-2 text-sm">
            <Play className="w-4 h-4" /> {t("workflows.run")}
          </motion.button>
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
            style={{ background: "var(--bg-surface)", color: "var(--text-primary)", border: "1px solid var(--border)" }}>
            <Pause className="w-4 h-4" /> {t("workflows.pause")}
          </motion.button>
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            className="p-2 rounded-lg transition-colors"
            style={{ background: "var(--bg-surface)", border: "1px solid var(--border)" }}>
            <RotateCcw className="w-4 h-4" style={{ color: "var(--text-muted)" }} />
          </motion.button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {workflowsData.workflows.map(wf => (
          <button
            key={wf.id}
            onClick={() => setActiveWorkflow(wf)}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={{
              background: activeWorkflow.id === wf.id ? "var(--brand-soft)" : "var(--bg-surface)",
              color: activeWorkflow.id === wf.id ? "var(--brand)" : "var(--text-muted)",
              border: activeWorkflow.id === wf.id ? "1px solid rgba(0,102,255,0.2)" : "1px solid var(--border)",
            }}
          >
            {wf.name}
          </button>
        ))}
      </div>

      <div className="flex items-center justify-between text-sm">
        <span style={{ color: "var(--text-muted)" }}>{activeWorkflow.description}</span>
        <span className="flex items-center gap-1" style={{ color: "var(--text-muted)" }}>
          <Clock className="w-3.5 h-3.5" />
          {t("workflows.last-run")}: {new Date(activeWorkflow.lastRun).toLocaleString()}
        </span>
      </div>

      <WorkflowCanvas workflow={activeWorkflow} />

      <div className="flex items-center gap-6 text-xs" style={{ color: "var(--text-muted)" }}>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full" style={{ background: "var(--success)" }} /> {t("workflows.completed")}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full" style={{ background: "var(--brand)" }} /> {t("workflows.running")}
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full" style={{ background: "var(--border-strong)" }} /> {t("workflows.pending")}
        </span>
      </div>
    </div>
  )
}