import os
import sqlite3
import tempfile
import unittest

from core.sera_learning_os.contradiction_export import export_contradictions_snapshot
from core.sera_learning_os.learning import get_pattern, init_learning_schema
from core.sera_learning_os.pipeline import process_learning_signal
from core.sera_learning_os.wiki_maintainer import compile_signal_to_wiki


class LearningPipelineTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_learning_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def _support_signal(self, idx):
        return {
            "trace_id": f"TR.pipeline.support.{idx}",
            "project": "SeraOS",
            "task": f"pipeline-support-{idx}",
            "source_agent": "codex",
            "source_model": "test-model",
            "observed_at": f"2026-08-3{idx}T01:02:03+00:00" if idx <= 1 else f"2026-08-{27 + idx:02d}T01:02:03+00:00",
            "outcome": "failure",
            "signal_types": ["repeat_failure"],
            "failure_mode": "Completion status was emitted before verification",
            "root_cause": "External write was not verified",
            "recommended_action": "Verify external writes before task completion.",
            "affected_skills": [
                {
                    "path": "core/example/SKILL.md",
                    "baseline_version": "1.0.0",
                    "portability": "universal",
                }
            ],
        }

    def _verified_pattern(self):
        result = None
        for idx in (1, 2, 3):
            signal = self._support_signal(idx)
            # Make timestamps valid and distinct without coupling the test to current day.
            signal["observed_at"] = f"2026-08-{27 + idx:02d}T01:02:03+00:00"
            result = compile_signal_to_wiki(self.conn, {**signal, "at": signal["observed_at"]})
        self.assertEqual(result["status"], "verified")
        return result["pattern_id"]

    def test_pipeline_preserves_observed_at_in_raw_store(self):
        signal = self._support_signal(1)
        signal["observed_at"] = "2026-08-30T09:15:00+00:00"
        result = process_learning_signal(self.conn, signal, auto_propose=False)
        self.assertFalse(result.get("error"))
        row = self.conn.execute(
            "SELECT at FROM learning_raw_signals WHERE trace_id=?", (signal["trace_id"],)
        ).fetchone()
        self.assertEqual(row["at"], signal["observed_at"])

    def test_pipeline_can_contest_existing_pattern_without_creating_new_support_pattern(self):
        pattern_id = self._verified_pattern()
        contradiction = {
            "trace_id": "TR.pipeline.contradiction.001",
            "project": "SeraOS",
            "task": "counterexample-task",
            "source_agent": "evaluator",
            "source_model": "regression-suite",
            "observed_at": "2026-08-31T02:30:00+00:00",
            "outcome": "success",
            "signal_types": ["contradiction", "regression"],
            "contradictions": [
                {
                    "pattern_id": pattern_id,
                    "reason": "Representative regression suite showed the tool transaction receipt already guarantees the claimed postcondition.",
                    "strength": 0.92,
                    "explicit": True,
                }
            ],
        }
        result = process_learning_signal(self.conn, contradiction, auto_propose=False)
        self.assertEqual(result["wiki"]["status"], "recorded_no_pattern")
        self.assertEqual(result["contradictions"][0]["status"], "contested")
        self.assertFalse(result["production_skill_modified"])
        self.assertEqual(get_pattern(self.conn, pattern_id)["status"], "contested")

    def test_contradiction_snapshot_is_exported_for_git_audit(self):
        pattern_id = self._verified_pattern()
        contradiction = {
            "trace_id": "TR.pipeline.contradiction.export.001",
            "project": "SeraOS",
            "task": "counterexample-export",
            "source_agent": "human-review",
            "source_model": "n/a",
            "observed_at": "2026-08-31T03:00:00+00:00",
            "outcome": "success",
            "signal_types": ["contradiction", "human_feedback"],
            "contradicts_pattern_ids": [pattern_id],
            "contradiction_reason": "Human review confirmed this rule is too broad for transactional tools.",
            "contradiction_strength": 0.95,
            "contradiction_explicit": True,
        }
        process_learning_signal(self.conn, contradiction, auto_propose=False)

        with tempfile.TemporaryDirectory() as tmp:
            result = export_contradictions_snapshot(self.conn, tmp)
            self.assertEqual(result["contradiction_files_exported"], 1)
            path = result["contradiction_files"][0]
            self.assertTrue(os.path.exists(path))
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("Append-only counter-evidence", content)
            self.assertIn("Human review confirmed", content)
            self.assertIn("Production Skills are not modified", content)


if __name__ == "__main__":
    unittest.main()
