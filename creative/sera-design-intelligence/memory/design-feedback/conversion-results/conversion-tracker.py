#!/usr/bin/env python3
"""
Sera Conversion Feedback Tracker
追踪设计变更对转化指标的影响
"""

import json
from datetime import datetime
from pathlib import Path

RESULTS_DIR = Path(__file__).parent

class ConversionTracker:
    def __init__(self):
        self.log_file = RESULTS_DIR / "conversion-history.json"
        self.data = self._load()
    
    def _load(self):
        if self.log_file.exists():
            with open(self.log_file) as f:
                return json.load(f)
        return {"version": "1.0.0", "records": []}
    
    def _save(self):
        with open(self.log_file, "w") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def record(self, product: str, page: str, metric: str, baseline: float, current: float):
        record = {
            "id": f"rec-{len(self.data['records']) + 1:03d}",
            "product": product,
            "page": page,
            "metric": metric,
            "baseline": baseline,
            "current": current,
            "change": round((current - baseline) / baseline * 100, 1),
            "timestamp": datetime.now().isoformat()
        }
        self.data["records"].append(record)
        self._save()
        return record
    
    def get_product_performance(self, product: str) -> dict:
        records = [r for r in self.data["records"] if r["product"] == product]
        if not records:
            return {"product": product, "total_changes": 0, "average_change": 0}
        
        avg_change = sum(r["change"] for r in records) / len(records)
        return {
            "product": product,
            "total_changes": len(records),
            "average_change": round(avg_change, 1),
            "improvements": len([r for r in records if r["change"] > 0]),
            "regressions": len([r for r in records if r["change"] < 0])
        }


if __name__ == "__main__":
    tracker = ConversionTracker()
    print(f"Total conversion records: {len(tracker.data['records'])}")