# 채널 및 에이전트 규칙

## 현재 채널 계약

- `default`: 일반 채널의 `/ask` 텍스트 질의
- `task1`: 전용 채널의 일반 메시지와 이미지·PDF·문서·CAD 기초 처리
- `task2`: 독립 텍스트 대화만 구성되어 있으며 업무 역할은 추후 정의

## 변경 체크리스트

채널 역할이나 기능을 바꿀 때 다음을 함께 점검한다.

- `config/agents/<id>/profile.toml`
- `config/agents/<id>/system.md`
- 관련 `config/skills`, `config/tools`, `config/mcp`
- `src/arch_bot`의 라우팅과 실행 어댑터
- 채널 격리, 권한, 성공·실패 흐름 테스트
- `README.md`, `README_dev.md`, `CHANGELOG.md`
- 이 문서의 현재 채널 계약

## Capability 표현

- Skill은 현재 시스템 프롬프트에 결합되는 지침 모듈이다.
- Tool은 코드 구현, 런타임 등록과 프로필 할당이 모두 있어야 실행 가능하다.
- MCP는 서버 연결, 인증, Tool 노출과 승인 정책이 있어야 실행 가능하다.
- `profile.toml`에 이름만 선언된 기능은 실행 가능하다고 표현하지 않는다.

## Task1 첨부 계약

- 이미지 PNG/JPEG/WEBP는 시각 입력으로 처리한다.
- PDF는 텍스트와 페이지 이미지를 처리한다.
- 지원 문서·표 파일은 OpenAI `input_file`로 처리한다.
- ASCII DXF와 IFC는 제한된 구조적 메타데이터만 요약한다.
- DWG, DGN, RVT는 현재 원본 내용을 분석하지 않고 변환을 안내한다.
- PDF가 아닌 문서의 내장 이미지·차트는 분석된다고 보장하지 않는다.
- 파일만 있는 메시지도 처리하며, 모든 파일이 거절되면 모델을 호출하지 않는다.
