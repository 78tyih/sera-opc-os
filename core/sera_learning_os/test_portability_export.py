import os
import sqlite3
import tempfile
import unittest

from core.sera_learning_os.learning import init_learning_schema, propose_skill_change
from core.sera_learning_os.portability import init_portability_schema, record_portability_probe
from core.sera_learning_os.portability_export import export_portability_snapshot


class PortabilityExportTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_learning_schema(self.conn)
        init_portability_schema(self.conn)
        result = propose_skill_change(
            self.conn,
            {
                "proposal_id": "SEP.export.portability",
                "skill_path": "core/example/SKILL.md",
                "baseline_version": "1.0.0",
                "candidate_version": "1.0.1",
                "portability": "universal",
                "source_patterns": ["PAT.export.portability"],
            },
        )
        self.assertEqual(result["status"], "proposed")

    def tearDown(self):
        self.conn.close()

    def test_export_contains_model_matrix_and_governance_boundary(self):
        record_portability_probe(
            self.conn,
            probe_id="PROBE.export.codex",
            proposal_id="SEP.export.portability",
            model="codex",
            model_family="openai",
            metric_name="task_success_rate",
            baseline_score=0.70,
            candidate_score=0.82,
        )
        record_portability_probe(
            self.conn,
            probe_id="PROBE.export.deepseek",
            proposal_id="SEP.export.portability",
            model="deepseek",
            model_family="deepseek",
            metric_name="task_success_rate",
            baseline_score=0.68,
            candidate_score=0.75,
        )

        with tempfile.TemporaryDirectory() as tmp:
            result = export_portability_snapshot(self.conn, tmp)
            self.assertEqual(result["portability_files_exported"], 1)
            path = result["portability_files"][0]
            self.assertTrue(os.path.exists(path))
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("Codex".lower(), content.lower())
            self.assertIn("deepseek", content.lower())
            self.assertIn("accepted", content)
            self.assertIn("does not authorize production Skill release", content)


if __name__ == "__main__":
    unittest.main()
