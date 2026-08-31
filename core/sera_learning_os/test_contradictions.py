import sqlite3
import unittest

from core.sera_learning_os.contradictions import (
    init_contradiction_schema,
    list_contradictions,
    record_pattern_contradiction,
)
from core.sera_learning_os.learning import get_pattern, init_learning_schema
from core.sera_learning_os.skill_proposer import propose_ready_skills
from core.sera_learning_os.wiki_maintainer import compile_signal_to_wiki


class PatternContradictionTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        init_learning_schema(self.conn)
        init_contradiction_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def _signal(self, idx):
        return {
            "trace_id": f"TR.contradiction.support.{idx}",
            "project": "SeraOS",
            "task": f"support-task-{idx}",
            "source_agent": "codex",
            "source_model": "test-model",
            "outcome": "failure",
            "signal_types": ["repeat_failure"],
            "root_cause": "Post-action verification was missing",
            "failure_mode": "Task was marked complete before the artifact existed",
            "recommended_action": "Verify the artifact after every external write.",
            "affected_skills": [
                {
                    "path": "core/example/SKILL.md",
                    "baseline_version": "1.0.0",
                    "portability": "universal",
                }
            ],
        }

    def _verified_pattern_id(self):
        result = None
        for idx in (1, 2, 3):
            result = compile_signal_to_wiki(self.conn, self._signal(idx))
        self.assertEqual(result["status"], "verified")
        return result["pattern_id"]

    def test_one_ordinary_contradiction_does_not_immediately_contest(self):
        pattern_id = self._verified_pattern_id()
        result = record_pattern_contradiction(
            self.conn,
            pattern_id=pattern_id,
            evidence_ref="TR.contradiction.001",
            reason="A verified external transaction already guaranteed persistence in this environment.",
            source_agent="kimi",
            source_model="test-model-b",
            task_context="SeraOS::contradiction-task-1",
            strength=0.75,
        )
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["trigger"], "insufficient_contradictory_evidence")
        self.assertFalse(result["production_skill_modified"])

    def test_two_independent_strong_contradictions_move_pattern_to_contested(self):
        pattern_id = self._verified_pattern_id()
        first = record_pattern_contradiction(
            self.conn,
            pattern_id=pattern_id,
            evidence_ref="TR.contradiction.101",
            reason="The environment returned a durable write receipt; a second artifact check added no value.",
            source_agent="kimi",
            source_model="model-b",
            task_context="SeraOS::contradiction-task-101",
            strength=0.75,
        )
        self.assertEqual(first["status"], "verified")

        second = record_pattern_contradiction(
            self.conn,
            pattern_id=pattern_id,
            evidence_ref="TR.contradiction.102",
            reason="Another independent task showed the transactional tool guarantee was sufficient.",
            source_agent="deepseek",
            source_model="model-c",
            task_context="SeraOS::contradiction-task-102",
            strength=0.80,
        )
        self.assertEqual(second["status"], "contested")
        self.assertEqual(second["trigger"], "repeated_independent_contradictions")
        self.assertLess(second["confidence"], 0.9)

        pattern = get_pattern(self.conn, pattern_id)
        self.assertEqual(pattern["status"], "contested")
        self.assertEqual(len(list_contradictions(self.conn, pattern_id)), 2)

        # Contested Patterns are not eligible for new automatic Skill proposals.
        proposals = propose_ready_skills(self.conn)
        self.assertFalse(any(item.get("proposal_id") for item in proposals))

    def test_explicit_high_confidence_contradiction_can_contest_immediately(self):
        pattern_id = self._verified_pattern_id()
        result = record_pattern_contradiction(
            self.conn,
            pattern_id=pattern_id,
            evidence_ref="EVAL.contradiction.explicit.001",
            reason="Regression evaluator falsified the claimed mechanism across the representative suite.",
            source_agent="evaluator",
            source_model="evaluation-suite",
            task_context="evaluation::suite-1",
            strength=0.90,
            explicit=True,
        )
        self.assertEqual(result["status"], "contested")
        self.assertEqual(result["trigger"], "explicit_high_confidence_contradiction")

    def test_contradiction_history_is_append_only(self):
        pattern_id = self._verified_pattern_id()
        record_pattern_contradiction(
            self.conn,
            pattern_id=pattern_id,
            evidence_ref="TR.contradiction.append.001",
            reason="Counterexample",
            source_agent="codex",
            source_model="model-x",
            task_context="SeraOS::append-test",
            strength=0.5,
        )
        with self.assertRaises(sqlite3.DatabaseError):
            self.conn.execute(
                "UPDATE wiki_pattern_contradictions SET reason='rewritten' WHERE evidence_ref='TR.contradiction.append.001'"
            )


if __name__ == "__main__":
    unittest.main()
