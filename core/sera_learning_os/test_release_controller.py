import sqlite3
import unittest

from core.sera_learning_os.learning import propose_skill_change
from core.sera_learning_os.portability import record_portability_probe
from core.sera_learning_os.regression import record_regression_check, record_release_readiness
from core.sera_learning_os.release_controller import (
    current_release_state,
    prepare_release_request,
    record_release_event,
)
from core.sera_learning_os.shadow_patch import generate_shadow_patch


BASELINE = """---
name: demo-skill
version: 1.0.0
status: active
---

# demo-skill

## Purpose
Do one thing safely.

## Workflow
1. Execute.

## Inputs
- task

## Outputs
- result
"""


class ReleaseControllerTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        proposal = propose_skill_change(
            self.conn,
            {
                "proposal_id": "SEP.release.001",
                "skill_path": "core/demo-skill/SKILL.md",
                "baseline_version": "1.0.0",
                "candidate_version": "1.0.1",
                "portability": "universal",
                "status": "proposed",
                "source_patterns": ["PAT.release.001"],
                "recommended_changes": "Require post-action verification before success.",
            },
        )
        self.assertNotIn("error", proposal)
        patch = generate_shadow_patch(
            self.conn,
            proposal_id="SEP.release.001",
            baseline_content=BASELINE,
        )
        self.patch_id = patch["patch_id"]

        for name in (
            "frontmatter_valid",
            "required_sections_present",
            "no_secret_material",
            "no_private_cot",
        ):
            result = record_regression_check(
                self.conn,
                check_id=f"CHK.static.{name}",
                proposal_id="SEP.release.001",
                patch_id=self.patch_id,
                check_type="static",
                check_name=name,
                passed=True,
            )
            self.assertNotIn("error", result)

        for idx in range(3):
            result = record_regression_check(
                self.conn,
                check_id=f"CHK.task.{idx}",
                proposal_id="SEP.release.001",
                patch_id=self.patch_id,
                check_type="task_probe",
                check_name=f"representative-task-{idx}",
                passed=True,
                score=1.0,
            )
            self.assertNotIn("error", result)

        for idx, model in enumerate(("codex-test", "kimi-test")):
            result = record_portability_probe(
                self.conn,
                probe_id=f"PROBE.release.{idx}",
                proposal_id="SEP.release.001",
                model=model,
                model_family="family-a" if idx == 0 else "family-b",
                metric_name="task_success_rate",
                baseline_score=0.70,
                candidate_score=0.80,
            )
            self.assertNotIn("error", result)

        ready = record_release_readiness(
            self.conn,
            proposal_id="SEP.release.001",
            patch_id=self.patch_id,
        )
        self.assertEqual(ready["status"], "release_ready")
        self.readiness_id = ready["readiness_id"]

    def tearDown(self):
        self.conn.close()

    def _prepare(self):
        result = prepare_release_request(
            self.conn,
            proposal_id="SEP.release.001",
            patch_id=self.patch_id,
            readiness_id=self.readiness_id,
            target_repo="78tyih/sera-opc-os",
            current_production_content=BASELINE,
            risk_class="medium",
        )
        self.assertNotIn("error", result)
        self.assertEqual(result["state"], "prepared")
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["production_skill_modified"])
        self.assertTrue(result["pr"]["draft"])
        return result

    def test_stale_baseline_blocks_release_request(self):
        result = prepare_release_request(
            self.conn,
            proposal_id="SEP.release.001",
            patch_id=self.patch_id,
            readiness_id=self.readiness_id,
            target_repo="78tyih/sera-opc-os",
            current_production_content=BASELINE + "\nchanged after shadow patch\n",
        )
        self.assertEqual(result["stage"], "baseline_guard")
        self.assertTrue(result["release_blocked"])

    def test_release_must_follow_pr_ci_authority_sequence(self):
        release = self._prepare()
        request_id = release["request_id"]

        invalid_merge = record_release_event(
            self.conn,
            request_id=request_id,
            event_type="merged",
            actor="human:sera",
        )
        self.assertIn("error", invalid_merge)
        self.assertEqual(current_release_state(self.conn, request_id), "prepared")

        opened = record_release_event(
            self.conn,
            request_id=request_id,
            event_type="draft_pr_opened",
            actor="github-adapter",
            payload={"pr_number": 123},
        )
        self.assertEqual(opened["state"], "draft_pr_open")

        ci = record_release_event(
            self.conn,
            request_id=request_id,
            event_type="branch_ci_passed",
            actor="github-actions",
            payload={"run_id": 456},
        )
        self.assertEqual(ci["state"], "ci_passed")

        self_approval = record_release_event(
            self.conn,
            request_id=request_id,
            event_type="approval_granted",
            actor="skill-proposer",
        )
        self.assertIn("error", self_approval)
        self.assertEqual(current_release_state(self.conn, request_id), "ci_passed")

        approval = record_release_event(
            self.conn,
            request_id=request_id,
            event_type="approval_granted",
            actor="human:sera",
            payload={"reason": "reviewed evidence and diff"},
        )
        self.assertEqual(approval["state"], "approved")
        self.assertTrue(approval["authority_recorded"])

        autonomous_merge = record_release_event(
            self.conn,
            request_id=request_id,
            event_type="merged",
            actor="release-controller",
        )
        self.assertIn("error", autonomous_merge)
        self.assertEqual(current_release_state(self.conn, request_id), "approved")

        merged = record_release_event(
            self.conn,
            request_id=request_id,
            event_type="merged",
            actor="human:sera",
            payload={"merge_sha": "abc123"},
        )
        self.assertEqual(merged["state"], "merged")
        self.assertTrue(merged["production_skill_modified"])

        verified = record_release_event(
            self.conn,
            request_id=request_id,
            event_type="post_release_verified",
            actor="post-release-monitor",
            payload={"smoke_tests": "passed"},
        )
        self.assertEqual(verified["state"], "verified")

    def test_release_request_is_deterministic_and_draft_only(self):
        first = self._prepare()
        second = prepare_release_request(
            self.conn,
            proposal_id="SEP.release.001",
            patch_id=self.patch_id,
            readiness_id=self.readiness_id,
            target_repo="78tyih/sera-opc-os",
            current_production_content=BASELINE,
            risk_class="medium",
        )
        self.assertEqual(second["request_id"], first["request_id"])
        self.assertFalse(second["recorded"])
        self.assertEqual(second["state"], "prepared")


if __name__ == "__main__":
    unittest.main()
