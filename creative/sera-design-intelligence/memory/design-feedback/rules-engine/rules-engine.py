#!/usr/bin/env python3
"""
Sera Design Rules Engine
从实验和反馈中自动生成设计规则
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class DesignRulesEngine:
    def __init__(self):
        self.rules_file = BASE_DIR / "memory/design-feedback/rules-engine/design-rules.json"
        self.rules = self._load()
    
    def _load(self):
        if self.rules_file.exists():
            with open(self.rules_file) as f:
                return json.load(f)
        return {"version": "1.0.0", "rules": []}
    
    def _save(self):
        self.rules_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.rules_file, "w") as f:
            json.dump(self.rules, f, indent=2, ensure_ascii=False)
    
    def add_rule(self, rule: str, source: str, product: str, confidence: str):
        new_rule = {
            "id": f"rule-{len(self.rules['rules']) + 1:03d}",
            "rule": rule,
            "source": source,
            "product": product,
            "confidence": confidence,
            "created": "2026-08-21",
            "applied_to": []
        }
        self.rules["rules"].append(new_rule)
        self._save()
        return new_rule
    
    def get_rules_by_product(self, product: str) -> list:
        return [r for r in self.rules["rules"] if r["product"] == product]
    
    def get_all_rules(self) -> list:
        return self.rules["rules"]


if __name__ == "__main__":
    engine = DesignRulesEngine()
    rules = engine.get_all_rules()
    if rules:
        print(f"Generated Design Rules: {len(rules)}")
        for r in rules:
            print(f"  [{r['id']}] {r['rule'][:60]}...")
    else:
        print("No design rules generated yet. Run experiments to generate rules.")