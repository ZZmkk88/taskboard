# taskboard 验收

结论：依赖按钉死版本装得上，pytest **15 passed**（exit 0），真服务自测 **ALL 16 CHECKS PASSED**（exit 0）。按 README 用 `python app.py` 绑在 `127.0.0.1:8000`，首页 HTTP 200，进程已退出。**P0 无，P1 无，本轮不改仓库源码。** README 有 1 条硬不符（测试数写成 14）和 1 条覆盖表述过满。许可证文本内部自洽；上游 commit 与署名原文未联网核实。

临时文件、虚拟环境和数据库都在 `E:\muse-bridge\work\TASK-035-taskboard`。完整命令输出在 `run.md`。

## 本地跑通记录

本机 `python --version`：`Python 3.11.9`。`git status --porcelain` 开工时无输出。

虚拟环境：

```
python -m venv E:\muse-bridge\work\TASK-035-taskboard\venv
```

exit 0。没有在仓库里建 `.venv`（`.gitignore` 虽忽略 `.venv/`，任务要求临时文件离开仓库）。下面的 `python` 都是该 venv 的 `Scripts\python.exe`。未执行 `Activate.ps1`。

运行依赖（exit 0）：

```
...\python.exe -m pip install -r E:\muse-bridge\in\TASK-035-taskboard\requirements.txt
```

```
Successfully installed ... fastapi-0.156.4 ... uvicorn-0.54.0
```

测试依赖（exit 0）：

```
...\python.exe -m pip install -r E:\muse-bridge\in\TASK-035-taskboard\requirements-dev.txt
```

```
Successfully installed ... httpx-0.28.1 ... pytest-9.1.1
```

pytest 第一次用未 chdir 的脚本收集，失败原文（执行方式问题，随后重跑通过）：

```
ModuleNotFoundError: No module named 'app'
ERROR tests/test_app.py
1 warning, 1 error in 0.24s
```

按 README，从仓库根跑 `python -m pytest tests/ -q`（脚本 chdir 到仓库，TEMP/TMP 指到工作目录，`-p no:cacheprovider`）：

```
...\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_pytest.py
```

```
...............                                                          [100%]
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
15 passed, 1 warning in 2.58s
```

exit 0。警告来自 venv 里 `fastapi/testclient.py:1`，触发点是 `tests/test_app.py:13` 的 `TestClient`。

真服务自测（脚本把 TEMP 指到工作目录后执行 `tests/live_selftest.py`，服务在 `127.0.0.1:8131`，结束时 `proc.terminate()`）：

```
...\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_live.py
```

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {"token":"(已截断)","username":"admin","must_change_password":true}
PASS 首次登录提示改密
PASS 自带三列 待办/进行中/已完成 | ['待办', '进行中', '已完成']
...
PASS 看板改名
ALL 16 CHECKS PASSED
```

exit 0。令牌来自一次性临时库，正文不写入报告。

README 方式起服务（`TASKBOARD_DB_PATH` 指到工作目录的 `server-check.db`，`PORT=8000`，`TASKBOARD_HOST=127.0.0.1`）：

```
...\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_server_check.py
```

```
startup_seconds=1.15 up=True
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12700]
GET / status=200 ctype=text/html; charset=utf-8
  headers={'x-frame-options': 'DENY', 'content-security-policy': "frame-ancestors 'none'", 'x-content-type-options': 'nosniff'}
  body 含 <title>taskboard · 项目看板</title>
GET /health status=404 {"detail":"Not Found"}
GET /api/health status=404 {"detail":"Not Found"}
GET /docs status=404
GET /redoc status=404
GET /openapi.json status=200
GET /api/boards（无令牌）status=401 {"detail":"未登录"}
POST /api/login 用户名 admin' OR 1=1 -- status=401
POST /api/login admin/admin123 status=200 must_change=true
POST 看板名 a'; DROP TABLE cards; -- status=200，名字按原文保存
POST 卡片额外带 is_archived=1、position=-5 status=200，archived=false position=0
DELETE 看板 status=200，再 GET status=404
POST /api/logout status=200，再 GET /api/me status=401
count users=1 sessions=0 boards=0 board_columns=0 cards=0
after_stop still_accepting=no (ConnectTimeout)
```

删看板后三张表都是 0 行，级联生效。检查脚本另开的 sqlite 连接上 `PRAGMA foreign_keys` 为 0，那是 SQLite 默认值；应用在 `app.py:107` 每个连接单独打开外键。

关闭：`Get-Process -Id 12700` 找不到该进程。`netstat -ano -p tcp` 里 `:8000` 只有 `TIME_WAIT`，没有 `LISTENING`。`probe_port.py` 输出 `down ConnectTimeout: timed out`。`inspect_app.py` 曾打印过 `port8000 accepting=yes`，和后面的进程、netstat、复查不一致，不以那一行当作服务仍在监听。

没有浏览器工具。首页和接口用 httpx 访问。没有在页面上拖卡片或点改密。改密由 pytest 覆盖（`tests/test_app.py:79`、`tests/test_app.py:110`）。

路由（`inspect_app.py`，exit 0）：无依赖的是 `GET /`、`POST /api/login`、`GET /openapi.json`。其余 `/api/*` 的依赖是 `current_user`。OpenAPI 文本里没有 `admin123`、没有 `jsdelivr`，有字段名 `password`。

已有用户后再设 `TB_INITIAL_PASSWORD=should-not-apply`：该口令登录 401，`admin123` 登录 200，`must_change_password` 仍为 true。与 README 环境变量表一致。

跑完后仓库根目录没有 `data/`、`.venv/`、`.pytest_cache/`、`__pycache__/`。`git status --porcelain` 无输出。

令牌 24 小时只核对了代码：`app.py:24` 的 `TOKEN_TTL_SECONDS = 24 * 60 * 60`，登录时写入 `app.py:225`。没有做满 24 小时的过期等待。`0.0.0.0` 没有实际改绑。

## README 与实际不符处

下列之外，安装步骤、默认账号、三列名、8 种颜色（`README.md:12`，`app.py:35`，`static/index.html:126`）、环境变量表（`README.md:44-48` 对 `app.py:23-27` 与 `app.py:812`）、16 个自测点（`README.md:55`，实测 `ALL 16 CHECKS PASSED`）、MIT（`README.md:68`）与代码或本次运行一致。代码里没有 `/health`；README 也没写健康检查 URL，`GET /health` 与 `GET /api/health` 都是 404，不记成双方矛盾。

1. `README.md:54` 写「14 项自动化测试」。同一命令实测 `15 passed`。第 15 个是 `tests/test_app.py:110` 的 `test_change_password_revokes_other_sessions`。`DECISIONS.md:23` 记录过这则回归测试，`README.md:54` 的数字没改。`DECISIONS.md:7` 的「pytest 14 项」是当时那次云端重跑的记录，不把它当成又一条错误。

2. `README.md:7` 写功能「均已实现并通过测试」。`README.md:13` 的鼠标拖拽落点在 `static/index.html:293`，`README.md:12` 的到期高亮、逾期红色在 `static/index.html:239`。pytest 与 `live_selftest.py` 只走 HTTP：移动在 `tests/test_app.py:225`，日期格式在 `tests/test_app.py:208`。自动化测试没有浏览器或 DOM 断言。这两段界面代码在，本次也没有打开浏览器去点。

## 许可证与署名核查

- `LICENSE:1-21` 是完整 MIT 正文。版权行是 `LICENSE:3` 的 `Copyright (c) 2026 taskboard contributors`。年份与本次运行日 2026-10-21 同属 2026。
- `README.md:68` 写 MIT 并指向 LICENSE，与正文一致。
- `README.md:5` 写代码独立编写，来源见 UPSTREAM。`UPSTREAM.md:4` 同样写独立编写、未复制上游代码。`UPSTREAM.md:6-9`：`source_url` 为 `https://github.com/kanboard/kanboard`，`source_commit` 为 `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`，`license: MIT`，`attribution: Copyright (c) Frédéric Guillot`。
- `NOTES.md:6-7` 把同一句署名和同一个 commit 记成 2026-10-21 从 GitHub 抄来的上游原文。UPSTREAM 与 NOTES 彼此一致。
- 在 `*.py`、`*.html`、`*.md`、`*.txt` 里检索 `Kanboard`、`kanboard`、`Frédéric`、`Guillot`、`Copyright`：只有 `NOTES.md:5`、`NOTES.md:7`、`UPSTREAM.md:6`、`UPSTREAM.md:9`。`app.py`、`static/index.html`、测试和 README 没有这些词。`LICENSE` 无扩展名，不在这次检索范围内；直接读到的版权行是 `LICENSE:3`。仓库里没有 PHP 文件。
- 本次按任务没有访问 GitHub。commit 是否仍是该仓库默认分支头、署名是否与上游 LICENSE 逐字相同，**未核实**。没有发现可以改写 LICENSE 或 UPSTREAM 的仓库内证据，这两份文件未改。

内部结论：本项目 MIT 与「未复制上游代码、另附 Kanboard 的 MIT 署名」可以同时成立。版权主体是泛称 `taskboard contributors`，仓库里没有第二个人名和它对打。

## 分级修复清单

### P0

无。安装、pytest、真服务自测、8000 首页都跑通，进程已退出。

### P1

无。写接口都挂了 `current_user`（`inspect_app.py` 的路由列表）。未登录访问看板为 401。删看板后卡片表为 0 行。登录与看板名里的 SQL 片段被当成普通字符串。卡片上的 `is_archived`、`position` 额外字段被忽略。`/docs` 与 `/redoc` 为 404，响应带 `X-Frame-Options: DENY`、`Content-Security-Policy: frame-ancestors 'none'`、`X-Content-Type-Options: nosniff`。

### P2

1. `README.md:54`。修法：把「14 项」改成「15 项」。
2. `app.py:44` 只关了 `docs_url` 和 `redoc_url`，`GET /openapi.json` 实测 200，且不校验登录。修法：同一处加上 `openapi_url=None`。schema 里没有默认口令，首页脚本也是匿名可下的，所以不升到 P1。
3. `app.py:257` 只拒绝短于 6 位的新密码；`app.py:219` 登录口令不限长度就进 20 万次 PBKDF2。修法：哈希之前拒绝过长密码。默认只听 `127.0.0.1`（`app.py:27`，本次启动日志已确认），不升到 P1。
4. `app.py:219` 与 `app.py:259` 用 `!=` 比较哈希。修法：改成 `secrets.compare_digest`。
5. `app.py:683` 的 `delete_card`、`app.py:739` 的 `archive_card`、`app.py:758` 的 `restore_card` 不调用 `_touch_board`，看板 `updated_at` 不动；移动和新建会更新（`app.py:731`、`app.py:643`）。修法：这三处提交前也调用 `_touch_board`。
6. `app.py:25-26` 与 `README.md:9` 的默认口令 `admin` / `admin123`，且只提示改密。修法：保持现状。`DECISIONS.md:23` 写明只提示、不强制；现有测试用这个口令登录。
7. `tests/test_app.py:13` 触发 Starlette 弃用警告，要装 `httpx2`。修法：保持 `requirements-dev.txt:2` 的 `httpx==0.28.1`。测试已通过，且本任务不改依赖版本号、不改测试。
8. `app.py:51` 的 CSP 只有 `frame-ancestors 'none'`。修法：保持现状。页面脚本是内联的，补 `default-src` 就要带 `unsafe-inline`。

本轮只修 P0 和 P1。上面 8 条都不改。
