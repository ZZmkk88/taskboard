# taskboard 验收审查

结论：这个仓库能装上、测试能过、服务能起也能停。没有 P0，没有 P1。本轮不改仓库源码。

pytest：`15 passed, 1 warning in 2.19s`。真服务自测：`ALL 16 CHECKS PASSED`。`GET http://127.0.0.1:8000/` 返回 200，正文含 taskboard。进程终止后端口不再完成握手。

## 本地跑通记录

解释器：`Python 3.11.9`。按任务要求，虚拟环境和数据库放在 `E:\muse-bridge\work\TASK-056-taskboard`，没有写进仓库。

README 的 Windows 步骤是 `py -m venv .venv`。本机默认 `py` 指向坏掉的 3.14，原样执行失败（环境限制，不是项目缺陷）：

```
py -m venv E:\muse-bridge\work\TASK-056-taskboard\.venv-pydefault
```

```
Unable to create process using 'E:\python.exe -m venv ...\.venv-pydefault': ???????????
```

`py -0p` 里 3.14 标成默认，路径 `E:\python.exe`；`py -3.11 --version` 为 `Python 3.11.9`。改用 3.11 建 venv 后安装依赖，exit 0。末尾：

```
Successfully installed ... fastapi-0.156.4 ... httpx-0.28.1 ... pytest-9.1.1 ... uvicorn-0.54.0
```

pytest（cwd 为仓库根，等价于 README 的 `python -m pytest tests/ -q`；加了 `-p no:cacheprovider`，并设 `PYTHONDONTWRITEBYTECODE=1`，避免缓存进仓库）：

```
E:\muse-bridge\work\TASK-056-taskboard\.venv\Scripts\python.exe -m pytest tests/ -q -p no:cacheprovider --tb=short
```

```
...............                                                          [100%]
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
15 passed, 1 warning in 2.19s
```

警告来自已安装的 `fastapi\testclient.py:1`，不是断言失败。15 这个数和 README 一致。

真服务自测：

```
E:\muse-bridge\work\TASK-056-taskboard\.venv\Scripts\python.exe tests/live_selftest.py
```

16 行 `PASS`，最后一行 `ALL 16 CHECKS PASSED`（exit 0）。登录 JSON 里的一次性 token 已打码；`must_change_password` 为 true。脚本把服务起在 `127.0.0.1:8131`，结束时 `terminate()`。

按 README 再起一次 8000 端口（`TASKBOARD_HOST=127.0.0.1`，数据库在工作目录）：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
GET / status=200 ctype=text/html; charset=utf-8
homepage_has_taskboard True
```

安全头：`X-Frame-Options: DENY`，`Content-Security-Policy: frame-ancestors 'none'`，`X-Content-Type-Options: nosniff`。`Cache-Control` 没有。未登录 `GET /api/boards` 为 401 `{"detail":"未登录"}`。`POST /api/login` 200，`must_change_password` true，没有 `Set-Cookie`。

README 没有健康检查路径。实测：

```
GET /health status=404 body={"detail":"Not Found"}
GET /api/health status=404 body={"detail":"Not Found"}
GET /docs status=404
GET /redoc status=404
GET /openapi.json status=404
```

`/app.py`、`/static/index.html`、`/data/taskboard.db`、`/.env` 都是 404。首页 200 作为存活依据。

关掉：`proc.terminate()` 后 `server_exit 1`（Windows 上终止进程的退出码）。新 socket 再连 `127.0.0.1:8000` 和 `8131`，都是 `TimeoutError timed out`（1.5 秒），不再返回 HTTP。服务在听的时候，同地址 `GET /` 是 200，所以进程已经不在握手。局域网地址 `192.168.31.86:8000` 在进程仍活着时也是 ConnectTimeout；日志写明只绑了 `127.0.0.1`。

本机没有浏览器自动化工具。拖拽、到期高亮、确认框只对照了 `static/index.html`，没有做点击级验证。

额外抽查（TestClient，库在工作目录，不计入项目测试数）：外键 `PRAGMA foreign_keys` 为 1；删列、删看板后孤儿卡片 0；另一用户访问别人的看板/归档/卡片都是 404；密码 1025 字符 400、1024 字符错误口令 401；`admin' OR '1'='1` 登录 401；看板名 `x'; DROP TABLE boards;--` 被当成普通名字，列表接口仍 200；退出后原令牌 401；把 `expires_at` 改成 0 后 401；非法日期 `2026-02-31` 400。令牌有效期常量 `TOKEN_TTL` 为 86400 秒。

## README 与实际不符处

对照过并且一致的部分：默认三列、令牌 24 小时（`app.py:24`）、默认账号、环境变量名和默认值（`app.py:23-27` 与 `app.py:841`）、监听 `127.0.0.1:8000`、pytest 15 项、自测 16 个检查点、MIT。下面只列对不上的地方。

1. `README.md:7` 写「功能清单（均已实现并通过测试）」。清单里的到期高亮、拖拽放下、删列确认框只存在于前端：`static/index.html:239-245`、`static/index.html:293-300`、`static/index.html:338-346`。`tests/test_app.py` 和 `tests/live_selftest.py` 都没有这些界面行为的断言。功能在页面里，自动化测试没覆盖。「并通过测试」超出了测试实际覆盖的范围。
2. `README.md:55` 写「真服务自测：起真服务走一遍完整流程，16 个检查点」。16 这个数字属实（`tests/live_selftest.py` 的 `check()` 到 `tests/live_selftest.py:108` 的看板改名结束）。流程里没有改密、删看板、删列、退出登录。叫「完整流程」偏满。

`README.md:32` 的 `py -m venv` 在本机失败，原因是本机 `py` 启动器坏了，不记成文档和代码不符。

## 许可证与署名核查

内部自洽。上游仓库上的版本号、commit、版权原文没有联网重查（任务禁止抓取外部页面），这三项标为未核实。没有改 `LICENSE` 或 `UPSTREAM.md`。

- `LICENSE:1-3`：MIT，版权行 `Copyright (c) 2026 taskboard contributors`。`README.md:68-69` 写 MIT 并指向该文件。两边一致。
- `UPSTREAM.md:3-9`：声明代码独立编写、未复制上游；参考 `https://github.com/kanboard/kanboard`，commit `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`，许可证 MIT，署名 `Copyright (c) Frédéric Guillot`。
- `NOTES.md:3-8` 与上面 commit、MIT、署名原文一致，并多写了 Kanboard 版本 1.2.54。版本号未核实。
- `README.md:5` 的「独立编写」和 `UPSTREAM.md:4` 的「未复制上游代码」一致。抽查 `app.py`、`static/index.html`：这是 Python + FastAPI + 单页，没有 PHP，也没有整段上游源码。设计参考不要求把 Guillot 写进本项目 `LICENSE`。两份版权分属两个作品，不冲突。
- commit 是否真是 2026-10-21 的 Kanboard HEAD、版权行是否与上游 LICENSE 逐字相同：未核实。仓库里这两处互相一致，没有发现可以改 `UPSTREAM.md` 的反证。

## 分级修复清单

### P0

无。安装、`15 passed`、`ALL 16 CHECKS PASSED`、首页 200 都已经跑到。

### P1

无。未登录 401，跨用户资源 404，删列/删看板没有留下孤儿行，文档和源码路径 404，默认只绑 127.0.0.1，超长密码在 PBKDF2 之前被拒绝（`app.py:220-221`、`app.py:268-273`）。默认口令只提示不强制，是 `DECISIONS.md:23` 的既定口径，而且 `tests/test_app.py` 的模块级 `auth` 夹具就是不改密直接调接口；改成强制会让现有测试失败。本轮不改。

### P2

1. `README.md:7`。修法：把「并通过测试」改成自动化测试覆盖 API，到期高亮、拖拽、确认框没有单测。
2. `README.md:55`。修法：删掉「完整流程」或补上未覆盖改密、删除和退出。
3. `static/index.html:410`。修法：用本地令牌恢复会话时，如果 `/api/me` 的 `must_change_password` 为真，再 toast 一次。不要改成不改密就拦接口。
4. `app.py:54-59`。修法：给 `/api/` 响应加 `Cache-Control: no-store`。当前令牌在 Authorization 头里，不在 cookie 里；没有复现出退出后还能从缓存读到看板，所以不升到 P1。
5. `app.py:75-80`。修法：`_clean_text` 拒绝 `\x00`。实测标题 `ab\x00cd` 会原样入库（字节 97,98,0,99,100），没有截断，也没有变成可执行脚本。
6. `requirements-dev.txt:2`。修法：不改。pytest 有一条 `StarletteDeprecationWarning`，提示用 httpx2 替换 httpx==0.28.1。任务禁止改已有依赖版本，`DECISIONS.md:37` 也写了不升 httpx。测试是通过的，这不是冲突。
7. `app.py:137-141`。修法：启动或登录时删掉过期会话行。现在只是查询时过滤，过期令牌不能用，表会慢慢变长。
