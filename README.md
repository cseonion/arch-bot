# arch-bot

Discord에서 사용하는 건축 업무용 LLM 비서의 초기 실행 환경입니다.

현재 제공하는 기능:

- `/ask <질문>`: 현재 채널의 대화 맥락을 이어서 답변
- `/reset`: 현재 채널의 대화 맥락 초기화
- `/status`: 연결 상태와 사용 모델 확인
- Discord 길이 제한을 고려한 긴 답변 자동 분할
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

이 봇은 슬래시 명령을 사용하므로 `MESSAGE_CONTENT` privileged intent가 필요하지
않습니다.

## 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env`에 `DISCORD_TOKEN`과 `OPENAI_API_KEY`를 입력합니다. 개발 중에는 Discord
서버 ID를 `DISCORD_GUILD_ID`에 입력하면 슬래시 명령이 해당 서버에 바로
동기화됩니다. 서버 ID는 Discord의 개발자 모드를 켠 뒤 서버를 우클릭하여 복사할
수 있습니다.

기본 모델은 비용과 성능의 균형을 위한 `gpt-5.6-terra`입니다. `.env`의
`OPENAI_MODEL`을 바꾸면 코드 수정 없이 다른 모델을 사용할 수 있습니다.

## 3. 로컬 실행

Python 3.11 이상이 필요합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
arch-bot
```

또는 Docker를 사용합니다.

```bash
docker compose up --build
```

로그에 `Connected as ...`가 표시되면 Discord에서 `/status`, `/ask` 순서로
확인합니다.

## 4. 검증

```bash
ruff check .
pytest
```

## 현재 범위와 다음 단계

대화 맥락은 프로세스 메모리에만 저장되므로 재시작하면 초기화됩니다. 현재 봇은
텍스트 질의응답 기반의 최소 운용 버전이며, 건축 문서 저장소 연결, 권한 체계,
감사 로그, 영속 대화 기록, 도구 실행 승인 흐름은 이후 단계에서 추가합니다.

OpenAI 연동은 Responses API를 사용합니다. Discord 명령은 슬래시 명령 기반이라
일반 채팅 내용을 수집하지 않습니다.
