#!/usr/bin/env python3
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from drift import build_report

BASE = {
    "target_id": "linear",
    "source_url": "https://linear.app",
    "captured_at": "2026-05-21T00:00:00Z",
    "freshness": "historical",
    "fingerprint": "old",
    "state": {
        "brand_personality": ["neutral voice", "you-only pronoun posture"],
        "color_system": {"primary": "#111111", "accent": "#aaaaaa"},
        "typography": {"primary_font": "Inter", "heading_style": {"h1": "64px"}, "body_style": {"size": "14px"}},
        "layout_language": {"grid": "98 grid / 495 flex", "section_style": "landing"},
        "component_patterns": ["buttons", "cards"],
        "design_patterns": [{"name": "flex-dominant layout with grid support"}],
    },
}

class DriftTests(unittest.TestCase):
    def test_identical_snapshot_has_no_drift(self):
        after = copy.deepcopy(BASE)
        after["fingerprint"] = "same"
        result = build_report(BASE, after)
        self.assertEqual(result["summary"]["severity"], "none")
        self.assertFalse(result["summary"]["meaningful_change"])

    def test_accent_only_is_minor_and_not_memory_worthy(self):
        after = copy.deepcopy(BASE)
        after["state"]["color_system"]["accent"] = "#bbbbbb"
        result = build_report(BASE, after)
        self.assertEqual(result["summary"]["severity"], "minor")
        self.assertEqual(result["summary"]["memory_action"], "archive_snapshot_only")

    def test_typography_plus_primary_color_requires_review(self):
        after = copy.deepcopy(BASE)
        after["state"]["typography"]["primary_font"] = "Geist"
        after["state"]["color_system"]["primary"] = "#222222"
        result = build_report(BASE, after)
        self.assertEqual(result["summary"]["severity"], "moderate")
        self.assertTrue(result["summary"]["meaningful_change"])

    def test_design_pattern_change_forces_major(self):
        after = copy.deepcopy(BASE)
        after["state"]["design_patterns"] = [{"name": "editorial asymmetric section rhythm"}]
        result = build_report(BASE, after)
        self.assertEqual(result["summary"]["severity"], "major")
        self.assertEqual(result["summary"]["memory_action"], "semantic_review_and_cross_site_recompute")

    def test_new_measurement_coverage_is_not_drift(self):
        after = copy.deepcopy(BASE)
        after["state"]["motion_language"] = {"feel": "snappy"}
        result = build_report(BASE, after)
        self.assertEqual(result["summary"]["severity"], "none")

    def test_cross_target_compare_is_rejected(self):
        after = copy.deepcopy(BASE)
        after["target_id"] = "stripe"
        with self.assertRaises(ValueError):
            build_report(BASE, after)

if __name__ == "__main__":
    unittest.main()
