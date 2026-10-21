# TASK-069-taskboard 执行记录

开工：2026-10-21。工作目录 `E:\muse-bridge\in\TASK-069-taskboard`。先审查再按清单修 P0/P1。

## 环境探测

命令：`python --version`

```
Python 3.11.9
```

命令：`git rev-parse --show-toplevel`

```
E:/muse-bridge/in/TASK-069-taskboard
```

命令：`git status --porcelain`

```
（无输出，工作区干净）
```

`.gitignore` 已忽略 `.venv/`、`data/`、`__pycache__/`、`.pytest_cache/`、`*.db`。临时库将放到 `E:\muse-bridge\work\TASK-069-taskboard`。

命令：`py -3 --version`（README Windows 步骤用的是 `py` 启动器）

```
exit: 1
Unable to create process using 'E:\python.exe --version': ???????????
```

本机 `py` 启动器指向不存在的 `E:\python.exe`，属环境限制。改用已可用的 `python`（3.11.9）创建虚拟环境。`.venv` 目录原先不存在。

## 安装运行依赖

命令：`python -m venv .venv`（退出码 0）

命令：`.venv\Scripts\python.exe -m pip install -r requirements.txt`（退出码 0）

```
Collecting fastapi==0.156.4
Collecting uvicorn==0.54.0
Collecting starlette>=0.46.0
  Using cached starlette-1.9.0-py3-none-any.whl
Successfully installed ... fastapi-0.156.4 ... starlette-1.9.0 ... uvicorn-0.54.0
```

解析到的 starlette 是 1.9.0，与 README 第 18 行一致。

本地包元数据 `starlette-1.9.0.dist-info/METADATA`：`Requires-Python: >=3.11`。与 README 第 18 行一致。

## 安装测试依赖

命令：`.venv\Scripts\python.exe -m pip install -r requirements-dev.txt`（退出码 0）

```
Successfully installed ... httpx-0.28.1 ... pytest-9.1.1
```

## 自动化测试

命令：`.venv\Scripts\python.exe -m pytest tests/ -q --tb=short -o cache_dir=E:\muse-bridge\work\TASK-069-taskboard\pytest_cache`

```
................                                                         [100%]
============================== warnings summary ===============================
.venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\in\TASK-069-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 2.97s
```

退出码 0。16 项全过。警告来自已安装的 starlette 1.9.0，不是断言失败。

## 真服务自测

命令：`.venv\Scripts\python.exe tests\live_selftest.py`（退出码 0）

```
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
```

自测脚本自己把服务绑在 127.0.0.1:8131，结束时 `proc.terminate()`。下面再按 README 用端口 8000 起一次。

## 按 README 起服务（端口 8000）

命令：工作目录脚本 `E:\muse-bridge\work\TASK-069-taskboard\serve.py`（设置 `TASKBOARD_DB_PATH` 到工作目录、`TASKBOARD_HOST=127.0.0.1`、`PORT=8000`，再以 `__main__` 跑 `app.py`）。

```
INFO:     Started server process [29604]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): 通常每个套接字地址(协议/网络地址/端口)只允许使用一次。
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
```

退出码 1。8000 已被占用。

命令：`netstat -ano | findstr :8000`

```
TCP    127.0.0.1:8000         0.0.0.0:0              LISTENING       33372
```

命令：`tasklist /FI "PID eq 33372" /V` → `python.exe` PID 33372。

命令：`Get-CimInstance Win32_Process -Filter "ProcessId=33372"` 的 CommandLine：

```
"C:\Users\xzm\AppData\Local\Programs\Python\Python311\python.exe" app.py
```

对 8000 发 GET（`probe_port.py`，标准库 urllib，不是 curl）：

```
GET / -> 200  title=freshfeeds · 清泉阅读
GET /health -> 404
GET /api/health -> 404
GET /api/me -> 401 {"detail":"未登录"}
GET /docs -> 404
GET /openapi.json -> 404
```

8000 上是另一个项目 freshfeeds，不是本仓库。未结束该进程。改用 README 允许的 `PORT=8099` 再起本仓库。

## 本仓库服务（PORT=8099，显式 TASKBOARD_HOST=127.0.0.1）

命令：`.venv\Scripts\python.exe E:\muse-bridge\work\TASK-069-taskboard\serve.py`

```
INFO:     Started server process [37428]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8099 (Press CTRL+C to quit)
```

首页与安全头（`probe_headers.py`，urllib，原始头）：

```
GET / -> 200
content-type: text/html; charset=utf-8
x-frame-options: DENY
content-security-policy: frame-ancestors 'none'
x-content-type-options: nosniff
body 含 <title>taskboard · 项目看板</title>
```

```
GET /api/me -> 401 {"detail":"未登录"}
cache-control: no-store
同上三枚安全头
```

```
GET /health -> 404 {"detail":"Not Found"}
GET /api/health -> 404
GET /docs -> 404
GET /redoc -> 404
GET /openapi.json -> 404
GET /app.py -> 404
```

`probe_app.py` 其他结果（令牌原文不贴）：

```
login SQL 注入用户名 -> 401 用户名或密码不正确
login admin/admin123 -> 200 must_change_password true
TOKEN_IN_DB_PLAIN False
TOKEN_HASH_IN_DB True
GET /api/me 已登录键只有 username, must_change_password
login 密码 1025 位 -> 400 密码太长了
删看板后 ORPHAN_COLS 0 ORPHAN_CARDS 0
第二用户读/删第一用户的看板、列、卡片、归档 -> 404；列表 -> []
第一用户自己的看板仍 200
```

访问日志只有方法、路径、状态码，没有口令和令牌。

用工具结束该进程后，`netstat -ano | findstr :8099` 无匹配（退出码 1）。

## 不设 TASKBOARD_HOST 的默认监听

命令：`serve_default_host.py`（只设 `PORT=8098` 和独立数据库，`os.environ.pop("TASKBOARD_HOST")`）。

```
INFO:     Uvicorn running on http://127.0.0.1:8098 (Press CTRL+C to quit)
```

`probe_8098.py`：`GET /` → `STATUS 200`，`CT text/html; charset=utf-8`，`XFO DENY`。

随后结束该进程。`netstat -ano | findstr :8098` 无匹配（退出码 1）。

## 审查后的全量重跑（未改源码）

命令：`.venv\Scripts\python.exe -m pytest tests/ -q --tb=short -o cache_dir=E:\muse-bridge\work\TASK-069-taskboard\pytest_cache ; .venv\Scripts\python.exe tests\live_selftest.py`

pytest：

```
16 passed, 1 warning in 3.08s
```

警告仍是 `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`

live_selftest 退出码 0（与 pytest 同一条命令链，整条退出码 0）：

```
ALL 16 CHECKS PASSED
```

## git status

命令：`git status --porcelain`

退出码 0，无输出。仓库源码未改，`.venv/` 与缓存被 `.gitignore` 忽略。

