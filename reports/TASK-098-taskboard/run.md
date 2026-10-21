# TASK-098-taskboard 执行记录

开工时间：2026-10-22。执行方：Grok Build。工作目录：E:\muse-bridge\in\TASK-098-taskboard。临时目录：E:\muse-bridge\work\TASK-098-taskboard。

## 0. 环境探针

命令：

```
python --version
```

输出：

```
Python 3.11.9
```

命令：

```
py -3 --version
```

输出（退出码 1）：

```
Unable to create process using 'E:\python.exe --version': ???????????
```

本机 `py` 启动器指向不存在的 `E:\python.exe`，无法按 README Windows 段第一步 `py -m venv .venv` 执行。改用已可用的 `python`（3.11.9，满足 README「Python ≥3.11」）。此为环境限制，先不记成项目缺陷。

命令：

```
git status --porcelain
git rev-parse --abbrev-ref HEAD
```

输出：工作区干净（porcelain 空），分支 `main`。`.gitignore` 已忽略 `.venv/`、`data/`、`__pycache__/`、`*.pyc`、`.pytest_cache/`、`*.db`、`*.sqlite`、`*.sqlite3`、`.env`。

## 1. 创建虚拟环境

命令：

```
New-Item -ItemType Directory -Force -Path E:\muse-bridge\work\TASK-098-taskboard
Set-Location E:\muse-bridge\in\TASK-098-taskboard
python -m venv .venv
.venv\Scripts\python.exe -m pip --version
```

输出（退出码 0）：

```
pip 24.0 from E:\muse-bridge\in\TASK-098-taskboard\.venv\Lib\site-packages\pip (python 3.11)
```

## 2. 安装依赖

命令：

```
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

退出码 0。关键输出：

```
Collecting fastapi==0.156.4
Collecting uvicorn==0.54.0
Collecting starlette>=0.46.0
  Using cached starlette-1.9.0-py3-none-any.whl.metadata (6.6 kB)
Successfully installed annotated-doc-0.0.5 annotated-types-0.8.0 anyio-4.15.1 click-8.5.0 fastapi-0.156.4 h11-0.16.0 idna-3.20 opentelemetry-api-1.45.1 pydantic-2.14.1 pydantic-core-2.50.1 starlette-1.9.0 typing-extensions-4.16.0 typing-inspection-0.4.4 uvicorn-0.54.0
```

解析到的 starlette 是 1.9.0，与 README 第 18 行一致。未执行 pip 自带的升级提示。

命令：

```
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

退出码 0。关键输出：

```
Successfully installed certifi-2026.10.19 colorama-0.4.6 httpcore-1.0.9 httpx-0.28.1 iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0 pytest-9.1.1
```

fastapi 0.156.4 与 uvicorn 0.54.0 已满足，未重装。

## 3. 自动化测试 pytest

为把测试库和 pytest 缓存留在工作目录，没有直接改仓库。命令：

```
.venv\Scripts\python.exe E:\muse-bridge\work\TASK-098-taskboard\run_pytest.py
```

脚本先把 TEMP/TMP 设为 `E:\muse-bridge\work\TASK-098-taskboard`，再 `pytest.main(["tests/", "-q", "-o", "cache_dir=...\\pytest_cache", "--basetemp", "...\\pytest-basetemp"])`。等价于 README 的 `python -m pytest tests/ -q`。

输出（退出码 0）：

```
................                                                         [100%]
============================== warnings summary ===============================
.venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\in\TASK-098-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 3.66s
```

starlette 1.9.0 的 METADATA 第 26 行：`Requires-Python: >=3.11`。与 README 第 18 行一致。

副作用：pytest 在仓库里写了 `__pycache__`（`app.cpython-311.pyc`、`tests/test_app.cpython-311-pytest-9.1.1.pyc`）。`.gitignore` 已忽略。后续 Python 进程加 `-B`，避免再写字节码。未删除这些文件（任务禁止 `del`/`rm`）。

## 4. 真服务自测 live_selftest

命令：

```
.venv\Scripts\python.exe -B E:\muse-bridge\work\TASK-098-taskboard\run_live.py
```

脚本把 TEMP/TMP 指到工作目录后，以 `__main__` 执行 `tests/live_selftest.py`（其内部 `PORT=8131`，起真 uvicorn，跑完 `proc.terminate()`）。

输出（退出码 0）：

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

16 个检查点与 README 第 55 行一致。登录打印里的 token 为 `<redacted>`。

## 5. 按 README 起服务（默认端口）并做首页/健康检查

数据库放到工作目录，避免在仓库里生成 `data/taskboard.db`。未设置 `PORT` / `TASKBOARD_HOST`，用来核对默认值。

命令：

```
.venv\Scripts\python.exe -B E:\muse-bridge\work\TASK-098-taskboard\probe_server.py
```

先单独导入时的默认值（退出码 0）：

```
DEFAULTS
E:\muse-bridge\in\TASK-098-taskboard\data\taskboard.db
'127.0.0.1'
86400
```

服务日志：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:53872 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:59180 - "GET /health HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:59183 - "GET /docs HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:59184 - "GET /redoc HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:59185 - "GET /openapi.json HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:59186 - "GET /api/me HTTP/1.1" 401 Unauthorized
INFO:     127.0.0.1:59188 - "POST /api/login HTTP/1.1" 200 OK
```

探针摘要（退出码 0）。登录响应里有明文令牌，这里不贴令牌：

```
UP True poll=None
GET / status=200 body=<!DOCTYPE html> ... <title>taskboard · 项目看板</title> ...
GET /health status=404 body={"detail":"Not Found"}
GET /healthz status=404 body={"detail":"Not Found"}
GET /api/health status=404 body={"detail":"Not Found"}
GET /api/me status=401 body={"detail":"未登录"}
GET /api/boards status=401 body={"detail":"未登录"}
AFTER_DELETE_COLUMN cards=0 deleted_col_rows=0
DELETE board status=200 body={"ok":true}
AFTER_DELETE_BOARD boards=0 cols=0 cards=0
SESSION_ROWS 1 token_lens=[64]
TOKEN_IN_DB False
STOPPED poll=1
```

第一次用 `dict(resp.headers)` 对响应头做大小写敏感查找，安全头被漏记。随即用 `list(resp.headers.items())` 重测。

命令：

```
.venv\Scripts\python.exe -B E:\muse-bridge\work\TASK-098-taskboard\probe_headers.py
```

输出（退出码 0，未打印令牌）：

```
GET / 200
[('content-type', 'text/html; charset=utf-8'), ... ('x-frame-options', 'DENY'), ('content-security-policy', "frame-ancestors 'none'"), ('x-content-type-options', 'nosniff'), ...]
GET /api/me 401
[..., ('x-frame-options', 'DENY'), ('content-security-policy', "frame-ancestors 'none'"), ('x-content-type-options', 'nosniff'), ('cache-control', 'no-store'), ...]
LOGIN 200 must_change True
GET /api/me 200
[..., ('cache-control', 'no-store'), ...]
STOPPED 1
```

访问日志里没有密码，也没有令牌。

## 6. 确认服务已退出

命令：

```
.venv\Scripts\python.exe -B E:\muse-bridge\work\TASK-098-taskboard\probe_shutdown.py
.venv\Scripts\python.exe -B E:\muse-bridge\work\TASK-098-taskboard\probe_ports.py
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Select-Object ProcessId, CommandLine
```

输出：

```
LOCAL 2026-10-22T01:34:59.448512+08:00
TZ 中国标准时间
DATA_DIR False
DB_FILE False
PORT 8000 CLOSED TimeoutError errno=None timed out
PORT 8131 CLOSED TimeoutError errno=None timed out
```

进程列表里没有 `app.py`。仍在跑的 python 是协调进程，与本次服务无关，没有动它们。8000/8131 阻塞连接 2 秒超时、没有连上；本机对关闭端口不立刻返回「连接被拒绝」。结合子进程 `poll=1` 和进程列表，服务已经关掉。

`git status --porcelain` 此时为空（还没改跟踪文件）。pytest 早先在仓库留下被 `.gitignore` 忽略的 `__pycache__`。任务禁止 `del`/`rm`，这些字节码还在。

## 7. 审查后的全量重跑

未改源码。重跑是为了把结果写进 fix-report.md。

命令：

```
.venv\Scripts\python.exe -B E:\muse-bridge\work\TASK-098-taskboard\run_pytest.py
```

输出（退出码 0）：

```
................                                                         [100%]
============================== warnings summary ===============================
.venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\in\TASK-098-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 2.70s
```

命令：

```
.venv\Scripts\python.exe -B E:\muse-bridge\work\TASK-098-taskboard\run_live.py
```

输出（退出码 0）：

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {'token': '<redacted>', 'username': 'admin', 'must_change_password': True}
PASS 首次登录提示改密
PASS 建看板成功
PASS 自带三列 待办/进行中/已完成 | ['待办', '进行中', '已完成']
PASS 加一列成功
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

失败项：无。弃用警告仍在，见 review.md 的 P2-3。

## 8. 收尾 git status

命令：

```
git status --porcelain
```

输出：空（退出码 0）。未改跟踪文件。说明见 fix-report.md 末尾。
