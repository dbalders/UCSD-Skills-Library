#!/usr/bin/env python3
"""GitHub webhook receiver that reviews public-skills PRs and issues through Codex app-server."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import logging
import os
import queue
import re
import select
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import public_skill_validator as skill_validator


ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- ucsd-public-skills-codex-pr-review -->"
ISSUE_MARKER = "<!-- ucsd-public-skills-codex-issue-review -->"
DEFAULT_CODEX = "/Applications/Codex.app/Contents/Resources/codex"
REVIEW_ACTIONS = {"opened", "reopened", "synchronize", "ready_for_review", "edited"}
ISSUE_ACTIONS = {"opened", "reopened", "edited"}
SENSITIVE_ENV_MARKERS = ("TOKEN", "SECRET", "PASSWORD", "PASSWD", "API_KEY", "ACCESS_KEY", "PRIVATE_KEY")
LOG = logging.getLogger("public-pr-review-service")


@dataclass
class CommandResult:
    label: str
    command: list[str]
    returncode: int
    output: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def markdown(self, limit: int = 6000) -> str:
        status = "PASS" if self.ok else "FAIL"
        command = " ".join(redact_command(self.command))
        output = truncate(redact_text(self.output.strip() or "(no output)"), limit)
        return f"### {self.label}: {status}\n\n`{command}`\n\n```text\n{output}\n```"


@dataclass(frozen=True)
class ReviewJob:
    owner: str
    repo: str
    number: int
    head_sha: str
    action: str
    delivery_id: str
    kind: str = "pull_request"


@dataclass
class ReviewContext:
    args: argparse.Namespace
    client: GitHubClient
    state_dir: Path
    state_path: Path
    state: dict[str, Any]
    state_lock: threading.Lock
    token: str | None
    jobs: "queue.Queue[ReviewJob]"
    repo_filter: tuple[str, str] | None


class GitHubError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str | None, api_url: str = "https://api.github.com") -> None:
        self.token = token
        self.api_url = api_url.rstrip("/")

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        body = None
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "ucsd-public-skills-codex-pr-reviewer",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(f"{self.api_url}{path}", data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GitHubError(f"GitHub API {method} {path} failed: {exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise GitHubError(f"GitHub API {method} {path} failed: {exc}") from exc

        return json.loads(raw) if raw else None

    def get_pull(self, owner: str, repo: str, number: int) -> dict[str, Any]:
        return self.request("GET", f"/repos/{owner}/{repo}/pulls/{number}")

    def get_issue(self, owner: str, repo: str, number: int) -> dict[str, Any]:
        return self.request("GET", f"/repos/{owner}/{repo}/issues/{number}")

    def list_issue_comments(self, owner: str, repo: str, number: int) -> list[dict[str, Any]]:
        comments: list[dict[str, Any]] = []
        page = 1
        while True:
            query = urllib.parse.urlencode({"per_page": 100, "page": page})
            chunk = self.request("GET", f"/repos/{owner}/{repo}/issues/{number}/comments?{query}")
            if not chunk:
                return comments
            comments.extend(chunk)
            if len(chunk) < 100:
                return comments
            page += 1

    def create_review_comment(self, owner: str, repo: str, number: int, body: str) -> int:
        created = self.request("POST", f"/repos/{owner}/{repo}/issues/{number}/comments", {"body": body})
        return int(created["id"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="Only accept events for owner/name. Defaults to git remote origin.")
    parser.add_argument("--remote", default="origin", help="Local git remote name used for refs.")
    parser.add_argument("--host", default=os.environ.get("PR_REVIEW_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PR_REVIEW_PORT", "8787")))
    parser.add_argument("--path", default=os.environ.get("PR_REVIEW_WEBHOOK_PATH", "/github/webhook"))
    parser.add_argument("--review-pr", type=int, action="append", help="Manually review this PR number and exit.")
    parser.add_argument("--review-issue", type=int, action="append", help="Manually review this issue number and exit.")
    parser.add_argument("--force", action="store_true", help="Review even if the head SHA was already reviewed.")
    parser.add_argument("--dry-run", action="store_true", help="Print comments instead of posting to GitHub.")
    parser.add_argument("--skip-drafts", action="store_true", help="Skip draft pull requests.")
    parser.add_argument("--allow-unsigned", action="store_true", help="Allow unsigned webhook requests. Use only locally.")
    parser.add_argument(
        "--state-dir",
        default=os.environ.get("PR_REVIEW_STATE_DIR", str(ROOT / ".public-pr-reviewer")),
        help="Directory for local state, logs, and temporary worktrees.",
    )
    parser.add_argument(
        "--codex-path",
        default=os.environ.get("CODEX_PATH") or (DEFAULT_CODEX if Path(DEFAULT_CODEX).exists() else "codex"),
        help="Path to the Codex CLI.",
    )
    parser.add_argument("--codex-model", default=os.environ.get("CODEX_MODEL", "gpt-5.5"))
    parser.add_argument("--codex-effort", default=os.environ.get("CODEX_REASONING_EFFORT", "high"))
    parser.add_argument("--codex-timeout", type=int, default=int(os.environ.get("CODEX_TIMEOUT_SECONDS", "3600")))
    parser.add_argument(
        "--codex-remote",
        default=os.environ.get("CODEX_REMOTE", "stdio://"),
        help="Codex app-server transport. Only stdio:// is currently supported by this reviewer.",
    )
    parser.add_argument("--github-api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com"))
    parser.add_argument("--max-webhook-bytes", type=int, default=int(os.environ.get("PR_REVIEW_MAX_WEBHOOK_BYTES", "10485760")))
    parser.add_argument("--log-level", default=os.environ.get("PR_REVIEW_LOG_LEVEL", "INFO"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )

    state_dir = Path(args.state_dir).resolve()
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "worktrees").mkdir(parents=True, exist_ok=True)

    token = os.environ.get("PR_REVIEW_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    webhook_secret = os.environ.get("PR_REVIEW_WEBHOOK_SECRET") or os.environ.get("WEBHOOK_SECRET")
    if not token and not args.dry_run:
        LOG.error("Set PR_REVIEW_GITHUB_TOKEN, GITHUB_TOKEN, or GH_TOKEN before posting GitHub comments.")
        return 2
    if not webhook_secret and not args.allow_unsigned and not args.review_pr and not args.review_issue:
        LOG.error("Set PR_REVIEW_WEBHOOK_SECRET or pass --allow-unsigned for local-only testing.")
        return 2

    repo_filter = parse_repo(args.repo) if args.repo else detect_repo(args.remote)
    context = ReviewContext(
        args=args,
        client=GitHubClient(token=token, api_url=args.github_api_url),
        state_dir=state_dir,
        state_path=state_dir / "state.json",
        state=load_state(state_dir / "state.json"),
        state_lock=threading.Lock(),
        token=token,
        jobs=queue.Queue(),
        repo_filter=repo_filter,
    )

    if args.review_pr:
        owner, repo = repo_filter
        for number in args.review_pr:
            pull = context.client.get_pull(owner, repo, number)
            process_job(context, ReviewJob(owner, repo, number, str(pull["head"]["sha"]), "manual", "manual"))
        return 0
    if args.review_issue:
        owner, repo = repo_filter
        for number in args.review_issue:
            issue = context.client.get_issue(owner, repo, number)
            process_job(
                context,
                ReviewJob(owner, repo, number, str(issue.get("updated_at") or issue.get("node_id") or ""), "manual", "manual", "issue"),
            )
        return 0

    worker = threading.Thread(target=worker_loop, args=(context,), daemon=True)
    worker.start()

    server = ThreadingHTTPServer((args.host, args.port), make_handler(context, webhook_secret))
    LOG.info("Webhook receiver listening on http://%s:%s%s", args.host, args.port, args.path)
    LOG.info("Accepting GitHub pull_request actions: %s", ", ".join(sorted(REVIEW_ACTIONS)))
    LOG.info("Accepting GitHub issues actions: %s", ", ".join(sorted(ISSUE_ACTIONS)))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOG.info("Stopping")
        server.shutdown()
        return 130


def make_handler(context: ReviewContext, webhook_secret: str | None) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/healthz":
                self.respond(HTTPStatus.OK, {"ok": True, "queued": context.jobs.qsize()})
                return
            self.respond(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            if urllib.parse.urlsplit(self.path).path != context.args.path:
                self.respond(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            try:
                raw = self.read_body()
                if not context.args.allow_unsigned:
                    verify_signature(raw, self.headers.get("X-Hub-Signature-256"), webhook_secret)
                event = self.headers.get("X-GitHub-Event", "")
                delivery = self.headers.get("X-GitHub-Delivery", "")
                payload = json.loads(raw.decode("utf-8"))
                accepted = handle_webhook_payload(context, event, delivery, payload)
            except PermissionError as exc:
                LOG.warning("Rejected webhook: %s", exc)
                self.respond(HTTPStatus.UNAUTHORIZED, {"error": str(exc)})
                return
            except ValueError as exc:
                LOG.warning("Bad webhook payload: %s", exc)
                self.respond(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
                return
            except Exception as exc:
                LOG.exception("Webhook handling failed")
                self.respond(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})
                return
            self.respond(HTTPStatus.ACCEPTED if accepted else HTTPStatus.OK, {"accepted": accepted})

        def read_body(self) -> bytes:
            length = int(self.headers.get("Content-Length", "0"))
            if length > context.args.max_webhook_bytes:
                raise ValueError("webhook payload is too large")
            return self.rfile.read(length)

        def respond(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            raw = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def log_message(self, fmt: str, *args: Any) -> None:
            LOG.info("%s - %s", self.address_string(), fmt % args)

    return Handler


def handle_webhook_payload(context: ReviewContext, event: str, delivery: str, payload: dict[str, Any]) -> bool:
    if event == "ping":
        LOG.info("Received GitHub webhook ping")
        return False

    action = str(payload.get("action") or "")
    if event == "pull_request" and action not in REVIEW_ACTIONS:
        LOG.info("Ignoring pull_request action %s", action)
        return False
    if event == "issues" and action not in ISSUE_ACTIONS:
        LOG.info("Ignoring issues action %s", action)
        return False
    if event not in {"pull_request", "issues"}:
        LOG.info("Ignoring GitHub event %s", event)
        return False

    repo_info = payload.get("repository") or {}
    owner, repo = parse_repo(str(repo_info.get("full_name") or ""))
    if context.repo_filter and (owner, repo) != context.repo_filter:
        LOG.warning("Ignoring webhook for unexpected repo %s/%s", owner, repo)
        return False

    if event == "pull_request":
        pull = payload.get("pull_request") or {}
        job = ReviewJob(owner, repo, int(pull["number"]), str(pull.get("head", {}).get("sha") or ""), action, delivery)
        context.jobs.put(job)
        LOG.info("Queued PR #%s from %s at %s", job.number, action, job.head_sha[:12])
        return True

    issue = payload.get("issue") or {}
    if issue.get("pull_request"):
        LOG.info("Ignoring issues event for pull request #%s", issue.get("number"))
        return False
    job = ReviewJob(
        owner,
        repo,
        int(issue["number"]),
        str(issue.get("updated_at") or issue.get("node_id") or ""),
        action,
        delivery,
        "issue",
    )
    context.jobs.put(job)
    LOG.info("Queued issue #%s from %s at %s", job.number, action, job.head_sha)
    return True


def worker_loop(context: ReviewContext) -> None:
    while True:
        job = context.jobs.get()
        try:
            process_job(context, job)
        except Exception:
            LOG.exception("Review job failed for %s/%s#%s", job.owner, job.repo, job.number)
        finally:
            context.jobs.task_done()


def process_job(context: ReviewContext, job: ReviewJob) -> None:
    if job.kind == "issue":
        process_issue_job(context, job)
        return

    pull = context.client.get_pull(job.owner, job.repo, job.number)
    number = int(pull["number"])
    title = str(pull.get("title") or "")
    head_sha = str(pull["head"]["sha"])
    key = f"{job.owner}/{job.repo}#{number}"

    if context.args.skip_drafts and pull.get("draft"):
        LOG.info("Skipping draft PR #%s: %s", number, title)
        return
    with context.state_lock:
        already_reviewed = context.state.get("pulls", {}).get(key, {}).get("head_sha") == head_sha
    if already_reviewed and not context.args.force:
        LOG.info("Skipping PR #%s at %s; already reviewed", number, head_sha[:12])
        return

    LOG.info("Reviewing PR #%s at %s from %s: %s", number, head_sha[:12], job.action, title)
    body, review_succeeded = review_pull(context.args, pull, context.state_dir, job.owner, job.repo, context.token)
    comment_id: int | None
    if context.args.dry_run:
        print(f"\n--- PR #{number} dry-run comment ---\n{body}\n")
        comment_id = None
    else:
        comment_id = context.client.create_review_comment(job.owner, job.repo, number, body)
        LOG.info("Posted review comment %s for PR #%s", comment_id, number)

    with context.state_lock:
        state_entry = {
            "comment_id": comment_id,
            "reviewed_at": now_iso(),
            "title": title,
            "last_delivery_id": job.delivery_id,
            "last_action": job.action,
        }
        if review_succeeded:
            state_entry["head_sha"] = head_sha
        else:
            state_entry["failed_head_sha"] = head_sha
        context.state.setdefault("pulls", {})[key] = state_entry
        save_state(context.state_path, context.state)


def process_issue_job(context: ReviewContext, job: ReviewJob) -> None:
    issue = context.client.get_issue(job.owner, job.repo, job.number)
    number = int(issue["number"])
    title = str(issue.get("title") or "")
    updated_at = str(issue.get("updated_at") or issue.get("node_id") or "")
    key = f"{job.owner}/{job.repo}#{number}"

    if issue.get("pull_request"):
        LOG.info("Skipping issue #%s because it is a pull request", number)
        return
    with context.state_lock:
        already_reviewed = context.state.get("issues", {}).get(key, {}).get("updated_at") == updated_at
    if already_reviewed and not context.args.force:
        LOG.info("Skipping issue #%s at %s; already reviewed", number, updated_at)
        return

    LOG.info("Reviewing issue #%s at %s from %s: %s", number, updated_at, job.action, title)
    body, review_succeeded = review_issue(context.args, issue, job.owner, job.repo)
    comment_id: int | None
    if context.args.dry_run:
        print(f"\n--- Issue #{number} dry-run comment ---\n{body}\n")
        comment_id = None
    else:
        comment_id = context.client.create_review_comment(job.owner, job.repo, number, body)
        LOG.info("Posted review comment %s for issue #%s", comment_id, number)

    with context.state_lock:
        state_entry = {
            "comment_id": comment_id,
            "reviewed_at": now_iso(),
            "title": title,
            "last_delivery_id": job.delivery_id,
            "last_action": job.action,
        }
        if review_succeeded:
            state_entry["updated_at"] = updated_at
        else:
            state_entry["failed_updated_at"] = updated_at
        context.state.setdefault("issues", {})[key] = state_entry
        save_state(context.state_path, context.state)


def review_pull(
    args: argparse.Namespace,
    pull: dict[str, Any],
    state_dir: Path,
    owner: str,
    repo: str,
    token: str | None,
) -> tuple[str, bool]:
    number = int(pull["number"])
    head_sha = str(pull["head"]["sha"])
    base_ref = str(pull["base"]["ref"])
    base_sha = str(pull["base"]["sha"])
    worktree = state_dir / "worktrees" / f"pr-{number}-{head_sha[:12]}"

    cleanup_worktree(worktree)
    try:
        prepare_worktree(args.remote, owner, repo, number, base_ref, worktree, token)
        contributor = str((pull.get("user") or {}).get("login") or "")
        checks = run_local_checks(worktree, base_ref, contributor, state_dir)
        failed_checks = [check for check in checks if not check.ok]
        if failed_checks:
            return local_checks_blocked_comment(pull, checks, failed_checks), True
        prompt = build_codex_prompt(pull, owner, repo, base_ref, base_sha, head_sha, checks)
        codex_body = run_codex(args, worktree, prompt)
        return normalize_comment(codex_body, pull, checks), True
    except Exception as exc:
        LOG.exception("PR #%s review failed", number)
        return failure_comment(pull, base_ref, head_sha, exc), False
    finally:
        cleanup_worktree(worktree)


def review_issue(
    args: argparse.Namespace,
    issue: dict[str, Any],
    owner: str,
    repo: str,
) -> tuple[str, bool]:
    number = int(issue["number"])
    updated_at = str(issue.get("updated_at") or "")
    try:
        prompt = build_issue_prompt(issue, owner, repo)
        codex_body = run_codex(args, ROOT, prompt)
        return normalize_issue_comment(codex_body, issue), True
    except Exception as exc:
        LOG.exception("Issue #%s review failed", number)
        return failure_issue_comment(issue, updated_at, exc), False


def prepare_worktree(
    remote: str,
    owner: str,
    repo: str,
    number: int,
    base_ref: str,
    worktree: Path,
    token: str | None,
) -> None:
    fetch_env = git_env(token)
    remote_url = fetch_url(remote, owner, repo, token)
    run_or_raise(["git", "fetch", "--no-tags", remote_url, f"+refs/heads/{base_ref}:refs/remotes/{remote}/{base_ref}"], ROOT, fetch_env)
    run_or_raise(["git", "fetch", "--no-tags", remote_url, f"+refs/pull/{number}/head:refs/remotes/{remote}/pr/{number}"], ROOT, fetch_env)
    run_or_raise(["git", "worktree", "add", "--detach", str(worktree), f"refs/remotes/{remote}/pr/{number}"], ROOT, os.environ.copy())


def cleanup_worktree(worktree: Path) -> None:
    if not worktree.exists():
        return
    subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if worktree.exists():
        shutil.rmtree(worktree)


def run_local_checks(
    worktree: Path,
    base_ref: str,
    contributor: str = "",
    state_dir: Path | None = None,
) -> list[CommandResult]:
    checks = [
        run_command("Changed files", ["git", "diff", "--name-status", f"origin/{base_ref}...HEAD"], worktree, timeout=120),
        run_command("Diff stat", ["git", "diff", "--stat", f"origin/{base_ref}...HEAD"], worktree, timeout=120),
        run_command("PR diff", ["git", "diff", "--no-ext-diff", "--unified=80", f"origin/{base_ref}...HEAD"], worktree, timeout=120),
        run_command("Whitespace check", ["git", "diff", "--check", f"origin/{base_ref}...HEAD"], worktree, timeout=120),
    ]
    changed = changed_files(worktree, base_ref)
    checks.append(check_contributor_placement(contributor, changed, state_dir))
    checks.append(check_public_skill_format(worktree))
    checks.append(check_changed_file_leaks(worktree, changed))
    return checks


def changed_files(worktree: Path, base_ref: str) -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"],
        cwd=worktree,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=scrubbed_env(),
    )
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def validation_command_result(
    result: skill_validator.ValidationResult,
    command: list[str],
) -> CommandResult:
    return CommandResult(result.label, command, 0 if result.ok else 1, result.output())


def check_contributor_placement(
    contributor: str,
    changed: list[Path],
    state_dir: Path | None = None,
) -> CommandResult:
    allowlist_path = state_dir / "ai-team-allowlist.txt" if state_dir is not None else None
    result = skill_validator.validate_contributor_placement(contributor, changed, allowlist_path)
    return validation_command_result(result, ["public-contributor-placement"])


def check_public_skill_format(worktree: Path) -> CommandResult:
    result = skill_validator.validate_public_skill_format(worktree)
    return validation_command_result(result, ["public-format-check"])


def check_changed_file_leaks(worktree: Path, changed: list[Path]) -> CommandResult:
    result = skill_validator.validate_changed_file_leaks(worktree, changed)
    return validation_command_result(result, ["public-leak-scan"])


def run_codex(args: argparse.Namespace, worktree: Path, prompt: str) -> str:
    command, label = codex_app_server_command(args)
    LOG.info("Starting Codex app-server review via %s with %s / %s", label, args.codex_model, args.codex_effort)
    output = run_codex_app_server(command, args, worktree, prompt)
    if not output.strip():
        raise RuntimeError("Codex app-server finished without producing a review body")
    return output.strip()


def codex_app_server_command(args: argparse.Namespace) -> tuple[list[str], str]:
    remote = args.codex_remote or "stdio://"
    if remote == "stdio://":
        return [args.codex_path, "app-server", "--stdio"], "stdio://"
    if remote.startswith(("ws://", "wss://")):
        raise RuntimeError(
            "Codex websocket remotes are supported by the interactive TUI, not by this noninteractive reviewer. "
            "Use CODEX_REMOTE=stdio:// so the reviewer talks to a local Codex app-server over stdio."
        )
    if remote.startswith("unix://"):
        raise RuntimeError(
            "Codex unix-socket app-server proxy mode is not supported by this reviewer yet. "
            "Use CODEX_REMOTE=stdio:// so the reviewer starts a local Codex app-server over stdio."
        )
    raise RuntimeError(f"Unsupported Codex app-server transport: {remote}")


def run_codex_app_server(command: list[str], args: argparse.Namespace, worktree: Path, prompt: str) -> str:
    process = subprocess.Popen(
        command,
        cwd=worktree,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=scrubbed_env(),
    )
    if process.stdin is None or process.stdout is None:
        raise RuntimeError("Codex app-server did not expose stdio pipes")

    stderr_lines: list[str] = []

    def read_stderr() -> None:
        if process.stderr is None:
            return
        for line in process.stderr:
            stderr_lines.append(line)

    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
    stderr_thread.start()
    deadline = time.monotonic() + args.codex_timeout
    request_counter = 0
    final_message: str | None = None
    error_notifications: list[str] = []

    def send(payload: dict[str, Any]) -> None:
        process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        process.stdin.flush()

    def request(method: str, params: dict[str, Any]) -> str:
        nonlocal request_counter
        request_counter += 1
        request_id = f"public-pr-review-{request_counter}"
        send({"id": request_id, "method": method, "params": params})
        return request_id

    def notify(method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"method": method}
        if params is not None:
            payload["params"] = params
        send(payload)

    def respond(request_id: str, result: dict[str, Any] | None = None, error: str | None = None) -> None:
        if error:
            send({"id": request_id, "error": {"code": -32000, "message": error}})
        else:
            send({"id": request_id, "result": result})

    def handle_server_request(message: dict[str, Any]) -> bool:
        request_id = message.get("id")
        method = message.get("method")
        if not request_id or not method or "result" in message or "error" in message:
            return False
        if method == "item/commandExecution/requestApproval":
            respond(request_id, {"decision": "decline"})
        elif method == "item/fileChange/requestApproval":
            respond(request_id, {"decision": "decline"})
        elif method in {"execCommandApproval", "applyPatchApproval"}:
            respond(request_id, {"decision": "denied"})
        elif method == "item/permissions/requestApproval":
            respond(request_id, {"permissions": {}, "scope": "turn", "strictAutoReview": True})
        elif method == "item/tool/requestUserInput":
            respond(request_id, {"answers": {}})
        elif method == "mcpServer/elicitation/request":
            respond(request_id, {"action": "decline", "content": None, "_meta": None})
        elif method == "item/tool/call":
            respond(request_id, {"contentItems": [], "success": False})
        else:
            respond(request_id, error=f"Unsupported app-server request during automated PR review: {method}")
        return True

    def read_message() -> dict[str, Any]:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(app_server_failure(process.returncode, stderr_lines))
            timeout = min(1.0, max(0.0, deadline - time.monotonic()))
            readable, _, _ = select.select([process.stdout], [], [], timeout)
            if not readable:
                continue
            line = process.stdout.readline()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                stderr_lines.append(f"non-json stdout: {line}")
                continue
            if handle_server_request(message):
                continue
            return message
        raise TimeoutError(app_server_timeout(args.codex_timeout, stderr_lines))

    def wait_for_response(request_id: str) -> dict[str, Any]:
        while True:
            message = read_message()
            observe(message)
            if message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError(f"Codex app-server request {request_id} failed: {message['error']}")
                return message.get("result") or {}

    def observe(message: dict[str, Any]) -> None:
        nonlocal final_message
        method = message.get("method")
        params = message.get("params") if isinstance(message.get("params"), dict) else {}
        if method == "error":
            error_notifications.append(json.dumps(params, sort_keys=True)[:2000])
        elif method == "item/completed":
            item = params.get("item") if isinstance(params.get("item"), dict) else {}
            if item.get("type") == "agentMessage":
                final_message = str(item.get("text") or "")

    try:
        initialize_id = request(
            "initialize",
            {
                "clientInfo": {
                    "name": "ucsd-public-skills-pr-reviewer",
                    "title": "UCSD Public Skills PR Reviewer",
                    "version": "0.1.0",
                },
                "capabilities": {
                    "experimentalApi": True,
                    "requestAttestation": False,
                    "optOutNotificationMethods": [
                        "command/exec/outputDelta",
                        "item/agentMessage/delta",
                        "item/plan/delta",
                        "item/fileChange/outputDelta",
                        "item/reasoning/summaryTextDelta",
                        "item/reasoning/textDelta",
                    ],
                },
            },
        )
        wait_for_response(initialize_id)
        notify("initialized")

        thread_result = wait_for_response(
            request(
                "thread/start",
                {
                    "model": args.codex_model,
                    "cwd": str(worktree),
                    "approvalPolicy": "never",
                    "approvalsReviewer": "user",
                    "sandbox": "read-only",
                    "config": {"model_reasoning_effort": args.codex_effort},
                    "serviceName": "ucsd-public-skills-pr-reviewer",
                    "ephemeral": True,
                },
            )
        )
        thread = thread_result.get("thread") if isinstance(thread_result.get("thread"), dict) else {}
        thread_id = str(thread.get("id") or "")
        if not thread_id:
            raise RuntimeError(f"Codex app-server did not return a thread id: {thread_result}")

        wait_for_response(
            request(
                "turn/start",
                {
                    "threadId": thread_id,
                    "input": [{"type": "text", "text": prompt, "text_elements": []}],
                    "cwd": str(worktree),
                    "approvalPolicy": "never",
                    "sandboxPolicy": {"type": "readOnly", "networkAccess": False},
                    "model": args.codex_model,
                    "effort": args.codex_effort,
                },
            )
        )

        while True:
            message = read_message()
            observe(message)
            if message.get("method") != "turn/completed":
                continue
            params = message.get("params") if isinstance(message.get("params"), dict) else {}
            turn = params.get("turn") if isinstance(params.get("turn"), dict) else {}
            status = turn.get("status")
            if status != "completed":
                detail = json.dumps(turn.get("error") or error_notifications or turn, indent=2, sort_keys=True)
                raise RuntimeError(f"Codex app-server turn ended with status {status}:\n{truncate(detail, 8000)}")
            if final_message is None:
                raise RuntimeError("Codex app-server turn completed without a final agent message")
            return final_message
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        stderr_thread.join(timeout=1)


def app_server_failure(returncode: int | None, stderr_lines: list[str]) -> str:
    stderr = truncate("".join(stderr_lines[-80:]).strip() or "(no stderr)", 8000)
    return f"Codex app-server exited {returncode} before completing the review:\n{stderr}"


def app_server_timeout(timeout_seconds: int, stderr_lines: list[str]) -> str:
    stderr = truncate("".join(stderr_lines[-80:]).strip() or "(no stderr)", 8000)
    return f"Codex app-server review timed out after {timeout_seconds} seconds:\n{stderr}"


def build_codex_prompt(
    pull: dict[str, Any],
    owner: str,
    repo: str,
    base_ref: str,
    base_sha: str,
    head_sha: str,
    checks: list[CommandResult],
) -> str:
    checks_markdown = "\n\n".join(check.markdown(limit=80000 if check.label == "PR diff" else 6000) for check in checks)
    pr_title = redact_text(str(pull.get("title") or ""))
    pr_body = redact_text(str(pull.get("body") or "(no PR body)"))
    return f"""You are reviewing a pull request for the public UCSD Skills Library.

Write the exact GitHub PR comment body that should be posted. Return only Markdown.

Pull request:
- Repo: {owner}/{repo}
- PR: #{pull["number"]}
- Title: {pr_title}
- Author: redacted by reviewer
- Draft: {"yes" if pull.get("draft") else "no"}
- Base: {base_ref} ({base_sha})
- Head: {head_sha}
- Body: {pr_body}

Review standard:
- Treat README.md, CONTRIBUTING.md, SECURITY.md, AGENTS.md, .github/CODEOWNERS, and .github/PULL_REQUEST_TEMPLATE.md as authoritative.
- This repo is public. It must not contain secrets, credentials, protected data, private infrastructure details, production exports, logs, screenshots with real data, token caches, private keys, kubeconfigs, auth cookies, private hostnames, private account IDs, or internal-only runbooks.
- Only privately authorized authors may contribute to `tritonai/`. Use the automated Contributor placement output as source of truth. Do not ask for, print, infer, or name private authorization membership. For non-blocking placement output, say only that no public placement action is being reported. For blocking placement output, say that TritonAI placement requires maintainer verification before merge and tell the contributor to move the skill to `community/<skill-name>/` and add `maintainer:` unless a maintainer confirms private placement approval.
- Decide whether changed skills belong here or should move to UCSD-Skills-Library-Secure. Public fit includes reusable public-safe guidance, public documentation navigation, source-backed UCSD/TritonAI workflows, and generic safety rules that do not depend on restricted access.
- Secure-only fit includes internal/restricted UCSD or TritonAI workflows, private infrastructure assumptions, deployment handoffs, authentication flows, restricted data handling, operational runbooks, private hostnames/accounts, or maintained secure operations. Call those out as likely belonging in UCSD-Skills-Library-Secure instead.
- Check public skill layout, SKILL.md frontmatter, concrete description trigger, community `maintainer:`, minimal allowed-tools, references/assets/scripts ownership, explicit human confirmation gates, and clear "agent boundary" language.
- For scripts and assets, review hidden network calls, secret handling, mutation of external systems, provenance, checksums, and whether any external action is left to the right human/team boundary.
- Use the automated command output below as evidence, including the redacted PR diff. Do not assume access to additional repository tools.
- Do not modify files. Do not approve unsafe changes just because automated checks pass.
- Be concise, specific, and constructive. Include file paths and line numbers for required fixes when you can.
- Never print a discovered secret. Refer to the file/path and the type of issue instead.

Required output format:
{MARKER}
## Codex Public Skills Review

**Verdict:** one of `Good to merge`, `Needs fixes`, or `Blocked`
**Reviewed commit:** `{head_sha}`

### Gate Results
- Public repo fit: pass/fail/inconclusive and why.
- Contributor placement: use neutral public wording. Say `no public placement action reported` unless deterministic output requires maintainer verification; do not state pass/fail or authorization status.
- Leakage/public boundary safety: pass/fail/inconclusive and why.
- Contributing format: pass/fail and why.

### Required Fixes
- If there are no required fixes, write `None`.

### Notes
- Mention non-blocking follow-ups, risk, or reviewer attention areas.

Automated command output:

{checks_markdown}
"""


def build_issue_prompt(issue: dict[str, Any], owner: str, repo: str) -> str:
    title = redact_text(str(issue.get("title") or ""))
    body = redact_text(str(issue.get("body") or "(no issue body)"))
    labels = ", ".join(sorted(str(label.get("name") or "") for label in issue.get("labels") or [] if label.get("name")))
    docs = "\n\n".join(
        repo_doc_excerpt(path)
        for path in [
            "README.md",
            "CONTRIBUTING.md",
            "AGENTS.md",
            ".github/ISSUE_TEMPLATE",
            ".github/PULL_REQUEST_TEMPLATE.md",
        ]
    )
    return f"""You are reviewing a GitHub issue for the public UCSD Skills Library.

Write the exact GitHub issue comment body that should be posted. Return only Markdown.

Issue:
- Repo: {owner}/{repo}
- Issue: #{issue["number"]}
- Title: {title}
- Author: redacted by reviewer
- State: {issue.get("state")}
- Labels: {labels or "(none)"}
- Updated at: {issue.get("updated_at")}
- Body: {body}

Review standard:
- This repository is public and contains reusable agent skills. The issue should not ask contributors to add secrets, protected data, private infrastructure details, production exports, screenshots with real data, token caches, private keys, kubeconfigs, auth cookies, private hostnames, private account IDs, or internal-only runbooks.
- Public-fit requests are reusable public-safe skill ideas, public documentation navigation, source-backed UCSD/TritonAI workflows, and generic safety rules that do not depend on restricted access.
- Secure-only or private-fit requests include internal/restricted UCSD or TritonAI workflows, private infrastructure assumptions, deployment handoffs, authentication flows, restricted data handling, operational runbooks, private hostnames/accounts, or maintained secure operations. Recommend moving those to UCSD-Skills-Library-Secure or a private tracker without naming sensitive specifics.
- Check whether the issue has enough information to act: requested workflow, intended skill name or area, maintainer/owner if community-scoped, public sources to cite, and expected artifact location (`community/<skill-name>/` or `tritonai/<skill-name>/` when maintainer-approved).
- Do not modify files, labels, assignees, milestones, or issue state. Do not reveal or infer private allowlist membership. Never print a discovered secret.
- Be concise, specific, and constructive.

Required output format:
{ISSUE_MARKER}
## Codex Public Skills Issue Review

**Verdict:** one of `Ready for maintainer triage`, `Needs clarification`, `Likely private/secure`, or `Not a skills-library issue`
**Reviewed issue update:** `{issue.get("updated_at")}`

### Fit
- Public repo fit: pass/fail/inconclusive and why.
- Public boundary safety: pass/fail/inconclusive and why.

### Needed From Reporter
- If nothing else is needed, write `None`.

### Suggested Next Step
- One concise next action for maintainers or the reporter.

Repository guidance excerpts:

{docs}
"""


def repo_doc_excerpt(path: str, limit: int = 7000) -> str:
    target = ROOT / path
    if target.is_dir():
        files = sorted(item for item in target.iterdir() if item.is_file())[:10]
        if not files:
            return f"### {path}\n\n(not present)"
        return "\n\n".join(repo_doc_excerpt(str(item.relative_to(ROOT)), limit=2500) for item in files)
    if not target.exists():
        return f"### {path}\n\n(not present)"
    text = target.read_text(encoding="utf-8", errors="replace")
    return f"### {path}\n\n{truncate(redact_text(text), limit)}"


def normalize_comment(body: str, pull: dict[str, Any], checks: list[CommandResult]) -> str:
    cleaned = redact_text(body.strip())
    if MARKER not in cleaned:
        cleaned = f"{MARKER}\n{cleaned}"
    if "Reviewed commit" not in cleaned:
        cleaned += f"\n\n_Reviewed commit: `{pull['head']['sha']}`_"
    footer = f"\n\n---\n_Automated public-skills Codex review updated {now_iso()}._"
    return truncate_comment(cleaned + footer, checks)


def normalize_issue_comment(body: str, issue: dict[str, Any]) -> str:
    cleaned = redact_text(body.strip())
    if ISSUE_MARKER not in cleaned:
        cleaned = f"{ISSUE_MARKER}\n{cleaned}"
    if "Reviewed issue update" not in cleaned:
        cleaned += f"\n\n_Reviewed issue update: `{issue.get('updated_at')}`_"
    footer = f"\n\n---\n_Automated public-skills Codex issue review updated {now_iso()}._"
    return truncate(cleaned + footer, 60000)


def local_checks_blocked_comment(
    pull: dict[str, Any],
    checks: list[CommandResult],
    failed_checks: list[CommandResult],
) -> str:
    required_fixes = "\n".join(
        f"- Fix `{check.label}` before merge. The failed check output below is authoritative."
        for check in failed_checks
    )
    failed_output = redact_text("\n\n".join(check.markdown(limit=5000) for check in failed_checks))
    body = f"""{MARKER}
## Codex Public Skills Review

**Verdict:** `Blocked`
**Reviewed commit:** `{pull['head']['sha']}`

### Gate Results
- Public repo fit: blocked until failed local checks are resolved.
- Contributor placement: {"requires maintainer verification" if any(check.label == "Contributor placement" for check in failed_checks) else "no public placement action reported"}.
- Leakage/public boundary safety: {"fail" if any(check.label == "High-confidence leak scan" for check in failed_checks) else "pass or not completed by local blocker"}.
- Contributing format: {"fail" if any(check.label == "Public skill format" for check in failed_checks) else "pass or not completed by local blocker"}.

### Required Fixes
{required_fixes}

### Notes
- The Codex model review was skipped because deterministic local checks failed.
- Resolve the failed check output below, then push another PR update for a fresh review comment.

### Failed Local Check Output

{failed_output}

---
_Automated public-skills Codex review updated {now_iso()}._
"""
    return truncate_comment(body, checks)


def failure_comment(pull: dict[str, Any], base_ref: str, head_sha: str, exc: Exception) -> str:
    detail = truncate(redact_text(str(exc)), 6000)
    return f"""{MARKER}
## Codex Public Skills Review

**Verdict:** `Blocked`
**Reviewed commit:** `{head_sha}`

### Gate Results
- Public repo fit: not completed.
- Contributor placement: not completed.
- Leakage/public boundary safety: not completed.
- Contributing format: not completed.

### Required Fixes
- The local public-skills review service failed before it could complete the review. A maintainer should check service logs and rerun the reviewer for this PR.

### Notes
- Base branch: `{base_ref}`
- Error:

```text
{detail}
```

---
_Automated public-skills Codex review updated {now_iso()}._
"""


def failure_issue_comment(issue: dict[str, Any], updated_at: str, exc: Exception) -> str:
    detail = truncate(redact_text(str(exc)), 6000)
    return f"""{ISSUE_MARKER}
## Codex Public Skills Issue Review

**Verdict:** `Needs clarification`
**Reviewed issue update:** `{updated_at}`

### Fit
- Public repo fit: not completed.
- Public boundary safety: not completed.

### Needed From Reporter
- None yet. The local public-skills issue review service failed before it could complete the review.

### Suggested Next Step
- A maintainer should check service logs and rerun the reviewer for this issue.

### Error

```text
{detail}
```

---
_Automated public-skills Codex issue review updated {now_iso()}._
"""


def run_command(label: str, command: list[str], cwd: Path, timeout: int) -> CommandResult:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        env=scrubbed_env(),
    )
    return CommandResult(label, command, result.returncode, result.stdout)


def run_or_raise(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    if result.returncode != 0:
        raise RuntimeError(
            f"{' '.join(redact_command(command))} failed with exit {result.returncode}:\n{redact_text(result.stdout)}"
        )


def verify_signature(raw: bytes, signature_header: str | None, secret: str | None) -> None:
    if not secret:
        raise PermissionError("webhook secret is not configured")
    if not signature_header or not signature_header.startswith("sha256="):
        raise PermissionError("missing X-Hub-Signature-256")
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature_header):
        raise PermissionError("invalid webhook signature")


def parse_repo(value: str) -> tuple[str, str]:
    if not value or "/" not in value:
        raise ValueError(f"invalid repo name: {value!r}")
    owner, repo = value.strip().removesuffix(".git").split("/", 1)
    return owner, repo


def detect_repo(remote: str) -> tuple[str, str]:
    result = subprocess.run(["git", "remote", "get-url", remote], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        raise RuntimeError(f"Could not read git remote {remote}: {result.stdout}")
    url = result.stdout.strip()
    if url.startswith("git@github.com:"):
        return parse_repo(url.removeprefix("git@github.com:"))
    parsed = urllib.parse.urlparse(url)
    return parse_repo(parsed.path.strip("/"))


def fetch_url(remote: str, owner: str, repo: str, token: str | None) -> str:
    if not token:
        return remote
    return f"https://github.com/{owner}/{repo}.git"


def git_env(token: str | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    if token:
        basic = base64.b64encode(f"x-access-token:{token}".encode("utf-8")).decode("ascii")
        env["GIT_CONFIG_COUNT"] = "1"
        env["GIT_CONFIG_KEY_0"] = "http.https://github.com/.extraheader"
        env["GIT_CONFIG_VALUE_0"] = f"AUTHORIZATION: basic {basic}"
    return env


def scrubbed_env() -> dict[str, str]:
    env = {}
    for key, value in os.environ.items():
        if any(marker in key.upper() for marker in SENSITIVE_ENV_MARKERS):
            continue
        env[key] = value
    return env


def redact_command(command: list[str]) -> list[str]:
    return [redact_text(part) for part in command]


def redact_text(text: str) -> str:
    redacted = re.sub(r"https://x-access-token:[^@\s]+@", "https://x-access-token:***@", text)
    redacted = re.sub(
        r"https://(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,})@github\.com",
        "https://***@github.com",
        redacted,
    )
    redacted = re.sub(
        r"https://([^/\s:@]+):(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|[^@\s]{20,})@github\.com",
        r"https://\1:***@github.com",
        redacted,
    )
    redacted = re.sub(
        r"https://[A-Za-z0-9._~!$&+,;=:%_-]+@github\.com",
        "https://***@github.com",
        redacted,
    )
    redacted = re.sub(r"github_pat_[A-Za-z0-9_]{20,}", "github_pat_***", redacted)
    redacted = re.sub(r"gh[pousr]_[A-Za-z0-9]{30,}", "gh*_***", redacted)
    redacted = re.sub(r"AKIA[0-9A-Z]{16}", "AKIA***", redacted)
    redacted = re.sub(r"xox[baprs]-[A-Za-z0-9-]{10,}", "xox*-***", redacted)
    redacted = re.sub(r"-----BEGIN[A-Z ]*PRIVATE KEY-----", "-----BEGIN PRIVATE KEY REDACTED-----", redacted)
    redacted = re.sub(
        r"(?i)([\"']?\b(?:[a-z0-9]+[_-])*(?:api[_-]?key|secret|token|password|passwd|pwd)(?:[_-][a-z0-9]+)*\b[\"']?\s*[:=]\s*([\"']))[^\n\"']{12,}([\"'])",
        r"\1***\3",
        redacted,
    )
    redacted = re.sub(
        r"(?i)([\"']?\b(?:[a-z0-9]+[_-])*(?:api[_-]?key|secret|token|password|passwd|pwd)(?:[_-][a-z0-9]+)*\b[\"']?\s*[:=]\s*)[A-Za-z0-9_./+=:@-]{12,}",
        r"\1***",
        redacted,
    )
    return redacted


def load_state(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            state = json.load(handle)
    except FileNotFoundError:
        return {"pulls": {}}
    except json.JSONDecodeError:
        return {"pulls": {}}
    return state if isinstance(state, dict) else {"pulls": {}}


def save_state(path: Path, state: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def truncate_comment(body: str, checks: list[CommandResult]) -> str:
    if len(body) <= 60000:
        return body
    summary = "\n".join(f"- {check.label}: {'PASS' if check.ok else 'FAIL'}" for check in checks)
    return truncate(body, 56000) + f"\n\n### Local Check Summary\n{summary}\n\n_Comment truncated by the public-skills review service._"


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 80)].rstrip() + "\n... [truncated by public_pr_review_service.py]"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


if __name__ == "__main__":
    raise SystemExit(main())
