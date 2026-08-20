#!/usr/bin/env python3
"""
Sera Product-to-Style Matching Engine
根据产品属性自动匹配设计风格，比 Style Router 更智能
支持多维度评分、权重调整、置信度计算

Usage:
  python matching-engine.py --name "牛牛 AI" --industry ai --audience developer --goal "free trial signup" --keywords "intelligent,minimal,innovative"
  python matching-engine.py --name "HTX OTC" --industry finance --audience institutional --goal "trust & conversion" --keywords "professional,premium,secure" --json
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class StyleMatchingEngine:
    def __init__(self, registry_path=None):
        if registry_path is None:
            registry_path = BASE_DIR / "styles" / "registry.json"
        with open(registry_path) as f:
            registry = json.load(f)
        self.styles = {s["id"]: s for s in registry["styles"]}
        self.max_possible_score = 100  # 40 + 25 + 20 + 15

    def match(self, product_profile: dict) -> dict:
        """根据产品画像匹配最佳风格组合"""
        scores = {}

        for style_id, style in self.styles.items():
            score = self._calculate_fit(style, product_profile)
            scores[style_id] = score

        # 排序（降序）
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # 归一化
        total = sum(s for _, s in ranked)
        normalized = [(sid, s / total) for sid, s in ranked if s > 0]

        # 取前 3 个（至少 1 个，最多 3 个）
        top_n = min(3, len(normalized))
        top_styles = normalized[:top_n]

        # 归一化权重（确保总和为 1）
        top_total = sum(w for _, w in top_styles)
        if top_total > 0:
            top_styles = [(sid, w / top_total) for sid, w in top_styles]

        primary_style = top_styles[0][0] if top_styles else None

        return {
            "product": product_profile.get("name", "unknown"),
            "primary_style": primary_style,
            "style_combination": [
                {
                    "style_id": sid,
                    "weight": round(w, 2),
                    "style_name": self.styles.get(sid, {}).get("name", sid),
                }
                for sid, w in top_styles
            ],
            "confidence": self._calculate_confidence(top_styles),
            "all_scores": {
                sid: round(s, 2) for sid, s in ranked
            },
            "fallback_triggered": top_styles[0][1] < 0.3 if top_styles else True,
        }

    def _calculate_fit(self, style: dict, product: dict) -> float:
        """计算风格与产品的匹配度（满分 100）"""
        score = 0.0

        # --- 行业匹配 (权重 40%) ---
        if style.get("industry") == product.get("industry"):
            score += 40
        elif product.get("industry") in style.get("recommended_for", []):
            score += 20

        # --- 受众匹配 (权重 25%) ---
        if style.get("audience") == product.get("audience"):
            score += 25
        elif product.get("audience") in str(style.get("target_user", "")):
            score += 15

        # --- 目标匹配 (权重 20%) ---
        goal = (product.get("goal") or "").lower()
        conversion_goal = (style.get("conversion_goal") or "").lower()
        if goal and conversion_goal:
            if goal in conversion_goal or conversion_goal in goal:
                score += 20
            else:
                # 部分匹配：检查是否有共同的关键词
                goal_words = set(goal.replace("&", "").split())
                conv_words = set(conversion_goal.replace("&", "").split())
                if goal_words & conv_words:
                    score += 10

        # --- 关键词匹配 (权重 15%) ---
        product_keywords = set(
            k.lower().strip() for k in product.get("brand_keywords", []) if k
        )
        style_keywords = set(
            k.lower().strip() for k in style.get("keywords", []) if k
        )
        if product_keywords and style_keywords:
            overlap = product_keywords & style_keywords
            score += min(len(overlap) * 5, 15)

        return score

    def _calculate_confidence(self, top_styles: list) -> dict:
        """计算置信度"""
        if not top_styles:
            return {"level": "low", "score": 0.0, "reason": "无匹配风格"}

        primary_weight = top_styles[0][1]

        if primary_weight > 0.5:
            level = "high"
        elif primary_weight > 0.3:
            level = "medium"
        else:
            level = "low"

        # 额外考虑 Top1 与 Top2 的差距
        gap = 0.0
        if len(top_styles) > 1:
            gap = top_styles[0][1] - top_styles[1][1]

        return {
            "level": level,
            "score": round(primary_weight, 2),
            "gap_to_second": round(gap, 2) if len(top_styles) > 1 else None,
        }

    def batch_match(self, profiles: list[dict]) -> list[dict]:
        """批量匹配多个产品画像"""
        return [self.match(p) for p in profiles]


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Sera Product-to-Style Matching Engine"
    )
    parser.add_argument("--name", required=True, help="Product name")
    parser.add_argument("--industry", required=True, help="Product industry")
    parser.add_argument("--audience", default="general", help="Target audience")
    parser.add_argument("--goal", default="conversion", help="Business goal")
    parser.add_argument(
        "--keywords", default="", help="Brand keywords (comma-separated)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    parser.add_argument("--stage", default="growth", help="Product stage: startup/growth/mature")
    args = parser.parse_args()

    profile = {
        "name": args.name,
        "industry": args.industry,
        "audience": args.audience,
        "goal": args.goal,
        "stage": args.stage,
        "brand_keywords": [
            k.strip() for k in args.keywords.split(",") if k.strip()
        ],
    }

    engine = StyleMatchingEngine()
    result = engine.match(profile)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # 人类可读输出
    print(f"\n=== Product Profile ===")
    print(f"Name:     {profile['name']}")
    print(f"Industry: {profile['industry']}")
    print(f"Audience: {profile['audience']}")
    print(f"Goal:     {profile['goal']}")
    print(f"Stage:    {profile['stage']}")
    print(f"Keywords: {', '.join(profile['brand_keywords'])}")

    print(f"\n=== Matching Result ===")
    conf = result["confidence"]
    print(f"Primary Style: {result['primary_style']}")
    print(
        f"Confidence:    {conf['level'].upper()} ({conf['score']*100:.0f}%)"
    )
    if conf.get("gap_to_second") is not None:
        print(f"Gap to 2nd:   {conf['gap_to_second']*100:.0f}%")

    print(f"\nStyle Combination:")
    for s in result["style_combination"]:
        bar = "█" * int(s["weight"] * 40)
        print(f"  {s['style_name']:30s} {s['weight']*100:5.1f}% {bar}")

    if result["fallback_triggered"]:
        print(f"\n  ⚠  Fallback triggered — low match confidence across all styles")

    print(f"\nAll Scores:")
    for sid, s in sorted(
        result["all_scores"].items(), key=lambda x: x[1], reverse=True
    ):
        bar = "█" * int(s / 2.5)
        print(f"  {sid:35s} {s:5.1f} {bar}")

    print()


if __name__ == "__main__":
    main()