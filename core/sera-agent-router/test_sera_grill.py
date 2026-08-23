#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression tests for the sera-grill preflight routing contract."""

import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import router  # noqa: E402


class SeraGrillRoutingTests(unittest.TestCase):
    def test_explicit_grill_request_routes_to_sera_grill(self):
        result = router.route("grill me，先帮我把需求想清楚", routes=router._builtin_routes())
        self.assertEqual(result["route"]["id"], "grill-clarify")
        self.assertEqual(result["pipeline"], ["sera-grill"])

    def test_product_init_starts_with_grill_preflight(self):
        result = router.route("启动项目，做一个新的内部工具", routes=router._builtin_routes())
        self.assertEqual(result["route"]["id"], "product-init")
        self.assertGreaterEqual(len(result["pipeline"]), 2)
        self.assertEqual(result["pipeline"][0], "sera-grill")

    def test_skill_and_product_phase_zero_are_registered(self):
        grill_skill = REPO_ROOT / "core" / "sera-grill" / "SKILL.md"
        product_skill = REPO_ROOT / "skills" / "developing-products" / "SKILL.md"
        routes_yaml = HERE / "routes.yaml"

        self.assertTrue(grill_skill.exists())
        self.assertIn("sera-grill", product_skill.read_text(encoding="utf-8"))
        route_text = routes_yaml.read_text(encoding="utf-8")
        self.assertIn("id: grill-clarify", route_text)
        self.assertIn("- sera-grill", route_text)


if __name__ == "__main__":
    unittest.main()
