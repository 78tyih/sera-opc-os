#!/usr/bin/env python3
"""Sera Experience Harvester V0 — 把 GitHub 全部仓库的历史收割进 Memory Kernel.

每个仓库 → 1 个 Project 对象 (authority=founder)
README 技术选型 → Decision 对象
git 历史中的 fix/revert/修复 提交 → 失败 Experience (必须带具体 root_cause，过不了 Staging Gate 就跳过)
feat 中的发布/上线/launch 提交 → 成功 Experience
重复建设的仓库家族 → 失败 Experience (root_cause 指向"经验未入库")

用法:  python3 tools/harvest_experience.py [--owner 78tyih] [--include-forks] [--max-per-repo 5]
依赖:  gh CLI (已登录) + core/sera_memory_kernel (stdlib only)
幂等:  objects INSERT OR REPLACE；events 每次运行追加（V0 已知行为）。
"""
import argparse, base64, json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core" / "sera_memory_kernel"))
import kernel  # noqa: E402

TECH_KEYWORDS = {  # README 关键词 → (决策标签, 理由)
    "remotion": ("remotion-pipeline", "用 Remotion 代码化视频流水线，替代手工剪辑"),
    "next.js": ("nextjs-app", "Next.js App Router 作为前端骨架"),
    "nextjs": ("nextjs-app", "Next.js App Router 作为前端骨架"),
    "vite": ("vite-spa", "Vite + React SPA 快速交付"),
    "tailwind": ("tailwind-css", "Tailwind CSS 原子化样式"),
    "supabase": ("supabase-backend", "Supabase 作为托管后端"),
    "neon": ("neon-db", "Neon serverless Postgres 存业务数据"),
    "vercel": ("vercel-deploy", "Vercel 作为部署平台"),
    "cloudflare": ("cloudflare-pages", "Cloudflare Pages 部署"),
    "comfyui": ("comfyui-local", "ComfyUI 本地算力生成图像/视频"),
    "framer-motion": ("framer-motion", "framer-motion 驱动界面动效"),
    "@xyflow/react": ("xyflow-canvas", "xyflow/react 实现工作流画布"),
    "wecom": ("wecom-channel", "企业微信作为触达渠道"),
}

# 重复建设家族：同一业务/概念多次重建仓库。key=家族 id, value=(repos, root_cause)
REBUILD_FAMILIES = {
    "deltapex": (["dpxpropfirm", "dpxpropfirm1", "deltapex-trading-group-", "deltapex-site", "dp-"],
                 "德湃考试盘/官网多次重建仓库：前序项目的架构与教训未沉淀入库，每次从零开始"),
    "trader-assessment": (["trader-dna", "traderbti"],
                          "交易人格测评概念做了两版独立仓库：第一版的测评模型与转化漏斗经验未复用"),
    "sera-os-lineage": (["sera-agent-os", "sera-opc-os-v2-archive", "sera-control-center"],
                        "Sera 操作系统三次重构：架构蓝图多次重写，执行层代码沉淀不足"),
}

FAIL_COMMIT = re.compile(r"^(fix|hotfix|revert|bugfix)(\(|:)|修复|回滚", re.I)
SHIP_COMMIT = re.compile(r"^(feat|release)(\(|:)|上线|发布|launch", re.I)
TOO_GENERIC = re.compile(r"^(fix|bugfix|update|wip|fix bug|bug fix|修复|改bug|fix typo|misc)[\s.:!)]*$", re.I)

def sh(args, timeout=30):
    r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return r.stdout if r.returncode == 0 else ""

def slug(name):
    return kernel._slugify(name) or "unnamed"

def harvest(owner, include_forks, max_per_repo):
    repos = json.loads(sh(["gh", "repo", "list", owner, "--limit", "100", "--json",
                           "name,isFork,isArchived,isPrivate,description,primaryLanguage,createdAt,updatedAt,diskUsage"]) or "[]")
    conn = kernel.init_db()
    report, skipped = {"projects": 0, "decisions": 0, "experiences": 0, "gate_rejected": 0}, []

    repo_slugs = {slug(r["name"]) for r in repos}
    for repo in repos:
        if repo["isFork"] and not include_forks:
            continue
        s = slug(repo["name"])
        pid = f"project.{s}"
        res = kernel.object_store(conn, pid, "Project", repo["name"], "structured", "organization",
                                  authority="founder", status="archived" if repo["isArchived"] else "active",
                                  importance=0.7 if not repo["isArchived"] else 0.4, confidence=1.0,
                                  properties={"url": f"https://github.com/{owner}/{repo['name']}",
                                              "description": repo.get("description") or "",
                                              "language": (repo.get("primaryLanguage") or {}).get("name", ""),
                                              "private": repo["isPrivate"], "created_at": repo["createdAt"],
                                              "updated_at": repo["updatedAt"], "disk_usage_kb": repo["diskUsage"]},
                                  actor="founder")
        if isinstance(res, dict):
            report["gate_rejected"] += 1; skipped.append((pid, res["error"])); continue
        report["projects"] += 1

        readme = ""
        raw = sh(["gh", "api", f"repos/{owner}/{repo['name']}/readme", "--jq", ".content"])
        if raw.strip():
            try:
                readme = base64.b64decode(raw).decode("utf-8", "ignore").lower()
            except Exception:
                readme = ""
        for kw, (dkey, why) in TECH_KEYWORDS.items():
            if kw in readme:
                did = f"decision.{s}.{dkey}"
                r = kernel.object_store(conn, did, "Decision", f"{repo['name']}: {why}", "structured", "project",
                                        authority="project", importance=0.6, confidence=0.9,
                                        properties={"tech": kw, "rationale": why, "source": "readme"},
                                        actor="harvester")
                if isinstance(r, dict):
                    report["gate_rejected"] += 1; skipped.append((did, r["error"]))
                else:
                    kernel.relate(conn, did, pid, "part_of", 0.9)
                    report["decisions"] += 1

        commits = sh(["gh", "api", f"repos/{owner}/{repo['name']}/commits?per_page=60",
                      "--jq", ".[].commit.message"]).split("\n\n")
        n_fail = n_ship = 0
        for msg in commits:
            first = msg.strip().splitlines()[0].strip() if msg.strip() else ""
            if not first:
                continue
            if FAIL_COMMIT.search(first) and n_fail < max_per_repo:
                if TOO_GENERIC.match(first):
                    report["gate_rejected"] += 1; skipped.append((f"{s}::commit", f"提交信息过泛，无法提炼具体 root_cause: '{first[:40]}'"))
                    n_fail += 1; continue
                eid = f"experience.{s}.fix-{abs(hash(first)) % 99999}"
                r = kernel.object_store(conn, eid, "Experience", f"{repo['name']}: {first[:70]}", "learned", "project",
                                        authority="agent", status="draft", importance=0.6, confidence=0.55,
                                        properties={"result": "failure", "failure_mode": first[:120],
                                                    "root_cause": f"提交记录显示的缺陷: {first[:100]}",
                                                    "source": "git-log", "lesson": first[:120]},
                                        actor="harvester")
                if isinstance(r, dict):
                    report["gate_rejected"] += 1; skipped.append((eid, r["error"]))
                else:
                    kernel.relate(conn, eid, pid, "part_of", 0.7)
                    report["experiences"] += 1
                n_fail += 1
            elif SHIP_COMMIT.search(first) and n_ship < 3:
                eid = f"experience.{s}.ship-{abs(hash(first)) % 99999}"
                r = kernel.object_store(conn, eid, "Experience", f"{repo['name']}: {first[:70]}", "learned", "project",
                                        authority="agent", status="draft", importance=0.5, confidence=0.5,
                                        properties={"result": "success", "source": "git-log", "lesson": first[:120]},
                                        actor="harvester")
                if not isinstance(r, dict):
                    kernel.relate(conn, eid, pid, "part_of", 0.5)
                    report["experiences"] += 1
                n_ship += 1

    for fam, (members, root_cause) in REBUILD_FAMILIES.items():
        present = [m for m in members if m in repo_slugs]
        for m in present[1:]:  # 第一个仓库是起点，其余都是"重建"
            eid = f"experience.{m}.rebuild-{fam}"
            r = kernel.object_store(conn, eid, "Experience", f"重复建设: {m} (家族 {fam})", "learned", "organization",
                                    authority="agent", status="draft", importance=0.8, confidence=0.75,
                                    properties={"result": "failure", "failure_mode": "repo-rebuild",
                                                "root_cause": root_cause, "family": fam,
                                                "lesson": "同类项目开工前先查记忆图谱，复用已有经验与代码"},
                                    actor="harvester")
            if isinstance(r, dict):
                report["gate_rejected"] += 1; skipped.append((eid, r["error"]))
            else:
                kernel.relate(conn, eid, f"project.{m}", "part_of", 0.9)
                report["experiences"] += 1

    return conn, report, skipped

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", default="78tyih")
    ap.add_argument("--include-forks", action="store_true")
    ap.add_argument("--max-per-repo", type=int, default=5)
    args = ap.parse_args()
    conn, report, skipped = harvest(args.owner, args.include_forks, args.max_per_repo)
    print("=== Harvest 完成 ===")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if skipped:
        print(f"\n--- Staging Gate 拦截/跳过 {len(skipped)} 条 (前 10) ---")
        for oid, err in skipped[:10]:
            print(f"  [SKIP] {oid}: {err}")
    print("\n=== Kernel stats() ===")
    print(json.dumps(kernel.stats(conn), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
