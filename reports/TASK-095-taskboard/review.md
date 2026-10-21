# taskboard 验收

环境能装上，服务能在 `127.0.0.1:8000` 起来，测完已停。pytest **16 passed**（3.65s，另有 1 条弃用警告）。`tests/live_selftest.py` **16 个检查点全部 PASS**。P0 无，P1 无，仓库源码未改。

## 本地跑通记录

解释器是 Python 3.11.9，路径 `E:\muse-bridge\env\TASK-095-taskboard\Scripts\python.exe`。README 写的 `py -m venv` 在本机走不通：

    py -3 --version
    Unable to create process using 'E:\python.exe --version': ???????????

`py` 指向的 `E:\python.exe` 起不来。这是本机启动器问题。改用 `python -m venv E:\muse-bridge\in\TASK-095-taskboard\.venv`（exit 0）。未执行 `Activate.ps1`，后面的命令都调用 `.venv\Scripts\python.exe`（README 测试一节允许这种替换）。

    .venv\Scripts\python.exe -m pip install -r requirements.txt

解析到 fastapi 0.156.4、uvicorn 0.54.0、starlette 1.9.0。已安装包 METADATA：starlette 1.9.0 的 `Requires-Python: >=3.11`（`starlette-1.9.0.dist-info\METADATA` 第 26 行）。fastapi `Requires-Python: >=3.10`，uvicorn `>=3.10`。与 README 第 18 行一致。未升级 pip。

    .venv\Scripts\python.exe -m pip install -r requirements-dev.txt

新装 httpx 0.28.1、pytest 9.1.1。

    .venv\Scripts\python.exe -m pytest tests/ -q

    16 passed, 1 warning in 3.65s

警告原文：

    StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.

    .venv\Scripts\python.exe tests\live_selftest.py

    ALL 16 CHECKS PASSED

该脚本把真服务绑在 `127.0.0.1:8131`（`tests/live_selftest.py:14` 与 `:31`），结束时自己 `terminate()`。README 默认端口仍是 8000，两处不冲突。

按 README 再起一次 `app.py`，数据库放在 `E:\muse-bridge\work\TASK-095-taskboard\probe.db`：

    .venv\Scripts\python.exe E:\muse-bridge\work\TASK-095-taskboard\probe_server.py

日志：

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     127.0.0.1:49360 - "GET / HTTP/1.1" 200 OK

| 请求 | 状态 | 片段 |
| --- | --- | --- |
| `GET /` | 200 | `text/html; charset=utf-8`，标题 `taskboard · 项目看板` |
| `GET /health`、`/healthz`、`/api/health` | 404 | `{"detail":"Not Found"}` |
| `POST /api/login` `admin` / `admin123` | 200 | `must_change_password: True`，令牌已打码 |
| `GET /api/boards`、`GET /api/me` 无令牌 | 401 | `{"detail":"未登录"}` |
| `GET /docs`、`/redoc`、`/openapi.json` | 404 | `{"detail":"Not Found"}` |

README 没有健康检查路径，404 不记成缺陷。首页 200 且默认账号能登录。

安全头（首页与接口都有）：`X-Frame-Options: DENY`，`Content-Security-Policy: frame-ancestors 'none'`，`X-Content-Type-Options: nosniff`。`/api/` 另有 `Cache-Control: no-store`。

抽查（同一轮探测，库文件在 work 目录）：

- 登录口令 1025 位 → 400 `密码太长了`；1024 位错误口令 → 401（长度放行）。新密码 5 位 → 400 `新密码至少 6 位`；1025 位 → 400 `新密码太长了`。
- 删掉含已归档卡的列之后，`will-archive` 与 `active-card` 计数都是 0，孤儿卡 0，`cards` 表还在。
- 看板名 `a'; DROP TABLE cards;--` 按字面量入库。
- 直接往库里插入的另一用户看板：GET、DELETE、往其列加卡都是 404，看板列表里没有它。
- `sessions` 1 行；明文令牌不在库，SHA-256 在库。

进程由脚本 `terminate()`，打印 `SERVER_STOPPED 1`。之后 `netstat -ano -p tcp`：8000 只剩 TIME_WAIT，没有 LISTENING；8131 没有匹配行。

`node --check` 检查从 `static/index.html` 抽出的内联脚本，exit 0。没有浏览器，拖拽、到期颜色、确认框只对照了源码（`static/index.html:239-246`、`:293-302`、`:219`、`:347`），没有在页面上点过。

## README 与实际不符处

硬性不符（装不上、功能没有、数字对不上）没有。下面两条是文案精度，测试与接口行为仍和 README 的规则一致。

1. `README.md:9` 写「首次登录会提示修改密码」。`must_change_password` 在建用户时置 1（`app.py:184`），每次登录都返回（`app.py:255`），改密成功才清 0（`app.py:302`）。页面在每次登录成功（`static/index.html:156`）和持本地令牌进入（`static/index.html:412`）时，只要标志仍为真就 toast。第二次登录、还没改密，仍会提示，toast 文案仍写「首次登录」。

2. `README.md:9` 写「新密码需 6–1024 位」。后端在 `app.py:287-290`（上限常量 `app.py:34`）这样做，探测与这句话一致。页面改密框只写「至少 6 位」（`static/index.html:164`），没有 1024 上限。

以下逐项核对过，与代码一致，不列入不符：16 项 pytest（`tests/test_app.py` 中 16 个 `test_`，运行结果 `16 passed`）；16 个自测检查点；默认三列「待办 / 进行中 / 已完成」；8 色标签（`app.py:36` 与 `static/index.html:126` 同为 gray/red/orange/yellow/green/blue/purple/pink）；令牌 86400 秒（`app.py:24`）；环境变量默认值（`app.py:23-27`、`app.py:860`）；监听 `127.0.0.1:8000`（uvicorn 日志）；starlette 1.9.0 且 Python ≥3.11；匿名文档三件套关闭（`app.py:47-49`，探测 404）。`DECISIONS.md` 里出现的 14 项、15 项是当时的记录，当前 README 与当前用例都是 16。

## 许可证与署名核查

三份说明彼此一致，仓库里看不到互相打架的版权声明。

- `LICENSE:1-3`：MIT，`Copyright (c) 2026 taskboard contributors`。`README.md:69` 写「MIT，见 LICENSE」，指向的就是这份。
- `UPSTREAM.md:3-8`：设计参考 Kanboard，声明代码独立编写、未复制上游；`source_commit` 为 `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`；许可证 MIT；署名为 `Copyright (c) Frédéric Guillot`。
- `NOTES.md:5-7` 与 UPSTREAM 的 commit、MIT、版权行相同，并写版本 1.2.54。

上游 commit、Kanboard 的 LICENSE 原文、版本号 1.2.54：**未核实**。任务禁止抓取外部页面，没有访问 GitHub。

仓库内没有 PHP 文件，也没有 Kanboard 源码树。`app.py`、`static/index.html`、`tests/` 里没有上游版权头。这与「独立编写」这句相符，不能代替对上游仓库的核对。

依赖许可证来自本机已安装包的 METADATA，不是联网查询：fastapi 0.156.4 为 MIT，starlette 1.9.0 与 uvicorn 0.54.0 为 BSD-3-Clause。这些包不在仓库里，随 pip 安装，各自带 LICENSE 文件。本仓库 `LICENSE` 只覆盖 taskboard 自己的代码，与依赖的 BSD 声明可以同时成立。

`LICENSE` 与 `UPSTREAM.md` 未改。

## 分级修复清单

### P0

无。pytest 16 项通过，真服务自测 16 项通过，`app.py` 在 `127.0.0.1:8000` 返回首页 200。

### P1

无。未登录接口 401；文档与 OpenAPI 关闭；令牌只存哈希；删列/删看板后无孤儿卡；跨用户看板与列返回 404；口令长度限制在进 PBKDF2 之前。默认口令、不强制改密、登录不限速放在 P2：默认只听本机，且 `DECISIONS.md:23`、`:61`、`:80` 与现有测试把这个口径固定住了。

### P2

1. `requirements-dev.txt:2` 的 `httpx==0.28.1` 触发 Starlette 弃用警告。修法：维持钉死版本，不改。要消警告得换 httpx2，本次测试已通过。
2. `app.py:26` 与 `app.py:184` 使用默认口令 `admin123`，且不拦截未改密的业务请求。修法：维持。`tests/test_app.py` 全流程依赖该口令，`DECISIONS.md:23` 写明只提示不强制。
3. `app.py:228` 登录没有限速。修法：维持。`app.py:27` 默认 `127.0.0.1`，本次日志也是这个地址。
4. `static/index.html:164` 改密提示只有「至少 6 位」。修法：文案改成「6–1024 位」。后端已经按这个范围拒绝，见不符处第 2 条。
5. `static/index.html:156` 在标志未清时仍写「首次登录」。修法：改成「仍在使用初始密码」一类说法，或只在真正的第一次成功登录时提示。见不符处第 1 条。
6. `static/index.html:398` 归档日期取 `updated_at` 前 10 位，而 `app.py:74-75` 写入的是 UTC。修法：按本地日历日显示。东八区凌晨可能差一天。
7. `app.py:852` 的 `GET /` 不接受 HEAD，探测 `HEAD /` 为 405。修法：为首页补 HEAD。浏览器打开首页用的是 GET，已经 200。
8. `requirements.txt:1` 未钉死 starlette。本次全新安装解析到 1.9.0，与 README 一致。修法：可追加 `starlette==1.9.0`。没有冲突，本轮不动版本号。
9. `app.py:58` 的 CSP 只有 `frame-ancestors 'none'`。修法：维持。页面脚本是内联的（`static/index.html:124` 起），再收紧 `script-src` 会把页面自身的脚本拦住。
