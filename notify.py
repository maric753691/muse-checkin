# -*- coding: utf-8 -*-
"""签到失败时给本人发一条 Telegram 消息（Saved Messages）。"""
import asyncio
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from telethon import TelegramClient
from telethon.sessions import StringSession

TEXT = os.environ.get(
    "NOTIFY_TEXT",
    "⚠️ muse-checkin 签到失败，请查看 Actions 日志：\n"
    "https://github.com/maric753691/muse-checkin/actions",
)


async def main():
    client = TelegramClient(
        StringSession(os.environ["TG_SESSION"]),
        int(os.environ["TG_API_ID"]),
        os.environ["TG_API_HASH"],
        connection_retries=5, request_retries=5, timeout=30,
    )
    await client.connect()
    try:
        await client.send_message("me", TEXT)
        print("notified")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
