# MCP servers

에이전트별 MCP 서버 연결 설정과 사용 정책을 둘 위치입니다. 프로필의
`capabilities.mcp_servers`는 할당 목록을 선언하지만, 현재 버전은 아직 MCP
연결 어댑터를 제공하지 않습니다.

비밀키는 이 디렉터리에 저장하지 않고 `.env` 또는 배포 환경의 secret manager를
사용합니다.
