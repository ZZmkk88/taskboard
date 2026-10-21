# TASK-095-taskboard 执行记录

开工：2026-10-22。工作目录 `E:\muse-bridge\in\TASK-095-taskboard`。先审查再修 P0/P1。

## 1. 环境探测

命令：

    py -3 --version

输出（exit 1）：

    Unable to create process using 'E:\python.exe --version': ???????????

`py` 启动器指向的 `E:\python.exe` 无法启动（问号是控制台编码显示不出的系统错误）。这是本机环境问题，不是仓库代码错误。

命令：

    python --version
    python -c "import sys; print(sys.executable); print(sys.version)"

输出：

    Python 3.11.9
    E:\muse-bridge\env\TASK-095-taskboard\Scripts\python.exe
    3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)]

命令：

    python -m pip list

已安装且与 requirements.txt 一致：fastapi 0.156.4、uvicorn 0.54.0、starlette 1.9.0、pydantic 2.14.1。尚未安装 pytest、httpx（在 requirements-dev.txt）。

`.gitignore` 已忽略 `.venv/`、`data/`、`*.db`。下一步在仓库内用 `python -m venv .venv`（README 写的是 `py -m venv`，本机 py 不可用）并安装依赖。

## 2. 安装依赖

命令（exit 0）：

    python -m venv E:\muse-bridge\in\TASK-095-taskboard\.venv

命令（exit 0）：

    .venv\Scripts\python.exe -m pip install -r requirements.txt

解析结果与 README 所述一致：fastapi 0.156.4、uvicorn 0.54.0，传递依赖 starlette 1.9.0（Requires-Python: >=3.11，见已安装 METADATA）。未升级 pip（提示 24.0 -> 26.2.2，忽略）。

命令（exit 0）：

    .venv\Scripts\python.exe -m pip install -r requirements-dev.txt

新装：httpx 0.28.1、pytest 9.1.1，以及 httpcore 1.0.9、certifi 2026.10.19 等传递依赖。

## 3. 全量 pytest

命令（在仓库根目录，exit 0，耗时 3.65s）：

    .venv\Scripts\python.exe -m pytest tests/ -q

输出：

    ................                                                         [100%]
    ============================== warnings summary ===============================
    .venv\Lib\site-packages\fastapi\testclient.py:1
      E:\muse-bridge\in\TASK-095-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
        from starlette.testclient import TestClient as TestClient  # noqa

    -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
    16 passed, 1 warning in 3.65s

16 项全部通过，与 README 写的「16 项」一致。警告来自 starlette 对 httpx 的弃用提示，测试未失败。

## 4. 真服务自测（tests/live_selftest.py，端口 8131）

命令（仓库根目录，exit 0）：

    .venv\Scripts\python.exe tests\live_selftest.py

输出：

    PASS 首页能打开且是 taskboard 页面
    PASS 默认账号登录成功 | {'token': '<redacted>', 'username': 'admin', 'must_change_password': True}
    PASS 首次登录提示改密
    PASS 建看板成功 | {"id":1,"name":"自测看板",...}
    PASS 自带三列 待办/进行中/已完成 | ['待办', '进行中', '已完成']
    PASS 加一列成功 | {"id":4,"title":"待评审","position":3}
    PASS 连建三张卡成功
    PASS 卡片移到进行中
    PASS 卡片移到已完成
    PASS 列内排序：约访谈提到最前
    PASS 待办顺序正确 | ['约访谈', '买咖啡豆']
    PASS 归档买咖啡豆
    PASS 归档箱里有 1 张且记着原列
    PASS 恢复归档卡
    PASS 恢复后回到待办末尾 | ['约访谈', '买咖啡豆']
    PASS 看板改名

    ALL 16 CHECKS PASSED

脚本自己起 uvicorn 并在结束时 terminate。16 个检查点与 README 一致。数据库在系统临时目录（脚本内 tempfile），未写入仓库。

## 5. 按 README 起服务（端口 8000）并探测

数据库放到 `E:\muse-bridge\work\TASK-095-taskboard\probe.db`，避免在仓库里生成 `data\taskboard.db`。

命令（exit 0）：

    .venv\Scripts\python.exe E:\muse-bridge\work\TASK-095-taskboard\probe_server.py

服务日志片段（`work\TASK-095-taskboard\server.log`）：

    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     127.0.0.1:49360 - "GET / HTTP/1.1" 200 OK

首页与健康检查：

    GET /            200  text/html; charset=utf-8  正文含 <title>taskboard · 项目看板</title>
    GET /health      404  {"detail":"Not Found"}
    GET /healthz     404  {"detail":"Not Found"}
    GET /api/health  404  {"detail":"Not Found"}

README 没有健康检查路径。首页 200、默认账号登录 200。

同时记录：`/docs` `/redoc` `/openapi.json` `/app.py` 均为 404。未登录 `GET /api/boards`、`GET /api/me` 为 401 `{"detail":"未登录"}`。登录 1025 位口令 400 `密码太长了`；1024 位错误口令 401（按长度放行后再校验）。新密码 5 位 400 `新密码至少 6 位`；1025 位 400 `新密码太长了`。响应头含 `X-Frame-Options: DENY`、`Content-Security-Policy: frame-ancestors 'none'`、`X-Content-Type-Options: nosniff`；`/api/` 另有 `Cache-Control: no-store`。

数据抽查：删列后标题 `will-archive` 与 `active-card` 计数均为 0，孤儿卡 0，`cards` 表仍在。看板名 `a'; DROP TABLE cards;--` 按字面量保存。另一用户的看板 GET/DELETE/加卡均为 404，列表中没有该看板。会话 1 条，明文令牌不在库，SHA-256 在库。

脚本对子进程 `terminate()`，打印 `SERVER_STOPPED 1`（Windows 上结束进程的退出码）。随后 `netstat -ano -p tcp`：8000 只有 TIME_WAIT，没有 LISTENING；8131 无匹配行。服务已停。

## 6. 内联脚本语法

命令（exit 0，无输出）：

    node --check E:\muse-bridge\work\TASK-095-taskboard\index.script.js

脚本由 `static\index.html` 的内联 `<script>` 抽出。没有浏览器工具，未做点击、拖拽、弹窗的页面操作。

## 7. 收尾重跑

命令：

    .venv\Scripts\python.exe E:\muse-bridge\work\TASK-095-taskboard\rerun_tests.py

该脚本把 TEMP/TMP 指到 `E:\muse-bridge\work\TASK-095-taskboard` 后重跑 pytest 与 live_selftest。

    16 passed, 1 warning in 3.55s
    ALL 16 CHECKS PASSED
    PYTEST_EXIT 0 seconds 4.76
    LIVE_EXIT 0 seconds 2.46

警告仍是 StarletteDeprecationWarning（httpx / httpx2）。

命令（exit 0，无输出行）：

    git status --porcelain
