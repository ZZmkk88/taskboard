# taskboard 验收审查

结论：仓库能在本机装起来并跑通。pytest 16 项通过，真服务自测 16 项通过，默认端口 8000 的首页返回 200。P0、P1 为零，本轮不改源码。许可证与署名在仓库内部自洽。上游 commit 与许可证原文未联网复核。

## 本地跑通记录

环境：`python --version` 输出 `Python 3.11.9`。本机 `py --version` 退出码 1，原文 `Unable to create process using 'E:\python.exe --version'`。README 的 `py -m venv` 因此没走，改用 `python -m venv`。这是本机启动器问题。

虚拟环境与临时库都在 `E:\muse-bridge\work\TASK-090-taskboard`，没有写进仓库。

装依赖（exit 0）：

```
E:\muse-bridge\work\TASK-090-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-090-taskboard\requirements-dev.txt
```

结果行：`Successfully installed ... fastapi-0.156.4 ... httpx-0.28.1 ... pytest-9.1.1 ... starlette-1.9.0 ... uvicorn-0.54.0`。

`starlette-1.9.0.dist-info/METADATA` 第 26 行是 `Requires-Python: >=3.11`。`fastapi-0.156.4.dist-info/METADATA` 第 39 行是 `Requires-Python: >=3.10`。更严的下限是 starlette，与 README 第 18 行一致。

pytest（在仓库目录，exit 0）。收尾重跑结果：

```
................                                                         [100%]
16 passed, 1 warning in 2.69s
```

警告原文：`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.` 来自已安装的 `fastapi/testclient.py` 第 1 行再导入 starlette。退出码是 0，16 项都过了。

真服务自测 `tests/live_selftest.py`（exit 0），脚本固定 `http://127.0.0.1:8131`。收尾重跑末行：`ALL 16 CHECKS PASSED`。登录打印里的令牌是 `<redacted>`。

按 README 起服务：不设 `TASKBOARD_HOST`，`PORT=8000`，数据库放到工作目录的 `probe.db`。uvicorn 日志：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:53015 - "GET / HTTP/1.1" 200 OK
```

`GET /` 为 200，`content-type: text/html; charset=utf-8`，正文长度 23444，含 `taskboard`。响应头有 `X-Frame-Options: DENY`、`Content-Security-Policy: frame-ancestors 'none'`、`X-Content-Type-Options: nosniff`。

README 没有健康检查路径。实测 `GET /health`、`GET /api/health`、`GET /healthz` 都是 404，正文 `{"detail":"Not Found"}`。首页正常，这个 404 不记成故障。

同一进程里还看到：`/docs`、`/redoc`、`/openapi.json` 为 404；未登录访问 `/api/boards` 为 401 且 `Cache-Control: no-store`；`admin` / `admin123` 登录成功且 `must_change_password` 为 true；另一个用户读、改、删别人的看板或卡片得到 404；删除看板后 `boards`、`board_columns`、`cards` 行数都是 0；`sessions.token` 长度为 64。查完后对启动进程 `terminate()`，再次连接超时，端口已关掉。

无浏览器工具。拖拽、到期颜色、确认框只做了静态对照，没有在页面上点击。对应代码在 `static/index.html`：拖拽投放第 293–302 行，到期样式第 61–63 行与 `dueChip` 第 239–246 行，确认框第 219、347、387、406 行。

## README 与实际不符处

行为与 README 一致的部分：16 项 pytest（`tests/test_app.py` 共 16 个 `test_` 函数，收尾重跑 `16 passed`）、16 个自测检查点、默认账号、令牌 24 小时（`app.py:24`）、密码 6–1024 与超长登录拒绝（`app.py:34`、`app.py:230`、`app.py:287-290`）、默认三列（`app.py:35`）、8 色（`app.py:36` 与 `static/index.html:126`）、监听地址和端口（`app.py:27`、`app.py:860`，日志为 `127.0.0.1:8000`）、数据库默认路径（`app.py:23`）、文档页关闭（`app.py:47-49`，实测 404）、MIT（`LICENSE:1`）。

只有一条文案粒度差异：

1. `README.md:9` 写新密码需 6–1024 位。后端 `app.py:287-290` 按这个范围拒绝。改密弹窗 `static/index.html:164` 只写「新密码（至少 6 位）」，没有写出 1024 上限。后端行为与 README 一致，界面少了一句上限。

## 许可证与署名核查

仓库内部是对齐的。

- `LICENSE:1-3`：MIT，`Copyright (c) 2026 taskboard contributors`。正文是标准 MIT 许可。
- `README.md:5` 写代码独立编写，来源与署名见 UPSTREAM。`README.md:69` 写 MIT，见 LICENSE。
- `UPSTREAM.md:3-9`：设计上参考看板类工具，声明未复制上游代码；`source_url` 为 kanboard，`license: MIT`，`attribution: Copyright (c) Frédéric Guillot`。
- `NOTES.md:7` 的署名句子与 `UPSTREAM.md:9` 相同。
- 抽查 `app.py` 与 `static/index.html`：FastAPI + SQLite + 一段原生页面脚本，没有 Kanboard 的 PHP 源码。与「独立编写」不冲突。本仓库用自己的版权行，上游署名放在 UPSTREAM，这种写法与「未复制代码、只记录参考来源」一致。

`NOTES.md:5-7` 里的 Kanboard 版本号、默认分支 commit、许可证原文，本次没有联网重抓，标为未核实。不改 `LICENSE` 与 `UPSTREAM`。

## 分级修复清单

### P0

无。依赖能装上，pytest 与 live_selftest 都通过，`python app.py` 能在 `127.0.0.1:8000` 起服务并返回首页 200。

### P1

无。抽查过的鉴权、级联删除、令牌哈希、超长密码拒绝、文档页关闭、安全响应头，都与代码和实测一致。默认口令、不强制改密、登录不限速是产品口径（`DECISIONS.md:23`、`DECISIONS.md:81`），默认只听本机，不升为 P1。

### P2

1. `requirements-dev.txt:2` 把 httpx 钉在 0.28.1，pytest 因此打出 StarletteDeprecationWarning。修法：维持钉死版本，不引入 httpx2。`DECISIONS.md:68` 已决定不修，本次也没有依赖冲突。
2. `app.py:228` 登录不限速。修法：保持现状。默认绑定 `app.py:27` 的 `127.0.0.1`。
3. `app.py:209-225` 的 `current_user` 只校验令牌，不看 `must_change_password`。修法：保持只提示不拦截。`tests/test_app.py:30-33` 的登录夹具在未改密时就去调业务接口，改了会红，而且 `DECISIONS.md:23` 已定这个口径。
4. `app.py:293-312` 允许新密码与旧密码相同，并会把 `must_change_password` 清掉。修法：新旧相同则返回 400。提示本身不拦截业务，本轮不改。
5. `requirements.txt:1-2` 没有钉 starlette，README 写的 1.9.0 是本次解析结果。修法：不改版本号。当前已解析到 `starlette-1.9.0`。
6. `app.py:860` 的 `uvicorn.run` 使用默认 `server_header=True`，响应里有 `server: uvicorn`。修法：需要的话传 `server_header=False`。信息量很小，不改。
7. `app.py:658-675` 新建卡片用 `MAX(position)+1`，没有 `BEGIN IMMEDIATE`。修法：单用户本机暂不包事务。
8. `static/index.html:164` 改密文案没有 1024 上限。修法：标签改成「6–1024 位」。纯文案，不改。
9. `tests/live_selftest.py:14` 把自测端口写死为 8131。修法：测试文件禁止改，保持原样。
