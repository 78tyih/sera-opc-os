"""Transport-neutral GitHub release adapter for Sera Learning OS.

The adapter converts a prepared Release Request into an ordered action plan that a
GitHub connector, MCP server, Codex tool, or `gh` wrapper can execute. It has no policy
or approval authority and never decides whether a release should be merged.
"""

from __future__ import annotations

import hashlib
from typing import Optional

from .release_controller import get_release_request


def build_github_action_plan(conn, request_id: str) -> dict:
    """Return the exact GitHub operations required to materialize a Draft PR."""
    request = get_release_request(conn, request_id)
    if request is None:
        return {"error": f"release request not found: {request_id}"}
    if request.get("state") != "prepared":
        return {"error": f"release request must be prepared before GitHub materialization; state={request.get('state')}"}

    payload = request.get("payload") or {}
    pr = payload.get("pr") or {}
    return {
        "request_id": request_id,
        "repository": request["target_repo"],
        "base_branch": request["base_branch"],
        "candidate_branch": request["candidate_branch"],
        "expected_baseline_sha256": request["baseline_sha256"],
        "candidate_sha256": request["candidate_sha256"],
        "actions": [
            {
                "order": 1,
                "action": "create_branch",
                "repository": request["target_repo"],
                "branch": request["candidate_branch"],
                "base": request["base_branch"],
            },
            {
                "order": 2,
                "action": "write_candidate_file",
                "repository": request["target_repo"],
                "branch": request["candidate_branch"],
                "path": request["skill_path"],
                "content": payload.get("candidate_content", ""),
                "candidate_sha256": request["candidate_sha256"],
                "expected_baseline_sha256": request["baseline_sha256"],
            },
            {
                "order": 3,
                "action": "create_pull_request",
                "repository": request["target_repo"],
                "head": request["candidate_branch"],
                "base": request["base_branch"],
                "title": pr.get("title"),
                "body": pr.get("body"),
                "draft": True,
            },
        ],
        "next_release_event": "draft_pr_opened",
        "approval_required_after_ci": True,
        "merge_authorized": False,
    }


def validate_github_materialization_receipt(
    conn,
    *,
    request_id: str,
    repository: str,
    branch: str,
    written_path: str,
    written_content: str,
    pr_number: int,
    pr_draft: bool,
    head_sha: Optional[str] = None,
) -> dict:
    """Validate tool receipts before recording `draft_pr_opened`.

    The function does not call GitHub and does not append release events. It simply
    verifies that the transport layer materialized the exact candidate that the
    Release Controller approved for PR creation.
    """
    request = get_release_request(conn, request_id)
    if request is None:
        return {"error": f"release request not found: {request_id}"}
    if request.get("state") != "prepared":
        return {"error": f"receipt validation requires prepared state; state={request.get('state')}"}

    payload = request.get("payload") or {}
    actual_sha = hashlib.sha256(written_content.encode("utf-8")).hexdigest()
    mismatches = []
    if repository != request["target_repo"]:
        mismatches.append("repository")
    if branch != request["candidate_branch"]:
        mismatches.append("candidate_branch")
    if written_path != request["skill_path"]:
        mismatches.append("skill_path")
    if actual_sha != request["candidate_sha256"]:
        mismatches.append("candidate_content_sha256")
    if not pr_draft:
        mismatches.append("pr_must_be_draft")
    if not isinstance(pr_number, int) or pr_number <= 0:
        mismatches.append("pr_number")

    if mismatches:
        return {
            "request_id": request_id,
            "valid": False,
            "mismatches": mismatches,
            "next_release_event": None,
        }

    return {
        "request_id": request_id,
        "valid": True,
        "pr_number": pr_number,
        "head_sha": head_sha,
        "branch": branch,
        "candidate_sha256": actual_sha,
        "next_release_event": "draft_pr_opened",
        "release_event_payload": {
            "pr_number": pr_number,
            "head_sha": head_sha,
            "candidate_branch": branch,
        },
        "merge_authorized": False,
    }
