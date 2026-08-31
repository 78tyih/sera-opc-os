# Workflow — Package a Real Project as a Reusable Design Template

## Trigger

Use this workflow when a completed or mature product/site/dashboard has reusable design value and should become a Sera Design Intelligence asset.

Examples:
- “把这个网页打包成 Skill / Template”
- “把这个项目的视觉系统沉淀下来”
- “这个设计以后想复用/售卖”
- “把这个项目写进模板库”

## Goal

Convert a real project into four connected outputs:

1. Case Study
2. Style / Design DNA
3. Reusable Template
4. Agent Skill

## Step 1 — Inspect the real artifact

Collect evidence from:
- deployed URL
- source repository
- screenshots
- existing design docs
- data schema
- interaction logic

Do not infer the design system only from screenshots when source code is available.

## Step 2 — Separate project-specific vs reusable

Create two buckets.

### Project-specific
- company/brand name
- confidential data
- customer information
- internal KPIs
- proprietary business language
- one-off operational constraints

### Reusable
- information architecture
- layout patterns
- tokens
- component anatomy
- interaction patterns
- hierarchy rules
- state semantics
- motion language
- content sequencing

Only reusable material may enter the public/template layer.

## Step 3 — Define the problem statement

A template must answer:

- Who is it for?
- What problem does it solve?
- What does the user understand faster because of this design?
- What action does the design help them take?

Reject “looks premium” as the only value proposition.

## Step 4 — Extract Design DNA

Capture at minimum:
- color roles
- typography hierarchy
- spacing system
- radius and shadow
- density
- container width
- navigation model
- card model
- status semantics
- motion and hover behavior
- light/dark theme behavior if present

Register or update the style in `styles/registry.json`.

## Step 5 — Extract Information Architecture

Document the module order and the reason for that order.

For each module record:
- user question answered
- information priority
- expected data
- primary interaction
- optional vs required

## Step 6 — Build a neutral Demo

Replace the original business with a different scenario.

A valid demo must prove transferability.

Bad demo:
- same company, fake numbers
- same industry with names changed

Good demo:
- OTC dashboard → AI product launch dashboard
- financial service landing → compliance SaaS service page

## Step 7 — Write SKILL.md

The skill should tell an Agent:
- when to use the pattern
- when not to use it
- required information architecture
- visual rules
- component rules
- state semantics
- output checklist
- anti-patterns

The skill should be executable, not descriptive prose only.

## Step 8 — Register the Template

Add entry to:

`template-library/registry.json`

Required fields:
- id
- name
- source_project
- source_repo
- style_ref
- target_users
- problems_solved
- core_modules
- commercial_formats
- status

## Step 9 — Package commercial variants

Evaluate four deliverables:

### Style Pack
Design DNA + prompt + tokens.

### Template Pack
Demo + docs + replaceable content/data structure.

### Skill Pack
Agent-ready SKILL.md.

### Solution Pack
Template + Skill + schema + integration guide.

## Step 10 — Review

Before publishing, verify:

- [ ] No confidential data
- [ ] No private customer/user information
- [ ] No original brand dependency in the reusable core
- [ ] Demo works in an unrelated scenario
- [ ] At least 3 reusable components exist
- [ ] Information architecture has a clear business purpose
- [ ] Style is registered
- [ ] Template is registered
- [ ] Skill is executable
- [ ] Source project remains referenced as evidence

## Output rule

Every mature design project should end in one of three states:

1. **Archive only** — not reusable enough.
2. **Pattern only** — useful component/style lessons, but not a full template.
3. **Template product** — reusable + demo-proven + skill-ready + commercially packageable.

Do not force every project into a product.