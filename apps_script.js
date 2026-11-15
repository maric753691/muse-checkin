/**
 * MusePromote 每日签到 —— 云端闹钟（Google Apps Script）
 *
 * 作用：每天定时调用 GitHub Actions 的 workflow_dispatch 接口，
 *      由 GitHub 的服务器执行 checkin.py —— 你的电脑关机也能签。
 *
 * 原因：GitHub 免费账号的 schedule(cron) 触发器不工作（实测 11 小时 0 次），
 *      所以用 Google 的定时器来"敲门"。
 *
 * 首次使用：
 *   1. 把下面的 TOKEN 换成你新建的 GitHub fine-grained token（见聊天里的步骤）
 *   2. 运行 installTriggers()，按提示授权（会弹"未验证应用"，点"高级 → 继续"）
 *   3. 运行 triggerMain() 测试一次，看日志里是不是 HTTP 204
 */

const REPO = 'maric753691/muse-checkin';
const WORKFLOW = 'checkin.yml';
const TOKEN = 'PASTE_YOUR_FINE_GRAINED_PAT_HERE'; // github_pat_ 开头

function dispatch(skipDelay) {
  const url = 'https://api.github.com/repos/' + REPO +
              '/actions/workflows/' + WORKFLOW + '/dispatches';
  const res = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + TOKEN,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    },
    payload: JSON.stringify({ ref: 'main', inputs: { skip_delay: skipDelay } }),
    muteHttpExceptions: true
  });
  const code = res.getResponseCode();
  Logger.log('dispatch skip_delay=' + skipDelay + ' -> HTTP ' + code);
  if (code !== 204) {
    Logger.log(res.getContentText());
  }
}

// 10:17 主签到：交给 workflow 内的随机延迟（1~30 分钟），避免每天同一分钟
function triggerMain() {
  dispatch('false');
}

// 13:23 补签：若已签到，bot 会回"今天已经签到过了"，幂等无副作用
function triggerBackup() {
  dispatch('true');
}

// 安装两个每日触发器（重复运行会先清空旧的，不会重复触发）
function installTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('triggerMain').timeBased()
    .atHour(10).nearMinute(17).everyDays(1).inTimezone('Asia/Shanghai').create();
  ScriptApp.newTrigger('triggerBackup').timeBased()
    .atHour(13).nearMinute(23).everyDays(1).inTimezone('Asia/Shanghai').create();
  Logger.log('triggers installed');
}
