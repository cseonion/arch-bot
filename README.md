# arch-bot

Discord에서 사용하는 건축 업무용 LLM 비서의 초기 실행 환경입니다.

현재 제공하는 기능:

- `/ask <질문>`: 현재 채널의 대화 맥락을 이어서 답변
- 지정된 Task 채널: 명령어 없이 일반 메시지로 독립 에이전트와 대화
- `/reset`: 현재 채널의 대화 맥락 초기화
- `/status`: 연결 상태, 사용 모델과 현재 에이전트 확인
- Discord 길이 제한을 고려한 긴 답변 자동 분할
- 에이전트별 시스템 프롬프트와 Skill/Tool/MCP 할당 구조
- 환경변수 기반 비밀키 및 모델 설정

## 1. Discord 앱 만들기

1. [Discord Developer Portal](https://discord.com/developers/applications)에서
   **New Application**을 선택합니다.
2. **Bot** 메뉴에서 봇 토큰을 생성합니다. 토큰은 외부에 공유하거나 Git에
   커밋하지 않습니다.
3. **Installation**에서 서버 설치를 활성화하고 `bot`,
   `applications.commands` scope를 선택합니다.
4. 봇 권한은 최소한 `View Channels`, `Send Messages`를 부여합니다.
5. 생성된 설치 링크로 테스트 서버에 앱을 추가합니다.
6. **Bot** 메뉴의 **Privileged Gateway Intents**에서
   **Message Content Intent**를 활성화합니다.

`/ask`만 사용할 때는 Message Content Intent가 필요하지 않지만, 지정 채널의
일반 메시지를 수신하려면 반드시 필요합니다.

## 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env`에 `DISCORD_TOKEN`과 `OPENAI_API_KEY`를 입력합니다. 개발 중에는 Discord
서버 ID를 `DISCORD_GUILD_ID`에 입력하면 슬래시 명령이 해당 서버에 바로
동기화됩니다. 서버 ID는 Discord의 개발자 모드를 켠 뒤 서버를 우클릭하여 복사할
수 있습니다.

Discord 개발자 모드를 켠 뒤 각 채널을 우클릭하여 **채널 ID 복사**를 선택하고
다음 값을 설정합니다.

```dotenv
DISCORD_TASK1_CHANNEL_ID=건축봇-task1의_채널_ID
DISCORD_TASK2_CHANNEL_ID=건축봇-task2의_채널_ID
```

채널 이름이 아니라 숫자로 된 채널 ID를 사용합니다. 지정하지 않은 Task 채널은
자동 대화 대상에서 제외되지만 `/ask`는 계속 사용할 수 있습니다.

기본 모델은 비용과 성능의 균형을 위한 `gpt-5.6-terra`입니다. `.env`의
`OPENAI_MODEL`을 바꾸면 코드 수정 없이 다른 모델을 사용할 수 있습니다.

## 3. 로컬 실행

Python 3.11 이상이 필요합니다.

가장 간단한 방법은 운영체제에 맞는 파일을 더블 클릭하는 것입니다.

- macOS: `run-macos.command`
- Windows: `run-windows.bat`

첫 실행 시 가상환경과 패키지를 준비합니다. `.env`가 없으면 예제 파일을 복사해
편집기로 열고 종료하며, 설정을 마친 뒤 다시 더블 클릭하면 봇 서버가 실행됩니다.
열린 터미널 창을 닫거나 `Ctrl+C`를 누르면 봇도 종료됩니다.

터미널에서 직접 실행하려면 다음 명령을 사용합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install ".[dev]"
arch-bot
```

일반 설치 방식을 사용하므로 소스 코드를 변경한 뒤에는
`python -m pip install ".[dev]"`를 다시 실행합니다. macOS의 Python 3.14에서는
editable 설치(`-e`)의 경로 파일이 숨김 처리되어 패키지를 찾지 못하는 경우가
있어 권장하지 않습니다.

또는 Docker를 사용합니다.

```bash
docker compose up --build
```

로그에 `Connected as ...; 2 autonomous channels configured`가 표시되면
Discord에서 `/status`, `/ask`를 확인하고 지정한 Task 채널에 일반 메시지를
입력합니다.

## 4. 에이전트 구성

각 에이전트는 `config/agents/<agent-id>/`에 독립적으로 구성합니다.

```text
config/
├── agents/
│   ├── default/  # 일반 채널의 /ask
│   ├── task1/    # 건축봇-task1
│   └── task2/    # 건축봇-task2
├── skills/       # 재사용 가능한 프롬프트 지침
├── tools/        # 향후 로컬 Tool 어댑터
└── mcp/          # 향후 MCP 연결 어댑터
```

각 `profile.toml`에서 채널 환경변수, 시스템 프롬프트 파일과 할당 기능을
선언합니다.

```toml
id = "task1"
display_name = "건축봇 Task 1"
channel_id_env = "DISCORD_TASK1_CHANNEL_ID"
system_prompt_file = "system.md"

[capabilities]
skills = ["architecture-safety"]
tools = []
mcp_servers = []
```

시스템 프롬프트는 같은 폴더의 `system.md`를 수정합니다. `skills`에 등록한
`config/skills/<name>.md`는 해당 에이전트의 시스템 프롬프트에 자동으로
결합됩니다.

현재 `skills`는 실제 적용되는 프롬프트 모듈입니다. `tools`와 `mcp_servers`는
에이전트별 할당을 위한 선언부이며, 실제 실행은 각 Tool/MCP 어댑터가 추가된
이후 활성화됩니다. 연결되지 않은 기능을 실행된 것처럼 처리하지 않습니다.

## 5. 검증

```bash
ruff check .
pytest
```

## 현재 범위와 다음 단계

대화 맥락은 에이전트와 채널별로 분리되지만 프로세스 메모리에만 저장되므로
재시작하면 초기화됩니다. 건축 문서 저장소 연결, 권한 체계, 감사 로그, 영속 대화
기록, Tool/MCP 실행 및 승인 흐름은 이후 단계에서 추가합니다.

OpenAI 연동은 Responses API를 사용합니다. 일반 메시지는 `.env`에 지정한 Task
채널에서만 처리하며 다른 텍스트 채널의 내용에는 반응하지 않습니다.
