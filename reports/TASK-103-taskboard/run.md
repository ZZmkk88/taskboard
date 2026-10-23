# TASK-103-taskboard 执行记录

开工：2026-10-23。工作目录 `E:\muse-bridge\in\TASK-103-taskboard`。先审查再按清单修 P0/P1（最多 5 项）。

## 环境探测

命令：`python -V`

```
Python 3.11.9
```

命令：`py -3 -V`（README Windows 段要求的启动器）

```
exit: 1
Unable to create process using 'E:\python.exe -V': ???????????
```

命令：`py -m venv E:\muse-bridge\work\TASK-103-taskboard\.venv-py-try`

```
exit: 1
Unable to create process using 'E:\python.exe -m venv E:\muse-bridge\work\TASK-103-taskboard\.venv-py-try': ???????????
```

结论：本机 `py` 启动器指向不存在的 `E:\python.exe`，无法按 README 的 `py -m venv` 建环境。`python` 本身是 3.11.9，满足 README「Python 3.11 以上」。虚拟环境改用 `python -m venv` 建在 `E:\muse-bridge\work\TASK-103-taskboard\.venv`（避免把依赖装进待审仓库；`.gitignore` 虽忽略 `.venv/`，临时库仍放工作目录）。

命令：`git status --porcelain`（开工时，仓库根目录）

```
（空，exit 0）
```

`git rev-parse --is-inside-work-tree` → `true`。

## 安装依赖

命令：`E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-103-taskboard\requirements.txt`

```
exit: 0
Successfully installed annotated-doc-0.0.5 annotated-types-0.8.0 anyio-4.15.1 click-8.5.0 fastapi-0.156.4 h11-0.16.0 idna-3.20 opentelemetry-api-1.45.1 pydantic-2.14.1 pydantic-core-2.50.1 starlette-1.9.0 typing-extensions-4.16.0 typing-inspection-0.4.4 uvicorn-0.54.0
```

传递依赖 `starlette-1.9.0` 与 README 第 18 行写法一致。pip 提示可升级 24.0 → 26.2.2，未升级（任务不要求）。

命令：`E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-103-taskboard\requirements-dev.txt`

```
exit: 0
Successfully installed certifi-2026.10.23 colorama-0.4.6 httpcore-1.0.9 httpx-0.28.1 iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0 pytest-9.1.1
```

fastapi/uvicorn 已满足，未重装。

## 自动化测试

工作目录 `E:\muse-bridge\in\TASK-103-taskboard`。`TEMP`/`TMP` 指到 `E:\muse-bridge\work\TASK-103-taskboard`，避免测试库进系统临时目录。`PYTHONDONTWRITEBYTECODE=1`。pytest 缓存目录设到工作目录。

命令：

```
E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe -m pytest tests/ -q -o cache_dir=E:\muse-bridge\work\TASK-103-taskboard\pytest-cache
```

```
exit: 0
...................                                                      [100%]
============================== warnings summary ===============================
..\..\work\TASK-103-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-103-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
19 passed, 1 warning in 6.79s
```

19 项全过。1 条警告来自依赖 `fastapi/testclient.py`，不是本仓库测试失败。

## 真服务自测

命令（仓库根目录）：

```
E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe tests/live_selftest.py
```

```
exit: 0
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

自测脚本自己起 8131 端口并在结束时 terminate。README 默认端口 8000 的启动核对见下一节。

## starlette 版本核对（本地已安装包，未访问网页）

`E:\muse-bridge\work\TASK-103-taskboard\.venv\Lib\site-packages\starlette-1.9.0.dist-info\METADATA` 第 26 行：`Requires-Python: >=3.11`。与 README 第 18 行一致。

## 按 README 启动服务并检查首页 / 健康检查

探测开始时 `127.0.0.1:8000` 已被占用。`GET /` 返回的是另一个本机服务，不是本仓库：

```
port_8000_open_before True
port_8000_existing 200 server=uvicorn title=weblens · 网站访问统计
```

未使用 taskkill。接着按 README 不设 PORT 启动本仓库 `app.py`（数据库改到工作目录 `E:\muse-bridge\work\TASK-103-taskboard\tb-home.db`）。子进程日志：

```
INFO:     Started server process [34476]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

2.5 秒时进程仍在（`poll=None`）。随后只 `terminate` 了这个子进程，`try8000_exit 1`（Windows 上 terminate 的退出码）。关掉后 `127.0.0.1:8000` 连接被拒绝（WinError 10061）。完整 HTTP 断言放在空闲端口 18765，避免和探测开始时已在 8000 上的进程缠在一起。

命令：`E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe E:\muse-bridge\work\TASK-103-taskboard\probe_server.py`

18765 启动约 1.81 秒后首页 200。监听行：

```
TCP    127.0.0.1:18765        0.0.0.0:0              LISTENING       17536
```

只绑在 `127.0.0.1`，不是 `0.0.0.0`。

```
GET / -> 200 content-type=text/html; charset=utf-8
  x-frame-options=DENY
  content-security-policy=frame-ancestors 'none'
  x-content-type-options=nosniff
  has_taskboard True
  has_admin123 False
  title taskboard · 项目看板
GET /health -> 404
GET /api/health -> 404
GET /docs -> 404
GET /redoc -> 404
GET /openapi.json -> 404
GET /api/me -> 401
GET /api/boards -> 401
GET /static/index.html -> 404
GET /app.py -> 404
login 200 must_change_password=True token 已打码
bad_password 401 {"detail":"用户名或密码不正确"}
missing_user 401 {"detail":"用户名或密码不正确"}
sqli_login 401 {"detail":"用户名或密码不正确"}
pw_1025 400 {"detail":"密码太长了"}
me 200 cache-control=no-store
boards 200 []
stored_equals_plaintext False
stored_equals_sha256 True
ttl_seconds 86399.7
hash_as_bearer 401 {"detail":"登录已过期，请重新登录"}
create_board 200 name=验收看板 column_count=3
```

`/health` 与 `/api/health` 为 404。README 没有健康检查路径，不记为缺陷。首页 `/` 即 README 写的入口。

关掉 18765 后：`shutdown_exit 1`，`port_alt_open_after False`，`port_8000_still_open False`。

默认数据库路径（只 import、未 init，未在仓库里建库）：

```
DB_PATH=E:\muse-bridge\in\TASK-103-taskboard\data\taskboard.db
HOST=127.0.0.1
default-import exit 0
```

与 README 环境变量表一致：库文件在 app.py 同目录的 `data\taskboard.db`，监听默认 `127.0.0.1`。

## 额外核对（级联删除、跨用户、边界）

命令：`E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe E:\muse-bridge\work\TASK-103-taskboard\probe_logic.py`

数据库：`E:\muse-bridge\work\TASK-103-taskboard\logic.db`。下面不贴令牌原文。

```
archived_card_rows_after_column_delete 0
restore_gone 404 {"detail":"卡片不存在"}
card_rows_after_board_delete 0
column_rows_after_board_delete 0
password_plaintext_in_db False
bob_list 200 []
bob_get 404 {"detail":"看板不存在"}
bob_rename 404
bob_del 404
bob_card 404
bob_move 404
admin_still 200 看板名仍为「仅管理员」
leap_bad 400 {"detail":"截止日期不是有效日期"}
leap_ok 200 due_date=2028-02-29
name_101 400 {"detail":"看板名太长了"}
null_title 200 name=AB（空字节被去掉）
same_pw 400 {"detail":"新密码不能和旧密码相同"}
user_space 200（用户名会 strip）
pw_space 401（密码不去掉首尾空格）
color 400 {"detail":"标签颜色不在可选范围内"}
```

同一轮还有 StarletteDeprecationWarning（httpx / starlette.testclient），与 pytest 那条相同。

`git status --porcelain`（逻辑探针之后）：空，exit 0。

## 补一次默认端口 8000 的首页请求

探测结束时 8000 已空闲。命令：

```
E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe E:\muse-bridge\work\TASK-103-taskboard\probe_8000_http.py
```

未设置 `PORT` / `TASKBOARD_HOST`。数据库 `E:\muse-bridge\work\TASK-103-taskboard\tb-8000.db`。

```
open_before False
GET / 200 taskboard · 项目看板
ctype text/html; charset=utf-8
xfo DENY
GET /health 404 {"detail":"Not Found"}
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:57351 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:57351 - "GET /health HTTP/1.1" 404 Not Found
exit 1
open_after False
```

`exit 1` 是 terminate 子进程的退出码。端口随后关闭。

## 审查结论之后的全量重跑

无源码改动。重跑是为了把最终结果写进 fix-report。工作目录 `E:\muse-bridge\in\TASK-103-taskboard`。

命令：

```
E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe -m pytest tests/ -q -o cache_dir=E:\muse-bridge\work\TASK-103-taskboard\pytest-cache
```

```
...................                                                      [100%]
============================== warnings summary ===============================
..\..\work\TASK-103-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1
  StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
19 passed, 1 warning in 3.82s
exit: 0
```

命令：

```
E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe tests/live_selftest.py
```

```
ALL 16 CHECKS PASSED
exit: 0
```

16 行均为 `PASS`（首页、登录、改密提示、建看板、三列、加列、三张卡、两次跨列移动、列内排序、待办顺序、归档、归档箱原列、恢复、恢复后顺序、改名）。

命令：`git status --porcelain`（仓库根目录）

```
（无输出，exit 0）
```

仓库内没有 `data\` 目录（`NO_DATA_DIR`）。临时库在 `E:\muse-bridge\work\TASK-103-taskboard\`。

