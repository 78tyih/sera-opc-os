#!/usr/bin/env python3
"""
Sera Design Experiment Tracker
记录和追踪设计实验（A/B 测试、设计变更效果）
"""

import json
from datetime import datetime
from pathlib import Path

EXPERIMENTS_DIR = Path(__file__).parent

class ExperimentTracker:
    def __init__(self):
        self.log_file = EXPERIMENTS_DIR / "experiments-log.json"
        self.experiments = self._load()
    
    def _load(self):
        if self.log_file.exists():
            with open(self.log_file) as f:
                return json.load(f)
        return {"version": "1.0.0", "experiments": []}
    
    def _save(self):
        with open(self.log_file, "w") as f:
            json.dump(self.experiments, f, indent=2, ensure_ascii=False)
    
    def create_experiment(self, name: str, product: str, variant_a: str, variant_b: str, 
                          hypothesis: str, metrics: list):
        """创建新实验"""
        experiment = {
            "id": f"exp-{len(self.experiments['experiments']) + 1:03d}",
            "name": name,
            "product": product,
            "created": datetime.now().isoformat(),
            "status": "running",
            "hypothesis": hypothesis,
            "variants": {
                "A": {"description": variant_a, "results": {}},
                "B": {"description": variant_b, "results": {}}
            },
            "metrics": metrics,
            "observations": []
        }
        self.experiments["experiments"].append(experiment)
        self._save()
        return experiment
    
    def record_result(self, experiment_id: str, variant: str, metric: str, value: float):
        """记录实验结果"""
        for exp in self.experiments["experiments"]:
            if exp["id"] == experiment_id:
                exp["variants"][variant]["results"][metric] = value
                self._save()
                return
    
    def conclude_experiment(self, experiment_id: str, winner: str, learnings: str):
        """结束实验并记录经验"""
        for exp in self.experiments["experiments"]:
            if exp["id"] == experiment_id:
                exp["status"] = "concluded"
                exp["winner"] = winner
                exp["concluded"] = datetime.now().isoformat()
                exp["learnings"] = learnings
                self._save()
                return
    
    def add_observation(self, experiment_id: str, observation: str):
        """添加实验观察"""
        for exp in self.experiments["experiments"]:
            if exp["id"] == experiment_id:
                exp["observations"].append({
                    "timestamp": datetime.now().isoformat(),
                    "note": observation
                })
                self._save()
                return
    
    def get_experiments_by_product(self, product: str) -> list:
        return [e for e in self.experiments["experiments"] if e["product"] == product]
    
    def get_running_experiments(self) -> list:
        return [e for e in self.experiments["experiments"] if e["status"] == "running"]


if __name__ == "__main__":
    tracker = ExperimentTracker()
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        experiments = tracker.get_running_experiments()
        print(f"Running experiments: {len(experiments)}")
        for e in experiments:
            print(f"  [{e['id']}] {e['name']} — {e['product']}")
    else:
        print(f"Total experiments: {len(tracker.experiments['experiments'])}")
        print(f"Running: {len(tracker.get_running_experiments())}")
        print(f"Use: python experiment-tracker.py list")