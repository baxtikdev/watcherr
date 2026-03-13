from __future__ import annotations

import asyncio
import os
import sys

from watcherr.bot.handlers import router


def main() -> None:
    token = os.getenv("WATCHERR_BOT_TOKEN")
    if not token:
        print("Error: WATCHERR_BOT_TOKEN environment variable is required")
        sys.exit(1)

    asyncio.run(_run(token))


async def _run(token: str) -> None:
    from aiogram import Bot, Dispatcher

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    print(f"watcherr bot started (token: ...{token[-6:]})")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    main()
