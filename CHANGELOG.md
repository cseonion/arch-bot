# 변경 기록

이 프로젝트는 [Semantic Versioning](https://semver.org/)을 따릅니다. 모든
설명은 한국어로 작성하며, 릴리스 전 변경은 `[미출시]`에 누적합니다.

## [미출시]

### 1. 서비스 사용자용 변경 사항

- Discord의 `건축봇-task1` 채널에 질문과 함께 이미지, PDF, Word·표 문서 등을
  올리면 파일 내용을 바탕으로 답변을 받을 수 있습니다. 설명 없이 파일만 올려도
  기본 검토를 시작합니다.
- ASCII DXF와 IFC는 주요 객체 구성을 요약하며, 아직 직접 해석할 수 없는
  DWG·DGN·RVT는 읽은 것처럼 답하지 않고 PDF·DXF·IFC 등 권장 변환 형식을
  안내합니다.
- 손상되거나 너무 크거나 지원되지 않는 파일은 어떤 파일을 건너뛰었는지 이유를
  명확히 알려줍니다.
- macOS와 Windows에서 실행 파일을 더블 클릭해 봇을 시작할 수 있고, Task 채널은
  명령어 없이 자연스럽게 대화할 수 있습니다.

### 2. 개발자용 업데이트 로그

- Discord Attachment를 크기·확장자·기본 파일 서명 기준으로 검증하고 Responses
  API의 `input_image`·`input_file` Base64 입력으로 변환하는 파이프라인을
  추가했습니다.
- Task1 프로필에 첨부 허용 목록, 파일 수, 개별·합산 크기, 이미지·PDF detail
  정책과 `task1-attachment-reader` Tool 선언을 추가했습니다.
- ASCII DXF 및 IFC 구조 메타데이터 요약기와 DWG·DGN·RVT 변환 안내 경계를
  추가했습니다.
- 에이전트별 프롬프트·Skill·Tool·MCP 선언 구조, Windows/macOS launcher,
  사용자/개발자 문서 분리와 `for_codex` 장기 규칙을 추가했습니다.
- SemVer 태그에서 한국어 두 단 변경 기록을 검증해 GitHub Release를 만드는
  workflow를 추가했습니다.
- GitHub Actions에서도 저장소 루트의 릴리스 스크립트 테스트를 찾을 수 있도록
  pytest 실행 경로를 `python -m pytest`로 통일했습니다.
- 첨부파일 구조화 API 입력, 파일 전용 메시지, 실패 시 모델 호출 차단, 파일
  서명, CAD 요약과 프로필 정책 테스트를 추가했습니다.
