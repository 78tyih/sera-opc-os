import sqlite3
import unittest

from core.sera_learning_os.learning import (
    get_pattern,
    init_learning_schema,
    propose_skill_change,
    record_evaluation,
    record_raw_signal,
    upsert_pattern,
)


class LearningOSV0Tests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_learning_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_raw_signal_is_append_only(self):
        result = record_raw_signal(
            self.conn,
            {
                "trace_id": "TR.test.001",
                "project": "SeraOS",
                "source_agent": "codex",
                "source_model": "test-model",
                "run_id": "run-1",
                "outcome": "failure",
                "error_signatures": ["missing-verification"],
            },
        )
        self.assertEqual(result["status"], "recorded")
        with self.assertRaises(sqlite3.DatabaseError):
            self.conn.execute(
                "UPDATE learning_raw_signals SET outcome='success' WHERE trace_id='TR.test.001'"
            )

    def test_private_reasoning_fields_are_rejected(self):
        result = record_raw_signal(
            self.conn,
            {
                "trace_id": "TR.test.002",
                "project": "SeraOS",
                "source_agent": "codex",
                "source_model": "test-model",
                "outcome": "success",
                "chain_of_thought": "must not persist",
            },
        )
        self.assertIn("error", result)

    def test_pattern_accumulates_evidence(self):
        first = upsert_pattern(
            self.conn,
            {
                "pattern_id": "PAT.test.verify",
                "title": "Actions need post verification",
                "pattern_type": "failure_pattern",
                "status": "provisional",
                "scope": "organization",
                "confidence": 0.6,
                "evidence": [{"ref": "TR.test.001", "kind": "trace"}],
                "observation": "Unverified actions can look successful while failing.",
            },
        )
        self.assertEqual(first["event"], "pattern_created")

        second = upsert_pattern(
            self.conn,
            {
                "pattern_id": "PAT.test.verify",
                "title": "Actions need post verification",
                "pattern_type": "failure_pattern",
                "status": "supported",
                "scope": "organization",
                "confidence": 0.8,
                "evidence": [{"ref": "TR.test.003", "kind": "trace"}],
                "observation": "Repeated evidence supports post-action verification.",
            },
        )
        self.assertEqual(second["event"], "pattern_updated")
        pattern = get_pattern(self.conn, "PAT.test.verify")
        self.assertEqual(pattern["status"], "supported")
        self.assertEqual(len(pattern["evidence"]), 2)

    def test_skill_proposal_requires_evaluation_and_does_not_edit_skill(self):
        proposal = propose_skill_change(
            self.conn,
            {
                "proposal_id": "SEP.test.001",
                "skill_path": "core/example/SKILL.md",
                "baseline_version": "1.0.0",
                "candidate_version": "1.1.0",
                "portability": "universal",
                "source_patterns": ["PAT.test.verify"],
            },
        )
        self.assertEqual(proposal["status"], "proposed")

        result = record_evaluation(
            self.conn,
            {
                "eval_id": "EVAL.test.001",
                "proposal_id": "SEP.test.001",
                "decision": "rejected",
                "metrics": {"baseline_success": 0.8, "candidate_success": 0.6},
                "notes": "Regression detected.",
            },
        )
        self.assertEqual(result["decision"], "rejected")
        self.assertFalse(result["production_skill_modified"])

        row = self.conn.execute(
            "SELECT status FROM skill_evolution_proposals WHERE proposal_id='SEP.test.001'"
        ).fetchone()
        self.assertEqual(row["status"], "rejected")


if __name__ == "__main__":
    unittest.main()
