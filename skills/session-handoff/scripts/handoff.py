#!/usr/bin/env python3
"""Portable OpenCode V2 session transfers retained until restored or explicitly removed."""

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
import uuid


ROOT = Path(__file__).resolve().parents[3]
ID_PATTERN = re.compile(r"\d{8}T\d{6}Z-[a-f0-9]{32}")


class HandoffError(Exception):
    pass


class APIError(HandoffError):
    def __init__(self, tag):
        self.tag = tag
        super().__init__(f"OpenCode API 오류: {tag}")


def command(*args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        # Do not echo API payloads, authentication, or transcripts in errors.
        raise HandoffError(f"명령 실패: {args[0]} {args[1] if len(args) > 1 else ''}")
    return result.stdout.strip()


def api(method, path):
    if "/export" in path:
        # 2.0.18 CLI output can also be truncated for large response bodies.
        return service_request(method, path)
    result = subprocess.run(
        ["opencode", "api", method, path], capture_output=True, text=True
    )
    try:
        response = json.loads(result.stdout) if result.stdout.strip() else None
    except ValueError as exc:
        raise HandoffError("OpenCode API 응답을 해석하지 못했습니다.") from exc
    if result.returncode:
        tag = response.get("_tag", "RequestFailed") if isinstance(response, dict) else "RequestFailed"
        raise APIError(tag)
    return response


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def service_request(method, path, payload=None):
    """Transfer large requests/responses without CLI argv/output size limits.

    Match the CLI's actual service before using the registration credentials.
    Authentication matches @opencode/client 2.0.18 Service.headers().
    """
    current = api("get", "/api/info")
    state = Path(command("opencode", "debug", "paths", "state"))
    registration = json.loads((state / "service.json").read_text(encoding="utf-8"))
    url = registration["url"].rstrip("/")
    parsed = urlsplit(url)
    if (
        registration.get("pid") != current.get("pid")
        or url not in [u.rstrip("/") for u in current.get("urls", [])]
        or parsed.scheme != "http"
        or parsed.hostname not in ("127.0.0.1", "localhost", "::1")
        or parsed.username is not None
        or parsed.query
        or parsed.fragment
    ):
        raise HandoffError("현재 연결과 로컬 서비스가 일치하지 않습니다. 보관·복원은 관리형 로컬 서비스에서 실행해 주세요.")
    headers = {"Content-Type": "application/json"}
    if "password" in registration:
        token = base64.b64encode(("opencode:" + registration["password"]).encode()).decode()
        headers["Authorization"] = "Basic " + token
    request = Request(
        url + path,
        data=json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None,
        headers=headers,
        method=method.upper(),
    )
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=180) as response:
            return json.load(response)
    except HTTPError as exc:
        status = exc.code
        exc.close()
        raise HandoffError(f"세션 전송 실패: HTTP {status}. 백업을 유지합니다.") from None


def import_session(payload):
    return service_request("post", "/api/experimental/session/import", payload)["data"]


def now():
    return datetime.now(timezone.utc)


def stamp(value):
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_time(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise HandoffError("보관 시각에 시간대가 없습니다.")
    return result


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def write_json(path, value):
    # Exclusive creation prevents silently replacing another transfer.
    with path.open("xb") as file:
        file.write(json_bytes(value))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def store_at(root):
    store = root / "handoff"
    if store.is_symlink():
        raise HandoffError("handoff 폴더가 심볼릭 링크입니다.")
    return store


def entry_at(root, entry_id):
    if not ID_PATTERN.fullmatch(entry_id):
        raise HandoffError("올바르지 않은 보관 항목 ID입니다.")
    entry = store_at(root) / entry_id
    if entry.is_symlink():
        raise HandoffError("보관 항목이 심볼릭 링크입니다.")
    return entry


def read_entry(root, entry_id):
    entry = entry_at(root, entry_id)
    if {p.name for p in entry.iterdir()} != {"metadata.json", "session.json"}:
        raise HandoffError(f"보관 항목에 누락되거나 알 수 없는 파일이 있습니다: {entry_id}")
    if any(p.is_symlink() or not p.is_file() for p in entry.iterdir()):
        raise HandoffError("보관 파일이 일반 파일이 아닙니다.")
    metadata = json.loads((entry / "metadata.json").read_text(encoding="utf-8"))
    raw = (entry / "session.json").read_bytes()
    data = json.loads(raw)
    if metadata.get("formatVersion") != 1 or metadata.get("id") != entry_id:
        raise HandoffError("지원하지 않거나 일치하지 않는 보관 메타데이터입니다.")
    if digest(raw) != metadata.get("sha256"):
        raise HandoffError("세션 파일의 검증값이 일치하지 않습니다. 백업을 유지합니다.")
    if not isinstance(data.get("info"), dict) or not isinstance(data.get("messages"), list):
        raise HandoffError("세션 데이터 형식이 올바르지 않습니다.")
    if data["info"].get("id") != metadata.get("sourceSessionID"):
        raise HandoffError("원본 세션 ID가 일치하지 않습니다.")
    parse_time(metadata["createdAt"])
    # Legacy expiry timestamps never authorize deleting an unrestored backup.
    return metadata, data


def export(root, session_id, title=None, project=None):
    if not re.fullmatch(r"ses[a-zA-Z0-9_-]+", session_id):
        raise HandoffError("올바르지 않은 세션 ID입니다.")
    data = api("get", f"/api/experimental/session/{session_id}/export?sanitize=false")["data"]
    created = now()
    entry_id = created.strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex
    entry = entry_at(root, entry_id)
    raw = json_bytes(data)
    directory = data["info"]["location"]["directory"]
    metadata = {
        "formatVersion": 1,
        "id": entry_id,
        "title": title or data["info"].get("title") or "제목 없는 대화",
        "createdAt": stamp(created),
        "expiresAt": None,
        "opencodeVersion": api("get", "/api/info")["version"],
        "sourceSessionID": session_id,
        "project": {"name": project or Path(directory).name, "sourceDirectory": directory},
        "messageCount": len(data["messages"]),
        "sha256": digest(raw),
    }
    entry.mkdir(parents=True, exist_ok=False)
    try:
        write_json(entry / "session.json", data)
        write_json(entry / "metadata.json", metadata)
    except Exception:
        for name in ("session.json", "metadata.json"):
            (entry / name).unlink(missing_ok=True)
        entry.rmdir()
        raise
    return {"status": "saved_locally", **metadata}


def entries(root):
    store = store_at(root)
    if not store.exists():
        return []
    result = []
    for entry in sorted(store.iterdir()):
        if not ID_PATTERN.fullmatch(entry.name):
            continue
        metadata, _ = read_entry(root, entry.name)
        result.append({**metadata, "expiresAt": None, "expired": False})
    return result


def listed(session_id, directory, title):
    query = {"directory": directory, "search": title, "limit": "100"}
    while True:
        response = api("get", "/api/session?" + urlencode(query))
        if any(item["id"] == session_id for item in response["data"]):
            return True
        cursor = response.get("cursor", {}).get("next")
        if not cursor:
            return False
        query["cursor"] = cursor


def restore(root, entry_id, directory):
    metadata, data = read_entry(root, entry_id)
    target = Path(directory).expanduser().resolve(strict=True)
    if not target.is_dir():
        raise HandoffError("복원할 프로젝트 경로가 폴더가 아닙니다.")
    target_id = "ses_handoff_" + digest(entry_id.encode())[:32]
    marker = {"id": entry_id, "sha256": metadata["sha256"]}
    # Message IDs are globally unique in OpenCode's database, not session-local.
    # Namespace only actual message identities/references, never transcript text.
    message_ids = {
        message["id"]: "msg_" + digest((entry_id + ":" + message["id"]).encode())[:32]
        for message in data["messages"]
    }
    for message in data["messages"]:
        message["id"] = message_ids[message["id"]]
    if "revert" in data["info"]:
        data["info"]["revert"]["messageID"] = message_ids[data["info"]["revert"]["messageID"]]
    try:
        existing = api("get", "/api/session/" + target_id)["data"]
    except APIError as exc:
        if exc.tag != "SessionNotFoundError":
            raise
        existing = None
    if existing:
        if existing.get("metadata", {}).get("sessionHandoff") != marker:
            raise HandoffError("복원 대상 세션 ID가 다른 세션과 충돌합니다. 덮어쓰지 않습니다.")
        if existing["location"]["directory"] != str(target):
            raise HandoffError("이미 다른 경로에 복원된 항목입니다. 기존 세션을 이동하거나 덮어쓰지 않습니다.")
    else:
        info = data["info"]
        # Imported transfers are independent root sessions, including fork exports.
        for field in ("parentID", "fork", "subpath"):
            info.pop(field, None)
        info["id"] = target_id
        info["title"] = metadata["title"]
        info["metadata"] = {**info.get("metadata", {}), "sessionHandoff": marker}
        info["time"].pop("archived", None)
        info["time"]["updated"] = int(now().timestamp() * 1000)
        imported = import_session({**data, "location": {"directory": str(target)}})
        if imported["id"] != target_id:
            raise HandoffError("가져온 세션 ID가 예상과 다릅니다. 백업을 유지합니다.")
    restored = api("get", f"/api/experimental/session/{target_id}/export?sanitize=false")["data"]
    # Additional messages are allowed after a successful earlier restore.
    if restored["messages"][:len(data["messages"])] != data["messages"]:
        raise HandoffError("복원한 대화 내용이 원본과 일치하지 않습니다. 백업을 유지합니다.")
    if restored["info"]["location"]["directory"] != str(target):
        raise HandoffError("복원한 작업 위치가 일치하지 않습니다. 백업을 유지합니다.")
    if not listed(target_id, str(target), restored["info"].get("title", "")):
        raise HandoffError("일반 세션 목록에서 복원된 세션을 확인하지 못했습니다. 백업을 유지합니다.")
    return {
        "status": "already_restored" if existing else "restored",
        "id": entry_id,
        "sessionID": target_id,
        "title": restored["info"].get("title"),
        "directory": str(target),
        "verified": True,
        "backupRetained": True,
    }


def remove(root, entry_id):
    # Only delete a validated bundle; never recursively remove unknown files.
    read_entry(root, entry_id)
    entry = entry_at(root, entry_id)
    (entry / "session.json").unlink()
    (entry / "metadata.json").unlink()
    entry.rmdir()
    return entry_id


def cleanup(root, exclude=()):
    # Keep the old command compatible, but never delete backups based on age.
    return {"removed": [], "retained": len(entries(root))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="환경 저장소 루트 (기본: 스킬의 저장소)")
    actions = parser.add_subparsers(dest="action", required=True)
    save = actions.add_parser("export", help="현재 세션을 로컬 보관; Git 전송은 스킬이 수행")
    save.add_argument("session_id")
    save.add_argument("--title")
    save.add_argument("--project")
    actions.add_parser("list")
    load = actions.add_parser("restore")
    load.add_argument("id")
    load.add_argument("--directory", required=True)
    delete = actions.add_parser("remove")
    delete.add_argument("id")
    clean = actions.add_parser("cleanup")
    clean.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()
    try:
        root = args.root.expanduser().resolve(strict=True)
        if args.action == "export":
            result = export(root, args.session_id, args.title, args.project)
        elif args.action == "list":
            result = entries(root)
        elif args.action == "restore":
            result = restore(root, args.id, args.directory)
        elif args.action == "remove":
            result = {"removed": [remove(root, args.id)]}
        else:
            result = cleanup(root, args.exclude)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (HandoffError, OSError, ValueError, KeyError, TypeError) as exc:
        # External errors may contain credentials or server responses.
        message = str(exc) if isinstance(exc, HandoffError) else f"처리 실패 ({type(exc).__name__}). 파일과 연결 상태를 확인해 주세요."
        print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
