import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "miner.py"
spec = importlib.util.spec_from_file_location("cross_site_miner", MODULE_PATH)
assert spec and spec.loader
miner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = miner
spec.loader.exec_module(miner)


class MinerTests(unittest.TestCase):
    def _case(self, root: Path, case_id: str, url: str, component: str, semantic: str):
        case = root / case_id
        dna_dir = case / "dna"
        dna_dir.mkdir(parents=True)
        dna = {
            "name": case_id,
            "industry": "saas",
            "emotion": "calm",
            "brand_personality": ["premium", "clear"],
            "color_system": {"primary": "#000"},
            "typography": {"primary_font": "Inter"},
            "component_patterns": [component],
            "design_patterns": [{"name": semantic, "category": "layout"}],
            "provenance": {"source_url": url}
        }
        (dna_dir / "STYLE_DNA.json").write_text(json.dumps(dna), encoding="utf-8")
        return f"{case_id}={case}"

    def test_semantic_pattern_becomes_strong_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = [
                self._case(root, "linear", "https://linear.app", "buttons", "flex-dominant layout"),
                self._case(root, "stripe", "https://stripe.com", "buttons", "flex-dominant layout"),
                self._case(root, "vercel", "https://vercel.com", "buttons", "flex-dominant layout"),
            ]
            report = miner.build_report([miner.load_case(s) for s in specs], minimum_sites=2)
            semantic = next(p for p in report["patterns"] if p["pattern_type"] == "semantic")
            self.assertEqual(semantic["status"], "strong_candidate")
            self.assertTrue(semantic["eligible_for_pattern_library"])
            buttons = next(p for p in report["patterns"] if p["normalized_pattern"] == "buttons")
            self.assertEqual(buttons["status"], "strong_candidate")
            self.assertFalse(buttons["eligible_for_pattern_library"])
            self.assertEqual(buttons["promotion_lane"], "component_coverage")

    def test_same_domain_does_not_count_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = [
                self._case(root, "a", "https://example.com/a", "cards", "quiet borders"),
                self._case(root, "b", "https://example.com/b", "cards", "quiet borders"),
            ]
            report = miner.build_report([miner.load_case(s) for s in specs], minimum_sites=2)
            semantic = next(p for p in report["patterns"] if p["pattern_type"] == "semantic")
            self.assertEqual(semantic["support_count"], 1)
            self.assertEqual(semantic["status"], "case_local")


if __name__ == "__main__":
    unittest.main()
