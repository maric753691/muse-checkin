# muse-checkin

给 Telegram `@MusePromoteBot` 每天自动签到（`/checkin`），跑在 GitHub Actions 上，
**不需要本机开机**。

## 原理

workflow 每天 02:00 UTC（北京时间 10:00）触发，随机延迟 1~36 分钟后执行
`checkin.py`：用预先登录好的 StringSession 以本人账号身份发送 `/checkin`，
解析 bot 回复并写入日志。

## 需要的 Secrets

| 名称 | 说明 |
| --- | --- |
| `TG_API_ID` | my.telegram.org 的 api_id |
| `TG_API_HASH` | my.telegram.org 的 api_hash |
| `TG_SESSION` | 本机 `login_local.py` 登录后生成的 StringSession |

⚠️ `TG_SESSION` 等同于账号登录态，泄露 = 账号被完全控制。仓库务必保持 **private**，
不要把它写进任何提交的文件。

## 手动触发

Actions → `muse-checkin` → Run workflow。

## 日志判读

- `RESULT: SUCCESS` —— 签到成功
- `RESULT: ALREADY` —— 今天已经签过（正常，exit 0）
- `RESULT: NEED_JOIN` —— bot 要求先加入 @MusePromote1 / @MusePromote2 群
- `RESULT: UNKNOWN` —— bot 话术变了，需要更新 `checkin.py` 里的关键字

## 本地调试（需代理）

```powershell
$env:TG_API_ID="..."; $env:TG_API_HASH="..."; $env:TG_SESSION="..."; $env:TG_PROXY="http://127.0.0.1:10808"
python checkin.py
```
