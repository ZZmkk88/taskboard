# taskboard 验收

能在本机跑通。pytest **19 passed**（3.82s，另有 1 条依赖弃用警告），真服务自测 **16/16 PASS**。不设 `PORT` 时进程日志为 `Uvicorn running on http://127.0.0.1:8000`，`GET /` 返回 **200**，标题 `taskboard · 项目看板`。`/health` 为 404，README 没有这条路径。

P0 无。P1 无。未改仓库源码。P2 见文末，按任务只修 P0/P1，这些不动。

## 本地跑通记录

环境：Python `3.11.9`（`python -V`）。虚拟环境放在 `E:\muse-bridge\work\TASK-103-taskboard\.venv`，避免往仓库里装包。依赖安装 exit 0，装上 `fastapi==0.156.4`、`uvicorn==0.54.0`、`starlette==1.9.0`、`httpx==0.28.1`、`pytest==9.1.1`。

本机 `py` 启动器不可用，这是环境问题，不是仓库缺陷。README 写的 Windows 第一步因此没走成，改用 `python -m venv` 后其余步骤按 README 做完。

```
py -3 -V
exit: 1
Unable to create process using 'E:\python.exe -V': ???????????

py -m venv E:\muse-bridge\work\TASK-103-taskboard\.venv-py-try
exit: 1
Unable to create process using 'E:\python.exe -m venv ...': ???????????
```

pytest（仓库根目录）：

```
E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe -m pytest tests/ -q -o cache_dir=E:\muse-bridge\work\TASK-103-taskboard\pytest-cache
19 passed, 1 warning in 6.79s
```

警告原文：`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.` 出处是已安装的 `fastapi/testclient.py:1`，不是本仓库断言失败。

真服务自测：

```
E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe tests/live_selftest.py
ALL 16 CHECKS PASSED
```

默认端口首页（库文件放在工作目录 `tb-8000.db`，未设 `PORT` / `TASKBOARD_HOST`）：

```
open_before False
GET / 200 taskboard · 项目看板
ctype text/html; charset=utf-8
xfo DENY
GET /health 404 {"detail":"Not Found"}
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:57351 - "GET / HTTP/1.1" 200 OK
exit 1
open_after False
```

`exit 1` 是关掉子进程时 terminate 的退出码。关掉后 8000 不再监听。

探测开始时 8000 上曾有另一个本机进程，`GET /` 的标题是 `weblens · 网站访问统计`。没有用 taskkill。稍后该端口空出来，本仓库自己的进程成功听在 `127.0.0.1:8000`。完整路由抽查是在空闲端口 18765 上做的，监听行 `TCP 127.0.0.1:18765 LISTENING`，只绑本机。抽查结果：`/` 200 且正文含 taskboard、不含 `admin123`；`/docs`、`/redoc`、`/openapi.json`、`/static/index.html`、`/app.py` 均为 404；未带令牌的 `/api/me`、`/api/boards` 为 401；登录 200 且 `must_change_password=true`；错误密码与不存在用户都是 401「用户名或密码不正确」；`' OR 1=1` 登录 401；1025 位密码 400；会话表里的 token 等于 SHA-256、不等于明文，TTL 约 86399.7 秒；拿库里的哈希当 Bearer 为 401；`/api/me` 的 `Cache-Control` 为 `no-store`。响应头有 `X-Frame-Options: DENY`、`Content-Security-Policy: frame-ancestors 'none'`、`X-Content-Type-Options: nosniff`。18765 关掉后端口关闭。

另一次探针（`probe_logic.py`，库在工作目录）：删列后归档卡行数为 0，恢复该卡 404；删看板后卡片行数 0、列行数 0；密码列不是明文 `admin123`。直接往库里插入第二个用户 bob 后，bob 的看板列表为 `[]`，读/改/删管理员看板、改/移管理员卡片均为 404，管理员自己的看板仍在。`2026-02-29` 为 400，`2028-02-29` 为 200。101 字看板名 400。标签颜色注入串 400。新旧密码相同 400。

前端拖拽、到期高亮、确认框没有浏览器点击记录（本环境没有浏览器工具）。代码在 `static/index.html:245-252`（到期样式）、`:217-221` 与 `:346-353`（确认框）、`:299-308`（整列投放）。接口级移动已由 live_selftest 走过。

只 import 时的默认值：`DB_PATH=E:\muse-bridge\in\TASK-103-taskboard\data\taskboard.db`，`HOST=127.0.0.1`。仓库里没有生成 `data\`。

命令全文在 `run.md`。

## README 与实际不符处

下面 3 条是口径偏宽或文档没写到的行为。功能清单里「能登录、三列、归档、16 个检查点、19 项测试全过、Python 3.11、starlette 1.9.0、默认端口 8000」与本次运行一致，不重复列。

1. `README.md:7` 与 `README.md:54` 把 19 项都写成「后端接口」测试。`tests/test_app.py:130-134` 的 `test_initial_password_validation` 直接调用 `app._validate_initial_password`，不发 HTTP。pytest 计数仍是 19 passed，数字没错，称呼偏宽。

2. `README.md:9` 写新密码 6–1024 位即可。`app.py:309-310` 在新旧密码相同时返回 400，详情是「新密码不能和旧密码相同」。本次探针 `same_pw 400`。

3. `README.md:12` 写卡片支持编辑，`README.md:14` 写归档后可恢复或彻底删除，没有写归档后的限制。`app.py:709-710` 对已归档卡片的 PUT 返回 400；`app.py:760-761` 对已归档卡片的移动返回 400。

`README.md:5` 用了复数「看板类工具」，`UPSTREAM.md:5-8` 只记录 Kanboard 一处来源。这是范围用词不同，不记成功能不符。

本机 `py` 启动器失败见上一节，不记成 README 与代码不符。

## 许可证与署名核查

仓库内部是自洽的，本次没有改 `LICENSE` 或 `UPSTREAM.md`。

- `LICENSE:1-3` 是 MIT，版权行 `Copyright (c) 2026 taskboard contributors`。许可、保留声明、免责三条都在，文本是常见 MIT 模板。
- `README.md:69` 写 MIT 并指向 `LICENSE`。`README.md:5` 写代码独立编写、来源见 `UPSTREAM.md`。
- `UPSTREAM.md:3-8` 写未复制上游代码，来源 `https://github.com/kanboard/kanboard`，commit `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`（40 位十六进制），许可证 MIT，署名 `Copyright (c) Frédéric Guillot`。
- `NOTES.md:5-7` 与 `UPSTREAM.md` 的仓库、commit、MIT、版权行一致，并写明该行是从上游 LICENSE 抄来的署名。
- 本仓库是 Python / FastAPI / SQLite 加一个静态页，树里没有 PHP 上游源码，和「未复制 Kanboard 代码、只记录设计参考」的说法相符。

未联网核对 commit 是否仍是 Kanboard 默认分支 HEAD，也未核对上游 LICENSE 文件原文（任务禁止抓取外部页面）。`NOTES.md:5` 的「最新版本 1.2.54」同样未核实。在仓库内部，LICENSE、README、UPSTREAM、NOTES 没有互相打架的事实声明，所以没有改这些文件。

## 分级修复清单

### P0

无。服务能起，测试能过。

### P1

无。核对过、未发现问题的点：

- 未登录访问 `/api/boards`、`/api/me` 为 401（`app.py:221-234`）。
- 第二个用户不能读写第一个用户的看板和卡片（探针 bob_* 均为 404）。归属查询在 `app.py:368-398`。
- 删列、删看板会连带删掉卡片行（探针行数为 0）。外键在 `app.py:170`、`app.py:176`，连接打开时 `app.py:118` 执行 `PRAGMA foreign_keys = ON`。
- 会话入库是 SHA-256（`app.py:285-287`），明文 Bearer 才能用。
- `/docs`、`/redoc`、`/openapi.json` 关闭（`app.py:46-51`），实测 404。
- 密码不是明文落库；1025 位登录口令 400（`app.py:241-243`）。
- 源码路径 `/app.py`、`/static/index.html` 不对外（只有 `app.py:868-870` 的 `/` 返回页面）。

### P2

每条都是「一句修法」。本次不改。

1. `README.md:7` 与 `README.md:54`：把「19 项后端接口测试」改成「19 项里 18 项走 HTTP，`tests/test_app.py:130` 测初始口令函数」。纯文案。
2. `README.md:9`：补上「新密码不能与旧密码相同」（对应 `app.py:309-310`）。纯文案。
3. `README.md:12` 与 `README.md:14`：补上已归档卡片不能改、不能移（对应 `app.py:709-710`、`app.py:760-761`）。纯文案。
4. `requirements-dev.txt:2` 的 `httpx==0.28.1` 触发 Starlette 弃用警告。消警告要换测试客户端依赖。现有钉死版本没有冲突，不改版本号。
5. `app.py:489` 的建看板以及其余业务接口不看 `must_change_password`。`static/index.html:156` 只 toast。`tests/live_selftest.py:60` 在未改密时就建看板。`DECISIONS.md:69` 记录了「只提示、不拦截」。若改成拦截，live_selftest 会失败，而测试文件不能改。不修。
6. `app.py:240` 登录没有失败次数限制。`DECISIONS.md:80` 已决定维持，默认只听 `127.0.0.1`（`app.py:28`）。不修。
7. `app.py:672-676` 新建卡片的 position 先读 MAX 再插入，并发时可能重号。`DECISIONS.md:101` 记为暂缓。单用户本机场景。不修。
8. `requirements.txt:1-2` 没有钉死 starlette。本次解析是 1.9.0，其 METADATA `Requires-Python: >=3.11`，与 `README.md:18` 一致。`DECISIONS.md:82` 决定本轮不动。不修。
9. `app.py:882` 的 `uvicorn.run` 使用默认 `server_header=True`（已安装 uvicorn 0.54.0 的 `main.py:532`）。响应里能看到 `server: uvicorn`。`DECISIONS.md:81` 认为信息不敏感。不修。
