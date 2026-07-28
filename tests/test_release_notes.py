from __future__ import annotations

import pytest

from scripts.extract_release_notes import extract_release_notes


def test_extract_release_notes_returns_korean_two_part_body() -> None:
    changelog = """
# 변경 기록

## [미출시]

### 1. 서비스 사용자용 변경 사항
- 다음 변경

### 2. 개발자용 업데이트 로그
- 다음 구현

## [0.2.0] - 2026-07-28

### 1. 서비스 사용자용 변경 사항
- 파일을 분석할 수 있습니다.

### 2. 개발자용 업데이트 로그
- 첨부 처리기를 추가했습니다.

## [0.1.0] - 2026-07-01

### 1. 서비스 사용자용 변경 사항
- 첫 버전

### 2. 개발자용 업데이트 로그
- 초기화
"""

    notes = extract_release_notes(changelog, "v0.2.0")

    assert "파일을 분석할 수 있습니다." in notes
    assert "첨부 처리기를 추가했습니다." in notes
    assert "첫 버전" not in notes


def test_extract_release_notes_rejects_missing_audience_section() -> None:
    changelog = "## [0.2.0] - 2026-07-28\n\n### 1. 서비스 사용자용 변경 사항\n- 기능"

    with pytest.raises(ValueError, match="두 단"):
        extract_release_notes(changelog, "v0.2.0")


def test_extract_release_notes_rejects_invalid_tag() -> None:
    with pytest.raises(ValueError, match="SemVer"):
        extract_release_notes("", "release-latest")
