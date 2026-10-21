# TASK-090-taskboard 执行记录

开工时间：2026-10-22。工作目录 `E:\muse-bridge\in\TASK-090-taskboard`。先审查再修 P0/P1。

## 环境

本机 `python --version` → `Python 3.11.9`（exit 0）。
本机 `py --version` → exit 1：`Unable to create process using 'E:\python.exe --version'`。README 写的 `py -m venv` 在本机启动器坏了，改用 `python`。这是本机环境限制，不计入项目缺陷。

虚拟环境不放进仓库，放在工作目录：

```
python -m venv E:\muse-bridge\work\TASK-090-taskboard\venv
```

exit 0。

## 装依赖

```
E:\muse-bridge\work\TASK-090-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-090-taskboard\requirements-dev.txt
```

exit 0。关键行：

```
Successfully installed ... fastapi-0.156.4 ... httpx-0.28.1 ... pytest-9.1.1 ... starlette-1.9.0 ... uvicorn-0.54.0
```

传递依赖实际解析到 starlette 1.9.0，与 README 第 18 行「starlette 1.9.0」一致。
已装包 `starlette-1.9.0.dist-info/METADATA` 第 26 行：`Requires-Python: >=3.11`。fastapi 的 METADATA 第 39 行是 `Requires-Python: >=3.10`，更严的是 starlette。

## 跑测试

临时目录指到工作目录，避免写系统 TEMP。实际命令：

```
E:\muse-bridge\work\TASK-090-taskboard\venv\Scripts\python.exe -m pytest tests/ -q -p no:cacheprovider
```

工作目录 `E:\muse-bridge\in\TASK-090-taskboard`。exit 0。输出：

```
................                                                         [100%]
============================== warnings summary ===============================
..\..\work\TASK-090-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-090-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 2.91s
```

16 项全过，与 README 第 54 行一致。警告来自 starlette 对 httpx 的弃用提示，测试本身没有失败。

## 真服务自测

```
E:\muse-bridge\work\TASK-090-taskboard\venv\Scripts\python.exe E:\muse-bridge\in\TASK-090-taskboard\tests\live_selftest.py
```

工作目录同上，TEMP/TMP 指到工作目录。exit 0。脚本固定端口 8131。输出末尾：

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {'token': '<redacted>', 'username': 'admin', 'must_change_password': True}
...
PASS 看板改名

ALL 16 CHECKS PASSED
```

16 个检查点全过，与 README 第 55 行一致。自测脚本在 `finally` 里 `proc.terminate()`，进程已退出（exit 0）。

中间有一次验收脚本自己写错：用仓库外的 `pytest.main()` 调用，当前目录没进模块搜索路径，收集测试时报 `ModuleNotFoundError: No module named 'app'`。这不是项目缺陷。改成 README 的 `python -m pytest tests/ -q` 后通过。

## 起服务（README 默认端口）

数据库放到工作目录，避免在仓库里生成 `data/taskboard.db`。命令等价于在仓库目录执行 `python app.py`，并设置：

- `TASKBOARD_DB_PATH=E:\muse-bridge\work\TASK-090-taskboard\probe.db`
- `PORT=8000`
- 不设置 `TASKBOARD_HOST`（走代码默认）

uvicorn 日志原文：

```
INFO:     Started server process [26208]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:53015 - "GET / HTTP/1.1" 200 OK
```

首页：`GET /` → 200，`content-type: text/html; charset=utf-8`，正文含 `taskboard`，长度 23444。响应头：`X-Frame-Options: DENY`，`Content-Security-Policy: frame-ancestors 'none'`，`X-Content-Type-Options: nosniff`，`server: uvicorn`。

健康检查：README 没有健康检查路径。实测：

```
GET /health → 404 {"detail":"Not Found"}
GET /api/health → 404 {"detail":"Not Found"}
GET /healthz → 404 {"detail":"Not Found"}
```

不把「没有 /health」算成故障。

顺手核对（同一进程，查完即停）：

- `GET /docs`、`/redoc`、`/openapi.json` → 404
- `GET /app.py`、`/static/index.html`、`/.git/config` → 404
- 未登录 `GET /api/boards` → 401，`Cache-Control: no-store`，正文 `{"detail":"未登录"}`
- `admin` / `admin123` 登录 → 200，`must_change_password=true`，响应字段只有 token、username、must_change_password
- 另一用户读/改/删别人的看板或卡片 → 404
- 删看板后 SQLite 里 boards/columns/cards 计数均为 0（外键级联生效）
- sessions.token 长度为 64，不是明文令牌
- 1025 位密码 → 400 `{"detail":"密码太长了"}`

停止方式：对启动该进程的 `Popen` 调用 `terminate()`（未使用 taskkill）。停止后再次 `GET /` 连接超时，端口已不再接受连接。完整探针输出在 `E:\muse-bridge\work\TASK-090-taskboard\server-8000.log`。

## 收尾重跑

审查结论是 P0/P1 为零，未改仓库源码。按要求重跑全量测试。

pytest（exit 0，耗时取自 pytest 自己的结果行）：

```
................                                                         [100%]
16 passed, 1 warning in 2.69s
```

警告原文仍是 `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`

live_selftest（exit 0）：

```
ALL 16 CHECKS PASSED
```

`git status --porcelain` 无输出，exit 0。
