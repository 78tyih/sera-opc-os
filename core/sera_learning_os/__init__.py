"""Sera Learning OS runtime API."""

from .contradiction_export import export_contradictions_snapshot, render_contradictions_markdown
from .contradictions import init_contradiction_schema, list_contradictions, record_pattern_contradiction
from .daily_review import build_daily_review, render_daily_review_markdown
from .github_release_adapter import build_github_action_plan, validate_github_materialization_receipt
from .learning import (
    get_pattern,
    init_learning_schema,
    list_patterns,
    propose_skill_change,
    record_evaluation,
    record_raw_signal,
    upsert_pattern,
)
from .pipeline import process_learning_signal
from .portability import (
    assess_and_record_portability,
    assess_portability,
    init_portability_schema,
    list_portability_probes,
    record_portability_probe,
)
from .portability_export import export_portability_snapshot, render_portability_markdown
from .regression import (
    assess_release_readiness,
    init_regression_schema,
    list_regression_checks,
    record_regression_check,
    record_release_readiness,
)
from .release_controller import (
    build_pr_payload,
    current_release_state,
    get_release_request,
    init_release_schema,
    list_release_events,
    prepare_release_request,
    record_release_event,
)
from .shadow_patch import (
    generate_shadow_patch,
    get_shadow_patch,
    init_shadow_patch_schema,
    validate_shadow_baseline,
)
from .skill_proposer import propose_from_pattern, propose_ready_skills
from .wiki_export import export_context_hub_snapshot, render_pattern_markdown, render_proposal_markdown
from .wiki_maintainer import compile_signal_to_wiki, maintain_uncompiled_signals

__all__ = [
    "init_learning_schema", "record_raw_signal", "upsert_pattern", "propose_skill_change",
    "record_evaluation", "get_pattern", "list_patterns", "compile_signal_to_wiki",
    "maintain_uncompiled_signals", "process_learning_signal", "propose_from_pattern",
    "propose_ready_skills", "build_daily_review", "render_daily_review_markdown",
    "render_pattern_markdown", "render_proposal_markdown", "export_context_hub_snapshot",
    "init_contradiction_schema", "record_pattern_contradiction", "list_contradictions",
    "render_contradictions_markdown", "export_contradictions_snapshot",
    "init_portability_schema", "record_portability_probe", "list_portability_probes",
    "assess_portability", "assess_and_record_portability", "render_portability_markdown",
    "export_portability_snapshot", "init_shadow_patch_schema", "generate_shadow_patch",
    "get_shadow_patch", "validate_shadow_baseline", "init_regression_schema",
    "record_regression_check", "list_regression_checks", "assess_release_readiness",
    "record_release_readiness", "init_release_schema", "build_pr_payload",
    "prepare_release_request", "record_release_event", "get_release_request",
    "list_release_events", "current_release_state", "build_github_action_plan",
    "validate_github_materialization_receipt",
]
