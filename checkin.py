# -*- coding: utf-8 -*-
"""MusePromote 每日签到（可在 GitHub Actions 中运行）。

环境变量：
  TG_API_ID     my.telegram.org 的 api_id
  TG_API_HASH   my.telegram.org 的 api_hash
  TG_SESSION    StringSession（登录时生成）
  可选 TG_PROXY 本地调试用，例如 http://127.0.0.1:10808

退出码：0=签到成功/今天已签；2=未知回复；3=需要加群；1=异常
"""
import asyncio
import os
import sys
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from telethon import TelegramClient
from telethon.sessions import StringSession

BOT = os.environ.get("TG_BOT", "@MusePromoteBot")
WAIT = float(os.environ.get("TG_WAIT", "6"))


def proxy_conf():
    raw = os.environ.get("TG_PROXY", "").strip()
    if not raw:
        return None
    u = urlparse(raw if "://" in raw else "http://" + raw)
    return {"proxy_type": u.scheme or "http", "addr": u.hostname,
            "port": u.port or 10808, "rdns": True}


def classify(text: str):
    if "签到成功" in text:
        return 0, "SUCCESS"
    if "已经签到" in text:
        return 0, "ALREADY"
    if "请先加入" in text:
        return 3, "NEED_JOIN"
    return 2, "UNKNOWN"


async def sign_in_once(client):
    sent = await client.send_message(BOT, "/checkin")
    await asyncio.sleep(WAIT)
    msgs = await client.get_messages(BOT, limit=6)
    replies = [m for m in msgs if not m.out and m.id > sent.id]
    if not replies:
        # 兜底：bot 的「📅 每日签到」是文本按钮，直接发文本等价于点按钮
        print("no reply to /checkin, retry with button text")
        sent = await client.send_message(BOT, "📅 每日签到")
        await asyncio.sleep(WAIT)
        msgs = await client.get_messages(BOT, limit=6)
        replies = [m for m in msgs if not m.out and m.id > sent.id]
    if not replies:
        print("ERROR: bot did not reply")
        return 2, "NO_REPLY", ""
    m = sorted(replies, key=lambda x: x.id)[0]
    text = (m.text or "").strip()
    code, label = classify(text)
    return code, label, text


async def main():
    client = TelegramClient(
        StringSession(os.environ["TG_SESSION"]),
        int(os.environ["TG_API_ID"]),
        os.environ["TG_API_HASH"],
        proxy=proxy_conf(),
        connection_retries=5,
        request_retries=5,
        timeout=30,
    )
    await client.connect()
    try:
        me = await client.get_me()
        print(f"account: id={me.id} @{me.username}")
        code, label, text = await sign_in_once(client)
        print(f"RESULT: {label}")
        print("---- bot reply ----")
        print(text)
        print("-------------------")
        return code
    finally:
        await client.disconnect()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
