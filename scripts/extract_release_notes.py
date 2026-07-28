from __future__ import annotations

import re
import sys
from pathlib import Path

USER_HEADING = "### 1. 서비스 사용자용 변경 사항"
DEVELOPER_HEADING = "### 2. 개발자용 업데이트 로그"


def extract_release_notes(changelog: str, tag: str) -> str:
    version = tag.removeprefix("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"유효하지 않은 SemVer 태그입니다: {tag}")

    pattern = re.compile(
        rf"^## \[{re.escape(version)}\][^\n]*\n(?P<body>.*?)(?=^## \[|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(changelog)
    if not match:
        raise ValueError(f"CHANGELOG.md에서 [{version}] 섹션을 찾지 못했습니다.")

    body = match.group("body").strip()
    if USER_HEADING not in body or DEVELOPER_HEADING not in body:
        raise ValueError("릴리스 섹션에 사용자용과 개발자용 두 단이 모두 필요합니다.")
    return body + "\n"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "사용법: python scripts/extract_release_notes.py vX.Y.Z <출력파일>"
        )

    tag = sys.argv[1]
    output_path = Path(sys.argv[2])
    try:
        notes = extract_release_notes(
            Path("CHANGELOG.md").read_text(encoding="utf-8"),
            tag,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    output_path.write_text(notes, encoding="utf-8")


if __name__ == "__main__":
    main()
