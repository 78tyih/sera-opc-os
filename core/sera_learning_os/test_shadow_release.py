import sqlite3
import unittest

from core.sera_learning_os.learning import init_learning_schema, propose_skill_change
from core.sera_learning_os.portability import record_portability_probe
from core.sera_learning_os.regression import (
    assess_release_readiness,
    record_regression_check,
    record_release_readiness,
)
from core.sera_learning_os.shadow_patch import generate_shadow_patch, get_shadow_patch, validate_shadow_baseline


BASELINE = """---
name: demo-skill
version: 1.0.0
status: active
---

# demo-skill

## Purpose
Do a thing.

## Workflow
1. Execute the action.
"""


class ShadowPatchReleaseTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_learning_schema(self.conn)
        result = propose_skill_change(
            self.conn,
            {
                "proposal_id": "SEP.shadow.001",
                "skill_path": "core/demo-skill/SKILL.md",
                "baseline_version": "1.0.0",
                "candidate_version": "1.0.1",
                "portability": "universal",
                "source_patterns": ["PAT.test.verify"],
                "recommended_changes": "Require post-action verification before marking success.",
            },
        )
        self.assertEqual(result["status"], "proposed")

    def tearDown(self):
        self.conn.close()

    def _patch(self):
        result = generate_shadow_patch(
            self.conn,
            proposal_id="SEP.shadow.001",
            baseline_content=BASELINE,
        )
        self.assertNotIn("error", result)
        return result

    def _record_static_passes(self, patch_id):
        for idx, name in enumerate((
            "frontmatter_valid",
            "required_sections_present",
            "no_secret_material",
            "no_private_cot",
        ), 1):
            record_regression_check(
                self.conn,
                check_id=f"CHECK.static.{idx}",
                proposal_id="SEP.shadow.001",
                patch_id=patch_id,
                check_type="static",
                check_name=name,
                passed=True,
            )

    def _record_task_passes(self, patch_id):
        for idx, model in enumerate(("codex-model", "kimi-model", "deepseek-model"), 1):
            record_regression_check(
                self.conn,
                check_id=f"CHECK.task.{idx}",
                proposal_id="SEP.shadow.001",
                patch_id=patch_id,
                check_type="task_probe",
                check_name=f"representative-task-{idx}",
                model=model,
                passed=True,
                score=1.0,
            )

    def _record_portability_passes(self):
        record_portability_probe(
            self.conn,
            probe_id="PROBE.shadow.codex",
            proposal_id="SEP.shadow.001",
            model="codex-model",
            model_family="openai",
            metric_name="success_rate",
            baseline_score=0.70,
            candidate_score=0.80,
        )
        record_portability_probe(
            self.conn,
            probe_id="PROBE.shadow.kimi",
            proposal_id="SEP.shadow.001",
            model="kimi-model",
            model_family="moonshot",
            metric_name="success_rate",
            baseline_score=0.72,
            candidate_score=0.79,
        )

    def test_shadow_patch_never_modifies_production_and_tracks_diff(self):
        result = self._patch()
        self.assertFalse(result["production_skill_modified"])
        patch = get_shadow_patch(self.conn, result["patch_id"])
        self.assertIn("version: 1.0.1", patch["candidate_content"])
        self.assertIn("Learned Guardrails", patch["candidate_content"])
        self.assertIn("--- a/core/demo-skill/SKILL.md", patch["unified_diff"])
        self.assertIn("+++ b/core/demo-skill/SKILL.md", patch["unified_diff"])

    def test_changed_production_baseline_blocks_release(self):
        result = self._patch()
        validation = validate_shadow_baseline(
            self.conn,
            result["patch_id"],
            BASELINE + "\nProduction changed independently.\n",
        )
        self.assertFalse(validation["baseline_matches_current_production"])
        self.assertTrue(validation["release_blocked"])

    def test_regression_failure_blocks_release_ready(self):
        result = self._patch()
        patch_id = result["patch_id"]
        self._record_static_passes(patch_id)
        self._record_task_passes(patch_id)
        record_regression_check(
            self.conn,
            check_id="CHECK.task.failure",
            proposal_id="SEP.shadow.001",
            patch_id=patch_id,
            check_type="task_probe",
            check_name="known-regression-case",
            model="codex-model",
            passed=False,
            score=0.0,
        )
        self._record_portability_passes()
        assessment = assess_release_readiness(self.conn, "SEP.shadow.001", patch_id)
        self.assertEqual(assessment["status"], "blocked")
        self.assertEqual(assessment["reason"], "regression_failure")
        self.assertFalse(assessment["production_skill_modified"])

    def test_all_gates_pass_only_to_release_ready_not_release(self):
        result = self._patch()
        patch_id = result["patch_id"]
        self._record_static_passes(patch_id)
        self._record_task_passes(patch_id)
        self._record_portability_passes()
        assessment = record_release_readiness(self.conn, "SEP.shadow.001", patch_id)
        self.assertEqual(assessment["status"], "release_ready")
        self.assertEqual(assessment["recommended_portability"], "universal")
        self.assertFalse(assessment["production_skill_modified"])

        row = self.conn.execute(
            "SELECT status FROM skill_evolution_proposals WHERE proposal_id='SEP.shadow.001'"
        ).fetchone()
        # Readiness does not mutate the proposal into a released state.
        self.assertEqual(row["status"], "proposed")


if __name__ == "__main__":
    unittest.main()
