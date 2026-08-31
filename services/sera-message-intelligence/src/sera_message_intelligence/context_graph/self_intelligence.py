from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from sera_message_intelligence.llm.client import StructuredLLM
from sera_message_intelligence.models import ContextGraphChange

from .schemas import ContextEvidenceRef, ContextInference, SelfSignal, SelfSignalType


class SelfSignalCandidate(BaseModel):
    signal_type: SelfSignalType
    statement: str
    supporting_change_ids: list[int] = Field(min_length=1)
    contradicting_change_ids: list[int] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class SelfSynthesisPayload(BaseModel):
    signals: list[SelfSignalCandidate] = Field(default_factory=list)


class SelfIntelligenceResult(BaseModel):
    signals: list[SelfSignal] = Field(default_factory=list)
    rejected_candidates: list[str] = Field(default_factory=list)


SYSTEM_PROMPT = """You synthesize evidence-gated self intelligence from validated Personal Context Graph changes.
Return JSON only.

Allowed signal types: attention, preference, behavior_pattern, goal, concern, transition, decision_style, interest_shift.
Every signal MUST cite exact change IDs from the input. Never invent events, identities, motivations or sources.
Write time-bounded statements about what appears to be happening during this window. Do not write permanent identity claims such as 'you are X'.
Do not infer clinical or psychiatric diagnoses, protected/sensitive traits, religion, politics, sexuality, ethnicity, or other sensitive identity attributes.
Do not turn one isolated event into a behavior pattern, preference, decision style or interest shift.
Prefer useful observations such as attention concentration, repeated unfinished loops, recurring goals/concerns, changes in focus, and evidence-backed decision patterns.
A model-generated signal is never user-confirmed knowledge.
"""

_PATTERN_TYPES = {"preference", "behavior_pattern", "decision_style", "interest_shift"}
_PROHIBITED_FRAGMENTS = {
    "depression",
    "depressed",
    "bipolar",
    "adhd",
    "autism",
    "autistic",
    "personality disorder",
    "political ideology",
    "sexual orientation",
    "抑郁症",
    "抑郁",
    "双相",
    "自闭症",
    "人格障碍",
    "政治倾向",
    "性取向",
}


def _change_title(change: ContextGraphChange) -> str:
    payload = change.after_payload or {}
    for key in ("title", "summary", "display_name", "statement"):
        value = payload.get(key)
        if value:
            return str(value)
    return change.object_id


def _source_contexts(change: ContextGraphChange) -> set[tuple[str, str, str, str]]:
    contexts: set[tuple[str, str, str, str]] = set()
    for ref in (change.after_payload or {}).get("evidence_refs", []):
        if not isinstance(ref, dict):
            continue
        contexts.add(
            (
                str(ref.get("source_type") or "unknown"),
                str(ref.get("platform") or ""),
                str(ref.get("account_id") or ""),
                str(ref.get("conversation_id") or ""),
            )
        )
    return contexts


def _evidence_refs(changes: list[ContextGraphChange]) -> list[ContextEvidenceRef]:
    refs: dict[str, ContextEvidenceRef] = {}
    for change in changes:
        for raw in (change.after_payload or {}).get("evidence_refs", []):
            if not isinstance(raw, dict) or not raw.get("source_id"):
                continue
            try:
                ref = ContextEvidenceRef.model_validate(raw)
            except Exception:
                continue
            refs[ref.source_id] = ref
    return list(refs.values())


def _unsafe_statement(statement: str) -> bool:
    lowered = statement.casefold()
    return any(fragment.casefold() in lowered for fragment in _PROHIBITED_FRAGMENTS)


def _stable_signal_id(
    signal_type: str,
    statement: str,
    window_start: datetime,
    window_end: datetime,
) -> str:
    raw = "|".join(
        [
            signal_type,
            statement.casefold().strip(),
            window_start.isoformat(),
            window_end.isoformat(),
        ]
    )
    return "self_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _build_prompt(
    changes: list[ContextGraphChange],
    *,
    window_start: datetime,
    window_end: datetime,
) -> str:
    rows = []
    for change in changes:
        rows.append(
            {
                "change_id": change.change_id,
                "object_type": change.object_type,
                "title": _change_title(change),
                "change_kind": change.change_kind,
                "semantic_changes": list(change.semantic_changes or []),
                "changed_fields": list(change.changed_fields or []),
                "effective_at": change.effective_at.isoformat(),
                "evidence_ids": list(change.evidence_ids or []),
                "source_contexts": [list(item) for item in sorted(_source_contexts(change))],
            }
        )
    shape = {
        "signals": [
            {
                "signal_type": "attention|preference|behavior_pattern|goal|concern|transition|decision_style|interest_shift",
                "statement": "time-bounded evidence-backed statement",
                "supporting_change_ids": [1, 2],
                "contradicting_change_ids": [],
                "confidence": 0.0,
            }
        ]
    }
    return (
        f"Window: {window_start.isoformat()} -> {window_end.isoformat()}\n\n"
        "Required output shape:\n"
        + json.dumps(shape, ensure_ascii=False, indent=2)
        + "\n\nValidated graph changes:\n"
        + json.dumps(rows, ensure_ascii=False, indent=2)
    )


class SelfIntelligenceSynthesizer:
    """Create bounded SelfSignal hypotheses from validated graph-change history.

    The model proposes patterns, but application code owns evidence validation,
    source-diversity calculation, evidence level and confidence caps.
    """

    def __init__(self, llm: StructuredLLM):
        self.llm = llm

    def synthesize(
        self,
        *,
        changes: list[ContextGraphChange],
        window_start: datetime,
        window_end: datetime,
    ) -> SelfIntelligenceResult:
        if not changes:
            return SelfIntelligenceResult()

        by_id = {change.change_id: change for change in changes}
        raw = self.llm.generate_json(
            system=SYSTEM_PROMPT,
            prompt=_build_prompt(
                changes,
                window_start=window_start,
                window_end=window_end,
            ),
        )
        payload = SelfSynthesisPayload.model_validate(raw)
        now = datetime.now(timezone.utc)
        result = SelfIntelligenceResult()

        for candidate in payload.signals:
            support_ids = list(dict.fromkeys(candidate.supporting_change_ids))
            contradict_ids = list(dict.fromkeys(candidate.contradicting_change_ids))
            if any(change_id not in by_id for change_id in [*support_ids, *contradict_ids]):
                result.rejected_candidates.append(
                    f"{candidate.signal_type}:{candidate.statement}:unknown_change_id"
                )
                continue
            if candidate.signal_type in _PATTERN_TYPES and len(support_ids) < 2:
                result.rejected_candidates.append(
                    f"{candidate.signal_type}:{candidate.statement}:insufficient_pattern_evidence"
                )
                continue
            if _unsafe_statement(candidate.statement):
                result.rejected_candidates.append(
                    f"{candidate.signal_type}:{candidate.statement}:sensitive_or_clinical_inference"
                )
                continue

            supporting_changes = [by_id[change_id] for change_id in support_ids]
            contradicting_changes = [by_id[change_id] for change_id in contradict_ids]
            source_contexts: set[tuple[str, str, str, str]] = set()
            for change in supporting_changes:
                source_contexts.update(_source_contexts(change))
            source_diversity = max(1, len(source_contexts))

            evidence_level: Literal[2, 3]
            if len(support_ids) >= 3 and source_diversity >= 2:
                evidence_level = 3
                status = "supported"
                confidence_cap = 0.90
            else:
                evidence_level = 2
                status = "hypothesis"
                confidence_cap = 0.55 if len(support_ids) == 1 else 0.75

            evidence_refs = _evidence_refs([*supporting_changes, *contradicting_changes])
            supporting_evidence_ids = [ref.source_id for ref in _evidence_refs(supporting_changes)]
            contradicting_evidence_ids = [ref.source_id for ref in _evidence_refs(contradicting_changes)]
            confidence = min(candidate.confidence, confidence_cap)

            signal = SelfSignal(
                id=_stable_signal_id(
                    candidate.signal_type,
                    candidate.statement,
                    window_start,
                    window_end,
                ),
                created_at=now,
                updated_at=now,
                evidence_refs=evidence_refs,
                observations=[],
                inferences=[
                    ContextInference(
                        statement=candidate.statement,
                        confidence=confidence,
                        status=status,
                        supporting_evidence_ids=supporting_evidence_ids,
                        contradicting_evidence_ids=contradicting_evidence_ids,
                    )
                ],
                signal_type=candidate.signal_type,
                statement=candidate.statement,
                window_start=window_start,
                window_end=window_end,
                supporting_event_ids=[],
                contradicting_event_ids=[],
                supporting_change_ids=support_ids,
                contradicting_change_ids=contradict_ids,
                confidence=confidence,
                status=status,
                evidence_level=evidence_level,
                source_diversity=source_diversity,
                user_confirmation_ref=None,
            )
            result.signals.append(signal)

        return result
