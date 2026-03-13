from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    chat_id = message.chat.id
    await message.answer(
        f"<b>watcherr</b> bot activated.\n\n"
        f"Your chat ID: <code>{chat_id}</code>\n\n"
        f"Set this as <code>WATCHERR_CHAT_ID</code> in your environment.",
        parse_mode="HTML",
    )


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    await message.answer(
        "<b>watcherr</b> is running and listening for alerts.",
        parse_mode="HTML",
    )


@router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("pong")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>Commands:</b>\n/start — Get chat ID\n/status — Check bot status\n/ping — Ping\n/help — This message",
        parse_mode="HTML",
    )
