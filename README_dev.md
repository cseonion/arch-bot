# 개발자 안내

## 1. 환경 세팅 방법

### 요구사항

- Python 3.11 이상
- Discord 애플리케이션과 Bot Token
- OpenAI API Key
- 일반 메시지와 첨부 수신을 위한 Discord `Message Content Intent`

`.env.example`을 `.env`로 복사한 뒤 비밀값과 Discord ID를 입력합니다.

```dotenv
DISCORD_TOKEN=
OPENAI_API_KEY=
DISCORD_GUILD_ID=
DISCORD_TASK1_CHANNEL_ID=
DISCORD_TASK2_CHANNEL_ID=
```

서버 ID와 채널 ID는 Discord 개발자 모드를 켠 뒤 각각 서버와 채널을 우클릭하여
복사합니다. `.env`는 절대 Git에 커밋하지 않습니다.

### 더블 클릭 실행

- macOS: `run-macos.command`
- Windows: `run-windows.bat`

실행 파일은 프로젝트 루트로 이동하고, `.venv`가 없으면 생성하며, 필수
의존성을 확인한 뒤 `PYTHONPATH=src`로 봇을 시작합니다. 실행 창을 닫거나
`Ctrl+C`를 누르면 봇도 종료됩니다.

### 터미널 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install ".[dev]"
PYTHONPATH=src python -m arch_bot.main
```

Windows PowerShell에서는 다음 명령을 사용합니다.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install ".[dev]"
$env:PYTHONPATH = "src"
python -m arch_bot.main
```

Docker 실행:

```bash
docker compose up --build
```

검증:

```bash
ruff check .
pytest
```

## 2. 채널별 역할 및 기능에 따른 저장소 구조

```text
arch-bot/
├── config/
│   ├── agents/
│   │   ├── default/      # 일반 채널 /ask
│   │   ├── task1/        # 파일 분석 채널
│   │   └── task2/        # 추후 역할 정의
│   ├── skills/           # 재사용 프롬프트 지침
│   ├── tools/            # 로컬 Tool 명세
│   └── mcp/              # MCP 연결 명세
├── src/arch_bot/
│   ├── agent.py          # OpenAI Responses API와 대화 상태
│   ├── attachments.py    # 첨부 검증·변환·CAD 요약
│   ├── bot.py            # Discord 명령과 채널 라우팅
│   ├── config.py         # 환경변수
│   └── profiles.py       # 에이전트 프로필 로더
├── tests/
├── for_codex/            # 저장소 작업 장기 규칙
├── CHANGELOG.md
└── README_dev.md
```

### 일반 채널

`default` 프로필을 사용합니다. 일반 메시지에는 반응하지 않고 `/ask`로 받은
텍스트를 처리합니다.

### 건축봇-task1

`DISCORD_TASK1_CHANNEL_ID`로 라우팅하며 명령어 없는 메시지와 첨부를 처리합니다.
파이프라인은 다음과 같습니다.

1. 채널과 프로필의 첨부 정책 확인
2. 파일 수, 개별 크기와 합산 크기 검사
3. 안전한 파일명 정규화 및 기본 파일 서명 검사
4. 이미지·지원 문서를 Base64 구조화 입력으로 변환
5. ASCII DXF·IFC는 원본 전송 없이 제한된 메타데이터 요약
6. DWG·DGN·RVT는 미분석 사실과 변환 형식 안내
7. 실제 분석 파일과 건너뛴 파일을 구분하여 모델과 사용자에게 전달

Task1 기본 제한은 한 메시지 5개, 개별 15MiB, 합산 30MiB입니다. OpenAI
`input_file`의 파일당·합산 50MB 제한보다 낮게 설정해 Base64 요청 오버헤드와
메모리 사용 여유를 둡니다.

PDF는 텍스트와 페이지 이미지가 전달되지만 비PDF 문서는 텍스트만 추출됩니다.
스프레드시트는 기초 증강 입력이며, 정밀 계산·조인·차트 생성은 전용 Tool이
필요합니다.

### 건축봇-task2

독립 대화 맥락만 구성된 상태입니다. 역할을 추가할 때
`config/agents/task2/system.md`, `profile.toml`, 관련 Skill/Tool/MCP, 테스트와
사용자 문서를 함께 갱신합니다.

### 에이전트 추가 방법

1. `config/agents/<id>/profile.toml`과 `system.md`를 생성합니다.
2. 전용 `DISCORD_<ID>_CHANNEL_ID` 환경변수를 `.env.example`에 추가합니다.
3. Skill, Tool, MCP 허용 목록과 첨부 정책을 선언합니다.
4. 채널 라우팅·권한·오류 흐름 테스트를 추가합니다.
5. `README.md`, `README_dev.md`, `CHANGELOG.md`, `for_codex` 정본을 갱신합니다.

## 3. 채널별 Tool/MCP/Skill 기본 설명

| 구분 | 의미 | 현재 상태 |
|---|---|---|
| Skill | 시스템 프롬프트에 결합되는 재사용 업무 지침 | `config/skills/*.md`가 실제 적용됨 |
| Tool | 입력·출력 계약을 가진 로컬 실행 기능 | 구현과 런타임 등록이 있어야 실행 가능 |
| MCP | 외부 서버가 제공하는 데이터·기능 연결 | 서버 설정, 인증과 승인 정책이 필요 |

`profile.toml`의 `capabilities` 목록은 해당 에이전트에 대한 할당 또는 허용
선언입니다. 이름을 적는 것만으로 실행 기능이 생기지는 않습니다.

### 현재 에이전트별 구성

| 에이전트 | Skill | Tool | MCP |
|---|---|---|---|
| `default` | `architecture-safety` | 없음 | 없음 |
| `task1` | `architecture-safety` | `task1-attachment-reader` | 없음 |
| `task2` | `architecture-safety` | 없음 | 없음 |

`task1-attachment-reader`는 `attachments.py`에서 Discord 첨부파일을 모델 입력
또는 제한된 CAD 메타데이터 요약으로 만드는 전처리 Tool입니다. 현재 LLM의
자율 함수 호출 Tool은 아니며 Discord 입력 파이프라인에서 애플리케이션이
결정적으로 실행합니다.

## 버전과 릴리스

모든 변경은 [CHANGELOG.md](CHANGELOG.md)의 `[미출시]`에 한국어로 누적합니다.
배포 가능한 기능 묶음이 준비되고 `main`의 CI가 통과한 뒤에만 버전, Git tag와
GitHub Release를 만듭니다. 상세 기준은
[for_codex/release-rules.md](for_codex/release-rules.md)를 따릅니다. `vX.Y.Z`
태그를 Push하면 Release workflow가 CHANGELOG의 해당 한국어 두 단을 검증해
GitHub Release 본문으로 사용합니다.

OpenAI 파일 입력 구현은 공식
[File inputs](https://developers.openai.com/api/docs/guides/file-inputs)와
[Images and vision](https://developers.openai.com/api/docs/guides/images-vision)
문서를 기준으로 합니다.
