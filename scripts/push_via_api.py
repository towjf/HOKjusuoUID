"""在 `git push` 被网络阻断时，用 GitHub Git Data API 把本地提交同步到远端。

适用场景：本机访问 github.com:443 超时 / 代理 CONNECT aborted，但 api.github.com 可达。
做法：把本地每个提交的树逐个重建成 blob → tree → commit，最后让 refs/heads/main
指向最新的那个提交。远端提交的 SHA 会重新生成（内容一致），因此是「整支重写」，
多人协作的仓库不要用这个脚本。

认证：复用本机 git 凭据（Git Credential Manager），不读、不打印 token 内容。

用法：
    python scripts/push_via_api.py                 # 推 main
    python scripts/push_via_api.py --branch main
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = "towjf/HOKjusuoUID"


def get_token() -> str:
    proc = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    for line in proc.stdout.splitlines():
        if line.startswith("password="):
            return line[len("password=") :]
    raise SystemExit("未取到 GitHub 凭据，请先执行一次 git 登录（或 gh auth login）")


def api(path: str, token: str, method: str = "GET", payload: dict | None = None, tries: int = 4):
    data = json.dumps(payload).encode() if payload is not None else None
    last = ""
    for attempt in range(1, tries + 1):
        req = urllib.request.Request(f"{API}{path}", data=data, method=method)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "HOKjusuoUID-pusher")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if data:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                body = resp.read().decode()
                return json.loads(body) if body.strip() else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode()[:300]
            if exc.code >= 500 and attempt < tries:
                last = f"HTTP {exc.code}"
                time.sleep(1.5 * attempt)
                continue
            raise SystemExit(f"{method} {path} -> HTTP {exc.code}: {detail}")
        except Exception as exc:  # noqa: BLE001  代理抖动
            last = f"{type(exc).__name__}: {exc}"
            if attempt < tries:
                time.sleep(1.5 * attempt)
                continue
            raise SystemExit(f"{method} {path} 连续 {tries} 次失败: {last}")
    raise SystemExit(f"{method} {path} 失败: {last}")


def git(*args: str, binary: bool = False):
    proc = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} 失败: {proc.stderr.decode('utf-8', 'replace')}")
    return proc.stdout if binary else proc.stdout.decode("utf-8", "replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=DEFAULT_REPO, help="owner/name")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--ref-plugin", default=str(ROOT / "HOKjusuoUID" / "version.py"))
    args = parser.parse_args()

    version = "?"
    for line in Path(args.ref_plugin).read_text(encoding="utf-8").splitlines():
        if line.startswith("__version__"):
            version = line.split('"')[1]
            break

    token = get_token()
    commits = git("rev-list", "--reverse", "HEAD").split()
    print(f"目标仓库 {args.repo} -> {args.branch}，本地 {len(commits)} 个提交，插件版本 v{version}")

    ref_path = f"/repos/{args.repo}/git/refs/heads/{args.branch}"
    try:
        api(ref_path, token)
    except SystemExit:
        # 空仓库不允许建 blob，先塞一个占位提交
        api(
            f"/repos/{args.repo}/contents/.push-init",
            token,
            method="PUT",
            payload={
                "message": "chore: 初始化仓库",
                "content": base64.b64encode(b"init\n").decode(),
            },
        )
        print("空仓库已初始化")

    blob_cache: dict[str, str] = {}
    parent: str | None = None
    for index, commit in enumerate(commits, 1):
        message = git("log", "-1", "--pretty=%B", commit).strip()
        items = []
        for line in git("ls-tree", "-r", commit).splitlines():
            meta, path = line.split("\t", 1)
            mode, kind, sha = meta.split()
            if kind != "blob":
                continue
            if sha not in blob_cache:
                content = git("cat-file", "blob", sha, binary=True)
                blob = api(
                    f"/repos/{args.repo}/git/blobs",
                    token,
                    method="POST",
                    payload={
                        "content": base64.b64encode(content).decode(),
                        "encoding": "base64",
                    },
                )
                blob_cache[sha] = blob["sha"]
            items.append({"path": path, "mode": mode, "type": "blob", "sha": blob_cache[sha]})

        tree = api(
            f"/repos/{args.repo}/git/trees",
            token,
            method="POST",
            payload={"tree": items},
        )
        payload = {"message": message, "tree": tree["sha"]}
        if parent:
            payload["parents"] = [parent]
        new_commit = api(
            f"/repos/{args.repo}/git/commits", token, method="POST", payload=payload
        )
        parent = new_commit["sha"]
        print(f"  [{index}/{len(commits)}] {message.splitlines()[0][:56]} -> {parent[:8]}")

    api(ref_path, token, method="PATCH", payload={"sha": parent, "force": True})
    tree = api(f"/repos/{args.repo}/git/trees/{args.branch}?recursive=1", token)
    files = [item["path"] for item in tree["tree"] if item["type"] == "blob"]
    print(f"完成：{args.branch} 指向 {parent[:8]}，远端 {len(files)} 个文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
