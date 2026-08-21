import { createClient } from "@supabase/supabase-js"
import { readFileSync } from "fs"
import { join, dirname } from "path"
import { fileURLToPath } from "url"

const __dirname = dirname(fileURLToPath(import.meta.url))

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY

if (!supabaseUrl || !supabaseKey) {
  console.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
  process.exit(1)
}

const sb = createClient(supabaseUrl, supabaseKey, { auth: { persistSession: false } })

async function migrate() {
  console.log("Starting data migration...")

  // 1. Agents
  const agents = JSON.parse(readFileSync(join(__dirname, "../src/data/agents.json"), "utf-8"))
  for (const a of agents) {
    const { error } = await sb.from("agents").upsert({
      id: a.id,
      name: a.name,
      department: a.department,
      role: a.role,
      skills: a.skills,
      tools: a.tools,
      model: a.model,
      status: a.status,
      description: a.description,
    }, { onConflict: "id" })
    if (error) console.error(`Agent ${a.id}:`, error.message)
    else console.log(`  ✓ Agent: ${a.name}`)
  }

  // 2. Projects
  const projects = JSON.parse(readFileSync(join(__dirname, "../src/data/projects.json"), "utf-8"))
  for (const p of projects) {
    const { error } = await sb.from("projects").upsert({
      id: p.id,
      name: p.name,
      category: p.category,
      status: p.status,
      priority: p.priority,
      progress: p.progress,
      description: p.description,
      agent_ids: p.agents,
    }, { onConflict: "id" })
    if (error) console.error(`Project ${p.id}:`, error.message)
    else console.log(`  ✓ Project: ${p.name}`)
  }

  // 3. Workflows
  const { workflows } = JSON.parse(readFileSync(join(__dirname, "../src/data/workflows.json"), "utf-8"))
  for (const w of workflows) {
    const { error: wfErr } = await sb.from("workflows").upsert({
      id: w.id,
      name: w.name,
      description: w.description,
      status: w.status,
      last_run: w.lastRun,
    }, { onConflict: "id" })
    if (wfErr) { console.error(`Workflow ${w.id}:`, wfErr.message); continue }
    console.log(`  ✓ Workflow: ${w.name}`)

    // Delete existing nodes for this workflow, then re-insert
    await sb.from("workflow_nodes").delete().eq("workflow_id", w.id)

    for (const n of w.nodes || []) {
      const nodeId = `${w.id}-${n.id}`
      const { error: nErr } = await sb.from("workflow_nodes").upsert({
        id: nodeId,
        workflow_id: w.id,
        label: n.label,
        agent: n.agent,
        skill: n.skill || "",
        icon: n.icon || "",
        position_x: 0,
        position_y: 0,
      }, { onConflict: "id" })
      if (nErr) console.error(`  Node ${n.id}:`, nErr.message)
    }

    // Update edge references to use prefixed node IDs
    // Delete existing edges for this workflow, then re-insert
    await sb.from("workflow_edges").delete().eq("workflow_id", w.id)

    for (const e of w.edges || []) {
      const edgeId = `${w.id}-${e.source}-${e.target}`
      const { error: eErr } = await sb.from("workflow_edges").upsert({
        id: edgeId,
        workflow_id: w.id,
        source_node_id: `${w.id}-${e.source}`,
        target_node_id: `${w.id}-${e.target}`,
      }, { onConflict: "id" })
      if (eErr) console.error(`  Edge ${e.source}->${e.target}:`, eErr.message)
    }
  }

  // 4. Departments
  const departments = JSON.parse(readFileSync(join(__dirname, "../src/data/departments.json"), "utf-8"))
  for (const d of departments) {
    const { error } = await sb.from("departments").upsert({
      id: d.id,
      name: d.name,
      description: d.description,
      agent_ids: d.agents,
      project_ids: d.projects,
    }, { onConflict: "id" })
    if (error) console.error(`Department ${d.id}:`, error.message)
    else console.log(`  ✓ Department: ${d.name}`)
  }

  console.log("Migration complete!")
}

migrate().catch(console.error)