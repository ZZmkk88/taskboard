# TASK-035-taskboard 执行记录

开工：2026-10-21。本地验收仓库 `E:\muse-bridge\in\TASK-035-taskboard`。以下按步骤追加真实命令与输出。

## 0. 环境探查

命令：

```
python --version
git rev-parse --is-inside-work-tree
git status --porcelain
```

输出：

```
Python 3.11.9
true
```

`git status --porcelain` 无输出，工作区干净。Python 3.11.9 满足 README 要求的 3.10 以上。

虚拟环境不放进待审仓库（仓库 `.gitignore` 虽忽略 `.venv/`，但任务要求临时文件写到工作目录）。解释器：`E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe`。

命令：

```
python -m venv E:\muse-bridge\work\TASK-035-taskboard\venv
```

输出：exit 0，无额外输出。

## 1. 安装运行依赖

命令（工作目录无关，用绝对路径）：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-035-taskboard\requirements.txt
```

输出片段（exit 0）：

```
Collecting fastapi==0.156.4
Collecting uvicorn==0.54.0
Successfully installed annotated-doc-0.0.5 annotated-types-0.8.0 anyio-4.15.1 click-8.5.0 fastapi-0.156.4 h11-0.16.0 idna-3.20 opentelemetry-api-1.45.1 pydantic-2.14.1 pydantic-core-2.50.1 starlette-1.9.0 typing-extensions-4.16.0 typing-inspection-0.4.4 uvicorn-0.54.0
```

钉死版本可安装，无依赖冲突。

## 2. 安装测试依赖

命令：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-035-taskboard\requirements-dev.txt
```

输出片段（exit 0）：

```
Collecting httpx==0.28.1
Collecting pytest==9.1.1
Successfully installed certifi-2026.10.19 colorama-0.4.6 httpcore-1.0.9 httpx-0.28.1 iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0 pytest-9.1.1
```

fastapi、uvicorn 已满足，未改版本号。

## 3. 全量 pytest

第一次启动方式不对（pytest.main 未把仓库根放进 `sys.path`），收集失败，不是项目缺陷。命令：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_pytest.py
```

当时脚本还没有 `os.chdir` 到仓库。输出原文：

```
ImportError while importing test module 'E:\muse-bridge\in\TASK-035-taskboard\tests\test_app.py'.
tests\test_app.py:12: in <module>
    import app as appmod  # noqa: E402
E   ModuleNotFoundError: No module named 'app'
ERROR tests/test_app.py
1 warning, 1 error in 0.24s
```

exit code 1。警告：`Unknown config option: cache_dir`（那次多传了无效 ini，已从脚本去掉）。

接着按 README，从仓库根跑 `python -m pytest tests/ -q`（脚本里 chdir 到仓库，TEMP/TMP 指到工作目录，`-p no:cacheprovider` 避免在仓库写 `.pytest_cache`）。

命令（脚本已改为 chdir 到仓库根）：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_pytest.py
```

输出（exit 0）：

```
...............                                                          [100%]
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
15 passed, 1 warning in 2.58s
```

README.md 写的是 14 项，实际收集并通过 15 项。

## 4. 真服务自测（README：`python tests/live_selftest.py`）

脚本 `E:\muse-bridge\work\TASK-035-taskboard\run_live.py` 把 TEMP/TMP 指到工作目录后，在仓库根执行 `tests/live_selftest.py`。该脚本自己把服务绑到 `127.0.0.1:8131`，结束时 `proc.terminate()`。

命令：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_live.py
```

输出（exit 0，令牌已截断；临时库随进程结束丢弃）：

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {"token":"gfwInXMm…(已截断)","username":"admin","must_change_password":true}
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

## 5. 按 README 起 8000 端口并关闭

数据库改到工作目录，避免在仓库里生成 `data/taskboard.db`。脚本：`E:\muse-bridge\work\TASK-035-taskboard\run_server_check.py`。关闭用 `proc.terminate()` / `proc.kill()`，没有调用 taskkill。

命令：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_server_check.py
```

输出片段（exit 0）：

```
startup_seconds=1.15 up=True
GET / status=200 ctype=text/html; charset=utf-8
  headers={'server': 'uvicorn', 'x-frame-options': 'DENY', 'content-security-policy': "frame-ancestors 'none'", 'x-content-type-options': 'nosniff'}
  body=<!DOCTYPE html> ... <title>taskboard · 项目看板</title> ...
GET /health status=404 body={"detail":"Not Found"}
GET /api/health status=404 body={"detail":"Not Found"}
GET /docs status=404 body={"detail":"Not Found"}
GET /redoc status=404 body={"detail":"Not Found"}
GET /openapi.json status=200 body={"openapi":"3.1.0","info":{"title":"taskboard","version":"0.1.0"},...}
GET /api/boards no auth status=401 body={"detail":"未登录"}
POST /api/login sqli-ish status=401 body={"detail":"用户名或密码不正确"}
POST /api/login default status=200 must_change=True token_len=43（令牌正文不写入本记录）
POST /api/boards odd name status=200 name 原样保存为 a'; DROP TABLE cards; --
POST card extra fields status=200 archived=False position=0（is_archived 与 position 被忽略）
DELETE board status=200
GET deleted board status=404
POST /api/logout status=200
GET /api/me after logout status=401 body={"detail":"登录已过期，请重新登录"}
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12700]
count users=1
count sessions=0
count boards=0
count board_columns=0
count cards=0
after_stop still_accepting=no (ConnectTimeout)
```

`foreign_keys_default_on_fresh_connection=0` 是检查脚本自己新开的 sqlite 连接没执行 `PRAGMA foreign_keys=ON`。应用连接在 `app.py` 里会打开该开关；上面 cards/columns 计数为 0，说明删看板时级联生效（若外键没开，列和卡会留下）。

关闭复查：

```
Get-Process -Id 12700
```

输出：找不到进程标识 12700（进程已退出）。

```
netstat -ano -p tcp | Select-String ":8000"
```

只有 `TIME_WAIT`，没有 `LISTENING`。

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-035-taskboard\probe_port.py
```

输出：`down ConnectTimeout: timed out`。

`inspect_app.py` 末行曾打印 `port8000 accepting=yes`，与「无 LISTENING、进程已退出、复查超时」不一致。不以那一行判断服务仍在运行。

## 6. 路由与已有用户口令

命令：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-035-taskboard\inspect_app.py
```

输出片段（exit 0）：

```
{'GET', 'HEAD'} /openapi.json deps=[]
{'POST'} /api/login deps=[]
{'GET'} / deps=[]
其余 /api/* 路由 deps=['current_user']
openapi contains 'admin123': False
openapi contains 'jsdelivr': False
openapi contains 'password': True
existing db new env password status=401
existing db original password status=200 must_change=True
```

没有 `/health` 路由。已有用户时 `TB_INITIAL_PASSWORD=should-not-apply` 不能登录，原口令仍可用。这与 README 环境变量表一致。

## 7. 仓库是否被跑测写脏

```
git status --porcelain
```

无输出。

```
Get-ChildItem -Force -Name E:\muse-bridge\in\TASK-035-taskboard
```

只有原有文件和 `.git`，没有 `data/`、`.venv/`、`.pytest_cache/`、`__pycache__/`。`tests` 目录同样只有 `test_app.py` 与 `live_selftest.py`。

## 8. 审查结束后的全量重跑

未改仓库源码。重跑 README 里的两步测试。

pytest（exit 0）：

```
...\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_pytest.py
```

```
...............                                                          [100%]
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
15 passed, 1 warning in 2.22s
```

真服务自测（exit 0，令牌已截断）：

```
...\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_live.py
```

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {"token":"8CpaHbpZ…(已截断)","username":"admin","must_change_password":true}
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

收尾：

```
git status --porcelain
git diff --stat
```

两条都无输出。








