# Codex 장기 작업 규칙

이 폴더는 저장소를 수정하는 Codex를 위한 현재 유효한 정본입니다. Discord에서
작동하는 런타임 에이전트의 프롬프트인 `config/agents/*`와 혼합하지 않습니다.

## 읽기 순서

1. 루트 `AGENTS.md`
2. `project-rules.md`
3. 변경 범위에 해당하는 아래 규칙

- 문서 변경: `documentation-rules.md`
- 버전·태그·Release: `release-rules.md`
- Discord 채널·에이전트·기능: `channel-agent-rules.md`
- 비밀정보·파일·외부 전송: `security-rules.md`

## 유지 방법

- 사용자가 반복 적용할 새 기준을 주면 같은 작업에서 해당 정본에 반영한다.
- 대화 내용을 시간순으로 계속 덧붙이지 않고, 현재 유효한 규칙만 간결하게
  유지한다.
- 규칙이 바뀌면 과거 문장을 남겨 충돌시키지 말고 정본을 수정한다. 과거 기준은
  Git 이력으로 확인한다.
- 사용자 요청과 상위 시스템 지시가 이 문서보다 우선한다.
