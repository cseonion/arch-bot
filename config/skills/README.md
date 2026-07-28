# Skills

재사용할 프롬프트 지침을 Markdown 파일로 저장합니다. 에이전트 프로필의
`capabilities.skills`에 확장자를 제외한 이름을 기록하면 시스템 프롬프트 뒤에
해당 Skill이 추가됩니다.

이 디렉터리의 Skill은 현재 프롬프트 모듈입니다. 실행 코드나 외부 시스템 접근이
필요한 Skill은 별도의 Tool 또는 MCP 어댑터 구현이 필요합니다.
