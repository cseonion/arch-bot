from __future__ import annotations

import tomllib
from pathlib import Path

from arch_bot import __version__
from arch_bot.profiles import AgentRegistry

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_user_readme_keeps_required_sections() -> None:
    user_readme = read("README.md")

    assert "## 1. 개요 및 소개" in user_readme
    assert "## 2. 채널별 역할 및 기능 소개" in user_readme


def test_developer_readme_keeps_required_sections() -> None:
    developer_readme = read("README_dev.md")

    assert "## 1. 환경 세팅 방법" in developer_readme
    assert "## 2. 채널별 역할 및 기능에 따른 저장소 구조" in developer_readme
    assert "## 3. 채널별 Tool/MCP/Skill 기본 설명" in developer_readme


def test_unreleased_changelog_has_two_audiences() -> None:
    changelog = read("CHANGELOG.md")
    unreleased = changelog.split("## [미출시]", maxsplit=1)[1]

    assert "### 1. 서비스 사용자용 변경 사항" in unreleased
    assert "### 2. 개발자용 업데이트 로그" in unreleased


def test_application_version_matches_project_version() -> None:
    with (ROOT / "pyproject.toml").open("rb") as file:
        project = tomllib.load(file)

    assert project["project"]["version"] == __version__


def test_all_repository_capability_references_resolve() -> None:
    registry = AgentRegistry.load(ROOT / "config/agents")

    assert {profile.agent_id for profile in registry.profiles} == {
        "default",
        "task1",
        "task2",
    }
