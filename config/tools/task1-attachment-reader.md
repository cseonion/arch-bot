# task1-attachment-reader

Task1 채널에서 Discord 첨부파일을 검증하고 OpenAI Responses API의 구조화 입력
또는 제한된 CAD 메타데이터 요약으로 변환하는 애플리케이션 전처리 Tool입니다.

## 입력

- Discord Attachment 목록
- Task1 `profile.toml`의 `[attachments]` 정책

## 출력

- `input_image`, `input_file`, `input_text` 입력 항목
- 실제 분석에 포함한 파일명
- 거절하거나 건너뛴 파일과 사용자 안내

## 경계

- LLM이 자율적으로 호출하는 Function Tool이 아니라 메시지 처리 파이프라인에서
  결정적으로 실행됩니다.
- ASCII DXF와 IFC는 구조 요약만 하며 DWG, DGN, RVT 원본은 분석하지 않습니다.
- 악성코드 탐지기나 CAD 형상 검증기가 아닙니다.
