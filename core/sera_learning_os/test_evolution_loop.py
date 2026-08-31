import sqlite3
import unittest

from core.sera_learning_os.daily_review import build_daily_review, render_daily_review_markdown
from core.sera_learning_os.learning import get_pattern, init_learning_schema
from core.sera_learning_os.skill_proposer import propose_ready_skills
from core.sera_learning_os.wiki_maintainer import compile_signal_to_wiki


class AutomaticEvolutionLoopTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_learning_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def _failure_signal(self, idx, root_cause="Actions were not verified after tool execution"):
        return {
            "trace_id": f"TR.auto.{idx:03d}",
            "project": "SeraOS",
            "task": f"task-{idx}",
            "source_agent": "codex" if idx != 2 else "kimi",
            "source_model": "gpt-test" if idx != 3 else "deepseek-test",
            "run_id": f"run-{idx}",
            "outcome": "failure",
            "signal_types": ["repeat_failure", "workflow_behavior"],
            "failure_mode": "Task reported success but output was not actually present",
            "root_cause": root_cause,
            "recommended_action": "Require post-action verification before marking the task complete.",
            "affected_skills": [
                {
                    "path": "core/sera-agent-orchestrator/SKILL.md",
                    "baseline_version": "1.0.0",
                    "portability": "universal",
                }
            ],
        }

    def test_three_independent_root_cause_signals_verify_pattern_and_create_proposal(self):
        ids = []
        statuses = []
        for idx in (1, 2, 3):
            result = compile_signal_to_wiki(self.conn, self._failure_signal(idx))
            ids.append(result["pattern_id"])
            statuses.append(result["status"])

        self.assertEqual(len(set(ids)), 1)
        self.assertEqual(statuses, ["provisional", "supported", "verified"])

        pattern = get_pattern(self.conn, ids[0])
        self.assertEqual(pattern["status"], "verified")
        self.assertEqual(pattern["body"]["evidence_count"], 3)
        self.assertEqual(pattern["body"]["independent_context_count"], 3)
        self.assertEqual(len(pattern["body"]["source_agents"]), 2)
        self.assertEqual(len(pattern["body"]["source_models"]), 2)

        proposals = propose_ready_skills(self.conn)
        created = [p for p in proposals if p.get("proposal_id")]
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0]["status"], "proposed")

        # Re-running the proposer must not duplicate the same proposal.
        second = propose_ready_skills(self.conn)
        self.assertTrue(any(p.get("reason") == "proposal_already_exists" for p in second))

    def test_symptom_only_failure_cannot_auto_verify(self):
        for idx in (10, 11, 12, 13):
            signal = self._failure_signal(idx, root_cause="")
            signal["failure_mode"] = "Something looked wrong"
            result = compile_signal_to_wiki(self.conn, signal)
        pattern = get_pattern(self.conn, result["pattern_id"])
        self.assertEqual(pattern["status"], "supported")
        self.assertTrue(pattern["body"]["verification_blocked"])
        proposals = propose_ready_skills(self.conn)
        self.assertFalse(any(p.get("proposal_id") for p in proposals))

    def test_daily_learning_review_is_separate_from_activity_summary(self):
        compile_signal_to_wiki(self.conn, self._failure_signal(20))
        review = build_daily_review(self.conn)
        markdown = render_daily_review_markdown(review)
        self.assertEqual(review["raw_signals"], 1)
        self.assertEqual(review["patterns_updated"], 1)
        self.assertIn("系统今天从执行中学到了什么", markdown)
        self.assertIn("Governance Reminder", markdown)


if __name__ == "__main__":
    unittest.main()
