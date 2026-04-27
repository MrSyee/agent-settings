#!/usr/bin/env python3
"""Confluence CLI - Wiki 페이지 CRUD 헬퍼 스크립트.

Usage:
    python confluence_cli.py <command> --base-url URL --token TOKEN [options]

Commands:
    get-page, search, list-pages, create-page, update-page, mark-deleted,
    list-spaces, get-space, attach-file, list-attachments, get-children
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any


def _ensure_atlassian() -> None:
    """atlassian-python-api가 없으면 자동 설치한다."""
    try:
        import atlassian  # noqa: F401
    except ImportError:
        import subprocess
        print("atlassian-python-api 설치 중...", file=sys.stderr)
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "atlassian-python-api",
             "-q", "--break-system-packages"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            # --break-system-packages 없이 재시도 (venv 등 환경)
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "atlassian-python-api", "-q"],
                check=True,
            )


def _make_client(args: argparse.Namespace):
    """atlassian-python-api Confluence 클라이언트를 생성한다."""
    _ensure_atlassian()
    from atlassian import Confluence

    # --no-verify-ssl 플래그 또는 CONFLUENCE_NO_VERIFY_SSL 환경변수
    no_verify = getattr(args, "no_verify_ssl", False) or (
        os.environ.get("CONFLUENCE_NO_VERIFY_SSL", "").lower() in ("1", "true", "yes")
    )
    kwargs: dict[str, Any] = {"url": args.base_url, "verify_ssl": not no_verify}

    if getattr(args, "token", None):
        kwargs["token"] = args.token
    elif getattr(args, "username", None) and getattr(args, "password", None):
        kwargs["username"] = args.username
        kwargs["password"] = args.password
    else:
        print("ERROR: --token 또는 --username/--password 인증 정보가 필요합니다.", file=sys.stderr)
        sys.exit(1)

    return Confluence(**kwargs)


def _print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


# ── Commands ──────────────────────────────────────────────────────────────────


def cmd_get_page(args: argparse.Namespace) -> None:
    """페이지 ID로 조회."""
    client = _make_client(args)
    expand = args.expand or "body.storage,version,ancestors,space"
    page = client.get_page_by_id(args.page_id, expand=expand)
    result = {
        "id": page.get("id"),
        "title": page.get("title"),
        "space_key": page.get("space", {}).get("key"),
        "version": page.get("version", {}).get("number"),
        "url": _build_url(args.base_url, page),
        "updated_by": (page.get("version", {}).get("by") or {}).get("displayName"),
        "body": page.get("body", {}).get("storage", {}).get("value", ""),
        "ancestors": [
            {"id": a.get("id"), "title": a.get("title")}
            for a in (page.get("ancestors") or [])
        ],
    }
    _print_json(result)


def cmd_search(args: argparse.Namespace) -> None:
    """CQL 기반 검색."""
    client = _make_client(args)
    cql_parts: list[str] = []

    if args.space_key:
        cql_parts.append(f'space="{args.space_key}"')
    if args.query:
        cql_parts.append(f'(title~"{args.query}" OR text~"{args.query}")')

    cql = " AND ".join(cql_parts) if cql_parts else 'type="page"'
    limit = args.limit or 20

    results = client.cql(cql, limit=limit, expand="version,space")
    pages = []
    for item in results.get("results", []):
        content = item.get("content") or item
        pages.append({
            "id": content.get("id"),
            "title": content.get("title"),
            "space_key": content.get("space", {}).get("key"),
            "url": _build_url(args.base_url, content),
            "excerpt": item.get("excerpt", ""),
        })
    _print_json({"total": results.get("totalSize", len(pages)), "pages": pages})


def cmd_list_pages(args: argparse.Namespace) -> None:
    """스페이스 내 페이지 목록."""
    client = _make_client(args)
    limit = args.limit or 50
    start = args.start or 0
    pages_raw = client.get_all_pages_from_space(
        space=args.space_key,
        start=start,
        limit=limit,
        expand="version",
        status="current",
    )
    pages = [
        {
            "id": p.get("id"),
            "title": p.get("title"),
            "version": p.get("version", {}).get("number"),
            "url": _build_url(args.base_url, p),
        }
        for p in pages_raw
    ]
    _print_json({"count": len(pages), "pages": pages})


def cmd_create_page(args: argparse.Namespace) -> None:
    """새 페이지 생성."""
    client = _make_client(args)
    body = _read_body(args)

    kwargs: dict[str, Any] = {
        "space": args.space_key,
        "title": args.title,
        "body": body,
        "type": "page",
        "representation": "storage",
    }
    if args.parent_id:
        kwargs["parent_id"] = args.parent_id

    result = client.create_page(**kwargs)
    _print_json({
        "status": "created",
        "id": result.get("id"),
        "title": result.get("title"),
        "url": _build_url(args.base_url, result),
    })


def cmd_update_page(args: argparse.Namespace) -> None:
    """기존 페이지 수정."""
    client = _make_client(args)
    body = _read_body(args)

    current = client.get_page_by_id(args.page_id, expand="version")
    current_title = current.get("title", "")
    title = args.title or current_title

    result = client.update_page(
        page_id=args.page_id,
        title=title,
        body=body,
        type="page",
        representation="storage",
    )
    _print_json({
        "status": "updated",
        "id": result.get("id"),
        "title": result.get("title"),
        "version": result.get("version", {}).get("number"),
        "url": _build_url(args.base_url, result),
    })


def cmd_mark_deleted(args: argparse.Namespace) -> None:
    """페이지 제목에 (삭제) 접두어를 붙여 소프트 삭제 표시한다. 실제 삭제는 수행하지 않는다."""
    client = _make_client(args)
    current = client.get_page_by_id(args.page_id, expand="version,body.storage")
    current_title = current.get("title", "")

    if current_title.startswith("(삭제)"):
        _print_json({
            "status": "already_marked",
            "message": f"이미 삭제 표시된 페이지입니다: {current_title}",
            "id": args.page_id,
            "title": current_title,
            "url": _build_url(args.base_url, current),
        })
        return

    new_title = f"(삭제){current_title}"
    body = current.get("body", {}).get("storage", {}).get("value", "")

    result = client.update_page(
        page_id=args.page_id,
        title=new_title,
        body=body,
        type="page",
        representation="storage",
    )
    _print_json({
        "status": "marked_deleted",
        "message": f"페이지가 삭제 표시되었습니다 (실제 삭제 아님). 제목: {current_title} → {new_title}",
        "id": result.get("id"),
        "title": result.get("title"),
        "previous_title": current_title,
        "version": result.get("version", {}).get("number"),
        "url": _build_url(args.base_url, result),
    })


def cmd_list_spaces(args: argparse.Namespace) -> None:
    """스페이스 목록 조회."""
    client = _make_client(args)
    limit = args.limit or 50
    spaces_raw = client.get_all_spaces(start=0, limit=limit, expand="description.plain")
    spaces = [
        {
            "key": s.get("key"),
            "name": s.get("name"),
            "type": s.get("type"),
            "description": s.get("description", {}).get("plain", {}).get("value", ""),
        }
        for s in spaces_raw.get("results", [])
    ]
    _print_json({"count": len(spaces), "spaces": spaces})


def cmd_get_space(args: argparse.Namespace) -> None:
    """특정 스페이스 정보 조회."""
    client = _make_client(args)
    space = client.get_space(args.space_key, expand="description.plain,homepage")
    _print_json({
        "key": space.get("key"),
        "name": space.get("name"),
        "type": space.get("type"),
        "description": space.get("description", {}).get("plain", {}).get("value", ""),
        "homepage_id": (space.get("homepage") or {}).get("id"),
        "homepage_title": (space.get("homepage") or {}).get("title"),
    })


def cmd_attach_file(args: argparse.Namespace) -> None:
    """페이지에 파일 첨부."""
    client = _make_client(args)
    result = client.attach_file(
        filename=args.file_path,
        page_id=args.page_id,
        comment=args.comment or "",
    )
    # attach_file 반환값은 dict 또는 list
    if isinstance(result, dict):
        results_list = result.get("results", [result])
    elif isinstance(result, list):
        results_list = result
    else:
        results_list = [result]

    attachments = [
        {
            "id": a.get("id"),
            "title": a.get("title"),
            "file_size": a.get("extensions", {}).get("fileSize"),
            "media_type": a.get("extensions", {}).get("mediaType"),
        }
        for a in results_list
    ]
    _print_json({"status": "attached", "attachments": attachments})


def cmd_list_attachments(args: argparse.Namespace) -> None:
    """페이지 첨부 파일 목록."""
    client = _make_client(args)
    limit = args.limit or 50
    attachments_raw = client.get_attachments_from_content(
        page_id=args.page_id, start=0, limit=limit,
    )
    attachments = [
        {
            "id": a.get("id"),
            "title": a.get("title"),
            "file_size": a.get("extensions", {}).get("fileSize"),
            "media_type": a.get("extensions", {}).get("mediaType"),
            "download_link": a.get("_links", {}).get("download"),
        }
        for a in attachments_raw.get("results", [])
    ]
    _print_json({"count": len(attachments), "attachments": attachments})


def cmd_get_children(args: argparse.Namespace) -> None:
    """자식 페이지 목록 조회."""
    client = _make_client(args)
    limit = args.limit or 50
    children = client.get_page_child_by_type(
        page_id=args.page_id, type="page", start=0, limit=limit, expand="version",
    )
    pages = [
        {
            "id": c.get("id"),
            "title": c.get("title"),
            "version": c.get("version", {}).get("number"),
            "url": _build_url(args.base_url, c),
        }
        for c in children
    ]
    _print_json({"count": len(pages), "children": pages})


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_url(base_url: str, page: dict[str, Any]) -> str | None:
    from urllib.parse import urljoin

    links = page.get("_links", {}) or {}
    webui = links.get("webui")
    if not webui:
        return None
    return urljoin(base_url.rstrip("/") + "/", webui.lstrip("/"))


def _read_body(args: argparse.Namespace) -> str:
    """--body 또는 --body-file에서 본문을 읽는다."""
    if getattr(args, "body", None):
        return args.body
    if getattr(args, "body_file", None):
        with open(args.body_file, encoding="utf-8") as f:
            return f.read()
    print("ERROR: --body 또는 --body-file 중 하나가 필요합니다.", file=sys.stderr)
    sys.exit(1)


# ── CLI Parser ────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Confluence CLI - Wiki 페이지 CRUD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 공통 인증 인자 (환경변수 우선, CLI 인자로 override 가능)
    auth = parser.add_argument_group("authentication")
    auth.add_argument(
        "--base-url",
        default=os.environ.get("CONFLUENCE_BASE_URL"),
        required=not os.environ.get("CONFLUENCE_BASE_URL"),
        help="Confluence base URL (또는 CONFLUENCE_BASE_URL 환경변수)",
    )
    auth.add_argument(
        "--token",
        default=os.environ.get("CONFLUENCE_TOKEN") or None,
        help="Personal Access Token (또는 CONFLUENCE_TOKEN 환경변수)",
    )
    auth.add_argument("--username", default=os.environ.get("CONFLUENCE_USERNAME"), help="Username (basic auth)")
    auth.add_argument("--password", default=os.environ.get("CONFLUENCE_PASSWORD"), help="Password (basic auth)")
    auth.add_argument("--no-verify-ssl", action="store_true", help="SSL 검증 비활성화 (또는 CONFLUENCE_NO_VERIFY_SSL=true)")

    sub = parser.add_subparsers(dest="command", required=True)

    # get-page
    p = sub.add_parser("get-page", help="페이지 ID로 조회")
    p.add_argument("--page-id", required=True)
    p.add_argument("--expand", help="커스텀 expand 필드")

    # search
    p = sub.add_parser("search", help="CQL 기반 검색")
    p.add_argument("--space-key", help="스페이스 키")
    p.add_argument("--query", help="검색어")
    p.add_argument("--limit", type=int, default=20)

    # list-pages
    p = sub.add_parser("list-pages", help="스페이스 내 페이지 목록")
    p.add_argument("--space-key", required=True)
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--start", type=int, default=0)

    # create-page
    p = sub.add_parser("create-page", help="새 페이지 생성")
    p.add_argument("--space-key", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--body", help="HTML/Storage Format 본문 (인라인)")
    p.add_argument("--body-file", help="본문 파일 경로")
    p.add_argument("--parent-id", help="부모 페이지 ID")

    # update-page
    p = sub.add_parser("update-page", help="기존 페이지 수정")
    p.add_argument("--page-id", required=True)
    p.add_argument("--title", help="새 제목 (미지정 시 기존 유지)")
    p.add_argument("--body", help="HTML/Storage Format 본문 (인라인)")
    p.add_argument("--body-file", help="본문 파일 경로")

    # mark-deleted (소프트 삭제: 제목에 (삭제) 접두어 추가)
    p = sub.add_parser("mark-deleted", help="페이지 제목에 (삭제) 표시 (실제 삭제 아님)")
    p.add_argument("--page-id", required=True)

    # list-spaces
    p = sub.add_parser("list-spaces", help="스페이스 목록 조회")
    p.add_argument("--limit", type=int, default=50)

    # get-space
    p = sub.add_parser("get-space", help="특정 스페이스 정보 조회")
    p.add_argument("--space-key", required=True)

    # attach-file
    p = sub.add_parser("attach-file", help="페이지에 파일 첨부")
    p.add_argument("--page-id", required=True)
    p.add_argument("--file-path", required=True)
    p.add_argument("--comment", help="첨부 파일 코멘트")

    # list-attachments
    p = sub.add_parser("list-attachments", help="페이지 첨부 파일 목록")
    p.add_argument("--page-id", required=True)
    p.add_argument("--limit", type=int, default=50)

    # get-children
    p = sub.add_parser("get-children", help="자식 페이지 목록 조회")
    p.add_argument("--page-id", required=True)
    p.add_argument("--limit", type=int, default=50)

    return parser


COMMANDS = {
    "get-page": cmd_get_page,
    "search": cmd_search,
    "list-pages": cmd_list_pages,
    "create-page": cmd_create_page,
    "update-page": cmd_update_page,
    "mark-deleted": cmd_mark_deleted,
    "list-spaces": cmd_list_spaces,
    "get-space": cmd_get_space,
    "attach-file": cmd_attach_file,
    "list-attachments": cmd_list_attachments,
    "get-children": cmd_get_children,
}


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    handler = COMMANDS.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)
    handler(args)


if __name__ == "__main__":
    main()
