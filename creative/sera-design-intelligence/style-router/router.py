#!/usr/bin/env python3
"""
Sera Style Router — 根据产品属性自动选择设计语言
Usage: python router.py --industry finance --audience trader --goal sales
"""

import json
import yaml
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent


def load_rules():
    with open(BASE_DIR / "rules.yaml") as f:
        return yaml.safe_load(f)


def load_registry():
    registry_path = BASE_DIR.parent / "styles" / "registry.json"
    with open(registry_path) as f:
        return json.load(f)


def match_style(profile: dict) -> dict:
    rules = load_rules()["rules"]
    registry = load_registry()
    styles = {s["id"]: s for s in registry["styles"]}

    best_match = None
    best_score = 0

    for rule in rules:
        match = rule["match"]
        score = 0
        if match.get("industry") == profile.get("industry"):
            score += 50
        if match.get("audience") == profile.get("audience"):
            score += 30
        if score > best_score:
            best_score = score
            best_match = rule

    if not best_match:
        return {"error": "no matching style found"}

    weights = best_match["weights"]
    total = sum(weights.values())
    recommendations = []

    for style_id, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        style = styles.get(style_id)
        if style:
            recommendations.append({
                "style_id": style_id,
                "name": style.get("name", style_id),
                "weight": f"{weight}%",
                "confidence": round(weight / total, 2),
                "reason": best_match["description"]
            })

    # Get reference cases from top style
    top_style = styles.get(list(weights.keys())[0], {})
    references = top_style.get("source", [])

    return {
        "profile": profile,
        "primary_style": recommendations[0]["style_id"] if recommendations else None,
        "recommendations": recommendations,
        "references": references,
        "components": top_style.get("components", []),
        "match_rule": best_match["description"]
    }


def main():
    parser = argparse.ArgumentParser(description="Sera Style Router")
    parser.add_argument("--industry", required=True, help="Product industry")
    parser.add_argument("--audience", default="general", help="Target audience")
    parser.add_argument("--goal", default="conversion", help="Business goal")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    profile = {
        "industry": args.industry,
        "audience": args.audience,
        "goal": args.goal
    }

    result = match_style(profile)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n Product Profile: {profile}")
        print(f"\n Primary Style: {result['primary_style']}")
        print(f"\n Style Mix:")
        for rec in result["recommendations"]:
            print(f"   {rec['name']} ({rec['style_id']}): {rec['weight']}")
        print(f"\n References: {', '.join(result['references'])}")
        print(f" Core Components: {', '.join(result['components'])}")
        print(f" Match Rule: {result['match_rule']}")


if __name__ == "__main__":
    main()