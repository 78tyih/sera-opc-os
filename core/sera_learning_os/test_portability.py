import sqlite3
import unittest

from core.sera_learning_os.learning import init_learning_schema, propose_skill_change
from core.sera_learning_os.portability import (
    assess_and_record_portability,
    assess_portability,
    init_portability_schema,
    record_portability_probe,
)


class PortabilityGateTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_learning_schema(self.conn)
        init_portability_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def _proposal(self, suffix="001"):
        proposal_id = f"SEP.portability.{suffix}"
        result = propose_skill_change(
            self.conn,
            {
                "proposal_id": proposal_id,
                "skill_path": "core/example/SKILL.md",
                "baseline_version": "1.0.0",
                "candidate_version": "1.0.1",
                "portability": "universal",
                "source_patterns": ["PAT.example.001"],
            },
        )
        self.assertEqual(result["status"], "proposed")
        return proposal_id

    def _probe(self, proposal_id, probe_id, model, baseline, candidate, family=None):
        result = record_portability_probe(
            self.conn,
            probe_id=probe_id,
            proposal_id=proposal_id,
            model=model,
            model_family=family,
            metric_name="task_success_rate",
            baseline_score=baseline,
            candidate_score=candidate,
        )
        self.assertEqual(result["status"], "recorded")

    def test_multi_model_improvement_can_pass_evaluation_as_universal(self):
        proposal_id = self._proposal("universal")
        self._probe(proposal_id, "PROBE.codex.001", "codex", 0.70, 0.82, "openai")
        self._probe(proposal_id, "PROBE.deepseek.001", "deepseek", 0.68, 0.75, "deepseek")

        assessment = assess_portability(self.conn, proposal_id)
        self.assertEqual(assessment["decision"], "accepted")
        self.assertEqual(assessment["recommended_portability"], "universal")

        recorded = assess_and_record_portability(self.conn, proposal_id)
        self.assertEqual(recorded["decision"], "accepted")
        self.assertTrue(recorded["evaluation_recorded"])
        self.assertFalse(recorded["production_skill_modified"])

        row = self.conn.execute(
            "SELECT status FROM skill_evolution_proposals WHERE proposal_id=?", (proposal_id,)
        ).fetchone()
        self.assertEqual(row["status"], "accepted")

    def test_negative_transfer_blocks_universal_and_marks_model_specific(self):
        proposal_id = self._proposal("negative-transfer")
        self._probe(proposal_id, "PROBE.codex.002", "codex", 0.60, 0.80, "openai")
        self._probe(proposal_id, "PROBE.qwen.002", "qwen", 0.70, 0.55, "qwen")

        assessment = assess_portability(self.conn, proposal_id)
        self.assertEqual(assessment["decision"], "model_specific")
        self.assertIn(assessment["recommended_portability"], {"model_specific", "model_family"})
        self.assertIn("qwen", assessment["regressed_models"])
        self.assertIn("codex", assessment["improved_models"])

        recorded = assess_and_record_portability(self.conn, proposal_id)
        self.assertEqual(recorded["decision"], "model_specific")
        self.assertFalse(recorded["production_skill_modified"])
        row = self.conn.execute(
            "SELECT status,portability FROM skill_evolution_proposals WHERE proposal_id=?", (proposal_id,)
        ).fetchone()
        self.assertEqual(row["status"], "model_specific")
        self.assertNotEqual(row["portability"], "universal")

    def test_single_model_cannot_claim_universal_portability(self):
        proposal_id = self._proposal("one-model")
        self._probe(proposal_id, "PROBE.codex.003", "codex", 0.50, 0.80, "openai")
        assessment = assess_portability(self.conn, proposal_id)
        self.assertEqual(assessment["decision"], "insufficient_evidence")
        self.assertEqual(assessment["reason"], "need_multiple_models_for_universal_claim")

    def test_cross_model_regression_rejects_candidate(self):
        proposal_id = self._proposal("reject")
        self._probe(proposal_id, "PROBE.codex.004", "codex", 0.80, 0.70, "openai")
        self._probe(proposal_id, "PROBE.deepseek.004", "deepseek", 0.75, 0.65, "deepseek")
        result = assess_and_record_portability(self.conn, proposal_id)
        self.assertEqual(result["decision"], "rejected")
        self.assertFalse(result["production_skill_modified"])

    def test_probe_history_is_append_only(self):
        proposal_id = self._proposal("append")
        self._probe(proposal_id, "PROBE.append.001", "codex", 0.50, 0.60)
        with self.assertRaises(sqlite3.DatabaseError):
            self.conn.execute(
                "UPDATE skill_portability_probes SET candidate_score=1.0 WHERE probe_id='PROBE.append.001'"
            )


if __name__ == "__main__":
    unittest.main()
