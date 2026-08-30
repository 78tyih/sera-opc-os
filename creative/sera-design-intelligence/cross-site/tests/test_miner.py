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
    def _case(self, root: Path, case_id: str, url: str, component: str, conversion: str):
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
            "conversion_patterns": [conversion],
            "provenance": {"source_url": url}
        }
        (dna_dir / "STYLE_DNA.json").write_text(json.dumps(dna), encoding="utf-8")
        return f"{case_id}={case}"

    def test_repeated_pattern_becomes_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = [
                self._case(root, "linear", "https://linear.app", "product demo", "single primary CTA"),
                self._case(root, "stripe", "https://stripe.com", "product demo", "single primary CTA"),
                self._case(root, "vercel", "https://vercel.com", "product demo", "dual CTA"),
            ]
            cases = [miner.load_case(s) for s in specs]
            report = miner.build_report(cases, minimum_sites=2)

            product_demo = next(p for p in report["patterns"] if p["normalized_pattern"] == "product demo")
            self.assertEqual(product_demo["status"], "strong_candidate")
            self.assertEqual(product_demo["support_count"], 3)

            single_cta = next(p for p in report["patterns"] if p["normalized_pattern"] == "single primary cta")
            self.assertEqual(single_cta["status"], "candidate")
            self.assertEqual(single_cta["support_count"], 2)

    def test_same_domain_does_not_count_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            specs = [
                self._case(root, "a", "https://example.com/a", "glass card", "cta"),
                self._case(root, "b", "https://example.com/b", "glass card", "cta"),
            ]
            cases = [miner.load_case(s) for s in specs]
            report = miner.build_report(cases, minimum_sites=2)
            glass = next(p for p in report["patterns"] if p["normalized_pattern"] == "glass card")
            self.assertEqual(glass["support_count"], 1)
            self.assertEqual(glass["status"], "case_local")


if __name__ == "__main__":
    unittest.main()
