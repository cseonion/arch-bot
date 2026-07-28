from __future__ import annotations

import logging

from dotenv import load_dotenv

from arch_bot.bot import create_bot
from arch_bot.config import ConfigError, Settings


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        raise SystemExit(f"Configuration error: {exc}") from exc
    create_bot(settings).run(settings.discord_token, log_handler=None)


if __name__ == "__main__":
    main()
