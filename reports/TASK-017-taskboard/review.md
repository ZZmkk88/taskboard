# taskboard 验收报告

结论：依赖能装上，14 项 pytest 通过，16 个真服务检查点通过，首页在 8000 端口返回 200。没有 P0。有 5 条 P1，其中 4 条直接改，1 条改了会破坏现有测试，不改。

审查时的代码还没改。行号都对应当时的文件。

## 本地跑通记录

环境：Python 3.11.9。虚拟环境在 `E:\muse-bridge\work\TASK-017-taskboard\venv`，没有建在仓库里。

`py -3 --version` 失败，原文：

```
Unable to create process using 'E:\python.exe --version': ???????????
```

README 的 Windows 步骤写 `py -m venv`。这是本机启动器坏了，不是仓库缺陷。后面都用 `python`。

安装（约 33.56s，退出码 0）：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
```

```
Successfully installed ... fastapi-0.156.4 ... uvicorn-0.54.0 ... httpx-0.28.1 ... pytest-9.1.1 ...
```

pytest（退出码 0）：

```
14 passed, 3 warnings in 1.95s
```

警告原文要点：`app.py:159` `on_event is deprecated`；`starlette.testclient` `Using httpx with starlette.testclient is deprecated; install httpx2 instead`。测试没有失败。

服务：`Uvicorn running on http://0.0.0.0:8000`。`netstat`：

```
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       29548
```

首页：`GET /` 200，`content-type: text/html; charset=utf-8`，正文含 `taskboard` 和登录表单。

健康检查：仓库和 README 都没有健康检查路由。实测：

```
GET /health 404 {"detail":"Not Found"}
GET /healthz 404 {"detail":"Not Found"}
GET /api/health 404 {"detail":"Not Found"}
```

这不是「跑不起来」。未登录 `GET /api/me` 为 401 `{"detail":"未登录"}`。默认账号登录 200，`must_change_password=true`。

查完已关掉。`findstr LISTENING` 加 `:8000` 退出码 1。

真服务自测 `tests/live_selftest.py` 退出码 0，末行 `ALL 16 CHECKS PASSED`。8131 没有残留 LISTENING。

没有浏览器，拖拽、改密弹窗、删列确认框没有在页面上点过。接口用 httpx 打过。命令全文和更长的输出在 `run.md`。

## README 与实际不符处

1. README.md:3 写「不依赖任何外部服务」。app.py:36 `app = FastAPI(title="taskboard")` 打开了框架默认文档页。实测 `GET /docs`、`GET /redoc` 为 200，页面外链包括 `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js`、`https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js`、`https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700`。看板页 `static/index.html` 没有这些外链。

2. README.md:3 写本地运行，README.md:38 只让浏览器打开 `http://127.0.0.1:8000`。app.py:784 是 `host="0.0.0.0"`。启动日志是 `Uvicorn running on http://0.0.0.0:8000`，netstat 是 `0.0.0.0:8000 LISTENING`。文档没写监听全部网卡。

3. README.md:44 默认数据库写成 `data/taskboard.db`。app.py:22 是 `Path(__file__).resolve().parent / "data" / "taskboard.db"`，锚在脚本目录，不是进程当前工作目录。从别的目录启动时，文件不会出现在 cwd 下的 `data/`。

4. README.md:12 写截止日期「到期高亮、逾期红色警告」。static/index.html:236 用 `new Date().toISOString().slice(0,10)`，这是 UTC 日期。东八区 00:00–08:00，本地的「今天」会被算成前一天。README 没写按 UTC 比较。

5. README.md:7 写功能「均已实现并通过测试」。pytest 14 项和 live_selftest 16 项都过了，但拖拽放下（static/index.html:288）、到期高亮（static/index.html:236）、删列确认框（static/index.html:334）没有对应自动化测试。令牌 24 小时只在 app.py:23 写成 `24 * 60 * 60`，也没有测试去推进时钟。

下列说法和代码一致，不记为不符：默认账号 admin/admin123（README.md:9，app.py:24-25）、三列默认名（README.md:10，app.py:32）、端口 8000（README.md:47，app.py:784）、14 项测试（README.md:53，实测 `14 passed`）、16 个检查点（README.md:54，实测 `ALL 16 CHECKS PASSED`）、后续不做多用户/评论/附件（README.md:59-64，代码里没有这些路由）。

## 许可证与署名核查

内部是自洽的，没有改 LICENSE 和 UPSTREAM。

- README.md:67 写 MIT，并指向 LICENSE。LICENSE:1 是 `MIT License`，LICENSE:3 是 `Copyright (c) 2026 taskboard contributors`，正文是标准 MIT 许可条款。
- README.md:5 把来源指到 UPSTREAM.md。UPSTREAM.md:4 写代码独立编写、未复制上游。UPSTREAM.md:6-9 记录 kanboard 的 URL、commit `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`、MIT、`Copyright (c) Frédéric Guillot`。
- NOTES.md:4-7 与 UPSTREAM 的版本号 1.2.54、commit、版权行一致。

上游版本号、commit 是否真实存在、版权行是否逐字相同：本次禁止抓取外网页面，**未核实**。

仓库侧可以核对的部分：本仓库是 Python，NOTES.md:4 写上游是 PHP。表是 `users` / `sessions` / `boards` / `board_columns` / `cards`（app.py:105-143），不是 NOTES 里写的上游 `projects` / `tasks` / `swimlanes`。没有看到成段抄来的上游源码。在「未复制代码」这个前提下，项目 LICENSE 不收录 Frédéric Guillot，不构成署名遗漏。没有确凿的事实错误，所以不改 LICENSE 和 UPSTREAM。

## 分级修复清单

### P0

无。安装、pytest、真服务自测、首页都跑通了。

### P1

1. app.py:784 监听 `0.0.0.0`，加上默认口令 `admin` / `admin123`（app.py:24-25），同一局域网的人可以登录。修法：默认改绑 `127.0.0.1`，和 README 写的地址一致。
2. app.py:36 默认打开 `/docs` 和 `/redoc`，这两个页面在应用同源执行 jsDelivr 上的脚本，脚本能读 `localStorage` 里的登录令牌（static/index.html:127）。修法：关掉 `docs_url` 和 `redoc_url`。
3. 响应没有点击劫持防护。探针里 `X-Frame-Options` 为空，应用创建处 app.py:36 没有任何安全响应头。恶意网页可以套住已登录的 `http://127.0.0.1:8000` 诱导点击。修法：加中间件，设置 `X-Frame-Options: DENY` 和 `Content-Security-Policy: frame-ancestors 'none'`。
4. 删列会连带删掉该列已归档卡片，确认框却只数未归档的。探针：归档列表里有 1 张 `column_id=1` 的卡，`DELETE /api/columns/1` 之后归档列表变成 `[]`。后端是 app.py:551-552 删列加外键级联；确认文案在 static/index.html:334，用的是 `col.cards.length`，而 `col.cards` 只含未归档卡（app.py:346）。修法：删除前先取归档列表，确认文案写上该列归档卡的数量。
5. 改密不使其他会话失效。app.py:234-250 只更新 `users`，不删 `sessions`。探针：会话 A 改密成功后，会话 B 的 `GET /api/me` 仍是 200。修法本应删掉该用户除当前令牌以外的会话。不改，原因见下。

P1-5 不落地：`tests/test_app.py:79` 的 `auth` 夹具是模块级的。`tests/test_app.py:101-105` 用另一次登录得到的新令牌把密码改回去，后面的用例仍用最初那个令牌。撤销其他会话会让这些用例 401。不许改测试，所以这条只记录，不动代码。

### P2

1. app.py:159 `@app.on_event("startup")` 在 FastAPI 0.156.4 上启动即打印 DeprecationWarning。修法：改成 lifespan，在里面调用 `init_db()`。当前不影响启动。
2. app.py:205 用 `!=` 比较密码哈希；用户不存在时直接失败，不算哈希。修法：用户不存在时也做一次等长哈希，并用 `hmac.compare_digest`。
3. app.py:197 登录没有失败次数限制。修法：同一用户名连续失败后短暂拒绝。绑到本机之后风险主要在本机。
4. app.py:113-116 会话令牌明文落在 `sessions.token`。修法：库里只存令牌哈希，校验时比对哈希。拿到数据库文件的人本来就能改密码哈希，所以这是纵深防御。
5. app.py:655 删卡、app.py:711 归档、app.py:730 恢复都不调用 `_touch_board`，而 app.py:403 看板列表按 `updated_at` 排序。修法：这三处成功后更新所属看板的 `updated_at`。
6. static/index.html:236 到期判断用 UTC。修法：用本地日历日（年-月-日）和 `due_date` 比较。
7. static/index.html:156 首次登录只 toast，不拦住后续操作。README.md:9 写的是「提示」，和代码一致，所以不算不符。修法：`must_change_password` 为真时，除改密和登出外拒绝其他接口。这会碰到现有测试顺序，本次不改。
8. 测试客户端弃用警告来自已安装的 Starlette，不是业务代码。修法：等依赖升级到它要求的 httpx2。本次不改 requirements 里的版本号，测试是通过的。
