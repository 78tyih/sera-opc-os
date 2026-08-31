# hx-skill + MarketUI skill — 2026-08-31 Update Intake

## Intake status

- Source type: HTX internal skill announcement + restricted Wiki documentation.
- Registered on: 2026-08-31.
- Public-repo state: metadata only.
- Detailed extraction: pending authorized access to the internal documentation.

## User-provided release information

The latest versions of both `hx-skill` and `MarketUI skill` were announced on 2026-08-31. The announcement states that this release can cover roughly **80% of daily work** and recommends that existing users re-download/update both skills.

Evidence class: `user_reported`.

This statement is retained as release context only. It is **not** treated as a measured benchmark score.

## References

### hx-skill / 火效

- Organization: HTX internal.
- Documentation: restricted internal Wiki.
- Public repository policy: original URL and content are intentionally not mirrored here.
- Current state: registered for later capability extraction and comparison.

### MarketUI skill

- Organization: HTX internal.
- Documentation: restricted internal Wiki.
- Public repository policy: original URL and content are intentionally not mirrored here.
- Current state: registered for later capability extraction and comparison.

## What to extract when authenticated access is available

For each skill, extract the following without copying confidential examples verbatim:

1. Trigger conditions — when the skill should or should not run.
2. Input contract — required project context, files, URLs or prompts.
3. Workflow stages — analysis, generation, review, handoff and update loops.
4. Design decision model — how it chooses layout, style, components and hierarchy.
5. Component model — reusable patterns or higher-level composites.
6. Safety/quality gates — constraints that make the skill safe for daily use.
7. Output contract — files, artifacts, code, prompts or design specs produced.
8. Update model — how previously installed versions should be refreshed.
9. Failure modes — what the skill refuses, escalates or leaves unresolved.
10. Generalizable rules — which ideas belong in Sera and which must remain HTX-specific.

## Comparison matrix to complete later

| Dimension | hx-skill | MarketUI | Sera Design Intelligence |
|---|---|---|---|
| Trigger / routing | Pending | Pending | Existing Style Router + workflow triggers |
| Evidence-first extraction | Pending | Pending | Yes |
| Design system generation | Pending | Pending | Yes |
| Component retrieval | Pending | Pending | Yes, semantic composite registry |
| Template productization | Pending | Pending | Yes |
| Design review gate | Pending | Pending | Yes |
| Living benchmark / drift | Pending | Pending | Yes |
| Internal daily-work safety rules | Pending | Pending | Partial; compare after document access |

## Merge policy

Do **not** blindly copy either skill into Sera.

Use this sequence:

```text
Read → Extract → Normalize → Compare → Conflict Review → Portability Review
→ Adopt / Adapt / Reject → Test → Promote
```

A strong internal practice can become a Sera-native rule only when it is sufficiently generic, safe to retain, and does not depend on confidential company data or infrastructure.
