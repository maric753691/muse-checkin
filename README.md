# muse-checkin

给 Telegram `@MusePromoteBot` 每天自动签到（`/checkin`），跑在 GitHub Actions 上，
**不需要本机开机**。

## 原理

`checkin.py`：用预先登录好的 StringSession 以本人账号身份发送 `/checkin`，解析 bot 回复写日志。

触发方式（三路冗余，重复签到时 bot 会回"今天已经签到过了"，幂等无副作用）：

1. **Google Apps Script 云端闹钟**（主）：每天 10:17 调 `workflow_dispatch` 触发本 workflow，
   触发主签到；13:23 再触发一次补签。代码见 `apps_script.js`。
2. **GitHub 原生 cron**（备用）：`17 2 * * *` / `23 5 * * *` UTC。注意：**GitHub 免费账号的
   schedule 触发器实测可能完全不触发**（本仓库私有状态下 11 小时 0 次、改为 public 后 40 分钟
   `*/5` 探针也 0 次，而 `workflow_dispatch` 正常），所以不能只依赖它。
3. **本机 Windows 计划任务 / 登录启动**（兜底）：`run_local.ps1` 直接在本机跑签到，
   仅在电脑开机时有效。

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
