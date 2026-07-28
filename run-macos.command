#!/bin/bash

set -u
cd "$(dirname "$0")" || exit 1

echo "========================================"
echo " arch-bot macOS launcher"
echo "========================================"

if [ ! -f ".env" ]; then
  cp ".env.example" ".env"
  echo
  echo ".env 파일을 생성했습니다."
  echo "토큰과 Discord ID를 입력한 뒤 이 파일을 다시 실행하세요."
  open -e ".env"
  read -r -p "Enter를 누르면 종료합니다..."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Python 가상환경을 생성합니다..."
  if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3.11 이상을 먼저 설치해 주세요."
    read -r -p "Enter를 누르면 종료합니다..."
    exit 1
  fi
  python3 -m venv ".venv" || exit 1
fi

if ! ".venv/bin/python" -c "import discord, openai, dotenv" >/dev/null 2>&1; then
  echo "필수 패키지를 설치합니다..."
  ".venv/bin/python" -m pip install . || {
    read -r -p "설치에 실패했습니다. Enter를 누르면 종료합니다..."
    exit 1
  }
fi

export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
echo
echo "봇 서버를 시작합니다. 종료하려면 이 창을 닫거나 Ctrl+C를 누르세요."
echo
".venv/bin/python" -m arch_bot.main

exit_code=$?
echo
echo "봇 서버가 종료되었습니다. 종료 코드: $exit_code"
read -r -p "Enter를 누르면 창을 닫습니다..."
exit "$exit_code"
