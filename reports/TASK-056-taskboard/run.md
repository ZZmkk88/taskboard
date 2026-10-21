# TASK-056-taskboard 执行记录

开工时间：2026-10-21
角色：本地执行方（Grok Build）验收云端 Muse 交付的 taskboard 仓库。
工作目录：E:\muse-bridge\in\TASK-056-taskboard
临时目录：E:\muse-bridge\work\TASK-056-taskboard

## 步骤 0 · 环境探查

命令：
```
python --version
python -c "import sys; print(sys.executable); print(sys.version)"
py -0p
py -3.14 --version
git status --porcelain
git rev-parse --show-toplevel
git log -1 --oneline
git ls-files
```

输出摘要：
- `python --version` → `Python 3.11.9`（满足 README「Python 3.10 以上」）
- 实际解释器：`E:\muse-bridge\env\TASK-056-taskboard\Scripts\python.exe`
- `py -0p`：
  ```
   -V:3.14 *        E:\python.exe
   -V:3.11          C:\Users\xzm\AppData\Local\Programs\Python\Python311\python.exe
  ```
- `py -3.14 --version` 失败（exit 1）：
  ```
  Unable to create process using 'E:\python.exe --version': ???????????
  ```
  默认 `py` 指向损坏的 3.14（E:\python.exe 起不来）。README Windows 安装步骤写的是 `py -m venv .venv`，在本机应会跟着失败。下面按 README 先试一次，失败则改用可用的 3.11。
- `git status --porcelain`：空（工作区干净）
- 仓库根：`E:/muse-bridge/in/TASK-056-taskboard`
- HEAD：`a3ac536 fix(TASK-053): 采纳 P2 修复 5 项——README 写实测试数、关 /openapi.json、密码超长拒绝、compare_digest、删/归档/恢复更新看板时间`
- 已跟踪文件含 `.gitignore`（忽略 `.venv/` `data/` `__pycache__/` `*.db` 等）

预置 venv `E:\muse-bridge\env\TASK-056-taskboard` 已有运行时依赖（`pip freeze`）：
```
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.15.1
click==8.5.0
fastapi==0.156.4
h11==0.16.0
idna==3.20
opentelemetry-api==1.45.1
pydantic==2.14.1
pydantic_core==2.50.1
starlette==1.9.0
typing-inspection==0.4.4
typing_extensions==4.16.0
uvicorn==0.54.0
```
没有 pytest / httpx。测试依赖稍后按 `requirements-dev.txt` 安装。按任务约束，新建的 venv、数据库、日志放工作目录，不写进仓库。

## 步骤 1 · 按 README 建虚拟环境

README Windows 步骤是 `py -m venv .venv`。本任务禁止把临时文件写进仓库，所以 venv 目标改到工作目录（只改路径，启动器仍按 README 用 `py`）。

命令：
```
py -m venv E:\muse-bridge\work\TASK-056-taskboard\.venv-pydefault
```
结果：exit 1
```
Unable to create process using 'E:\python.exe -m venv E:\muse-bridge\work\TASK-056-taskboard\.venv-pydefault': ???????????
```
判定：环境限制。本机 `py` 默认指向损坏的 Python 3.14（`E:\python.exe`），不是项目缺陷。README 要求 Python 3.10 以上；`py -3.11 --version` 为 `Python 3.11.9`，改用它建 venv。

命令：
```
py -3.11 -m venv E:\muse-bridge\work\TASK-056-taskboard\.venv
```
结果：exit 0。

## 步骤 2 · 安装依赖

命令（在工作目录 venv 里装 `requirements-dev.txt`，它包含 `-r requirements.txt`）：
```
E:\muse-bridge\work\TASK-056-taskboard\.venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-056-taskboard\requirements-dev.txt
```
结果：exit 0。钉死版本均能解析并安装。末尾：
```
Successfully installed annotated-doc-0.0.5 annotated-types-0.8.0 anyio-4.15.1 certifi-2026.10.19 click-8.5.0 colorama-0.4.6 fastapi-0.156.4 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.20 iniconfig-2.3.1 opentelemetry-api-1.45.1 packaging-26.3 pluggy-1.7.0 pydantic-2.14.1 pydantic-core-2.50.1 pygments-2.21.0 pytest-9.1.1 starlette-1.9.0 typing-extensions-4.16.0 typing-inspection-0.4.4 uvicorn-0.54.0
```
pip 提示可升级 24.0 → 26.2.2，未升级（与验收无关）。

## 步骤 3 · pytest 全量

第一次误用 `pytest.main()`，工作目录占了 `sys.path`，收集失败：`ModuleNotFoundError: No module named 'app'`。这是跑法错误，不是项目缺陷。改为与 README 一致的 `python -m pytest`，cwd=仓库根。

命令：
```
E:\muse-bridge\work\TASK-056-taskboard\.venv\Scripts\python.exe -m pytest tests/ -q -p no:cacheprovider --tb=short
```
cwd：`E:\muse-bridge\in\TASK-056-taskboard`
环境：`TEMP`/`TMP`=`E:\muse-bridge\work\TASK-056-taskboard\tmp`，`PYTHONDONTWRITEBYTECODE=1`（避免把缓存写进仓库）。

结果：exit 0
```
...............                                                          [100%]
============================== warnings summary ===============================
..\..\work\TASK-056-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-056-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
15 passed, 1 warning in 2.19s
```
与 README「15 项」一致。警告来自依赖（Starlette 弃用 httpx），测试本身通过。

## 步骤 4 · 真服务自测 live_selftest

命令：
```
E:\muse-bridge\work\TASK-056-taskboard\.venv\Scripts\python.exe tests/live_selftest.py
```
cwd：仓库根。同上，临时库落到 work\tmp。脚本自己起 uvicorn（PORT=8131），结束时 `proc.terminate()`。

结果：exit 0。16 条 PASS，最后一行 `ALL 16 CHECKS PASSED`。登录响应里的一次性 token 已打码：
```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {"token":"<redacted>","username":"admin","must_change_password":true}
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
与 README「16 个检查点」一致。

## 步骤 5 · 按 README 起服务（PORT=8000）并关掉

数据库放到工作目录，避免在仓库里生成 `data/taskboard.db`。

命令：工作目录 `probe_server.py` 用 venv 的 python 执行 `app.py`，环境变量：
```
TASKBOARD_DB_PATH=E:\muse-bridge\work\TASK-056-taskboard\server-check.db
TASKBOARD_HOST=127.0.0.1
PORT=8000
```
cwd：仓库根。日志：`E:\muse-bridge\work\TASK-056-taskboard\server-8000.log`。

结果（真实片段）：
```
startup_wait_s=1.16 pid=28444 poll=None
GET / status=200 ctype=text/html; charset=utf-8
  headers={'x-frame-options': 'DENY', 'content-security-policy': "frame-ancestors 'none'", 'x-content-type-options': 'nosniff', 'cache-control': None, 'server': 'uvicorn', 'set-cookie': None}
homepage_has_taskboard True
GET /health status=404 body={"detail":"Not Found"}
GET /api/health status=404 body={"detail":"Not Found"}
GET /docs status=404
GET /redoc status=404
GET /openapi.json status=404
GET /app.py status=404
GET /static/index.html status=404
GET /data/taskboard.db status=404
GET /.env status=404
GET /api/boards no auth status=401 body={"detail":"未登录"}
POST /api/login 200 must_change True
login_set_cookie None
GET /api/me status=200 body={"username":"admin","must_change_password":true}
host_header_status 200 reflects False
lan_ip 192.168.31.86
lan_get_failed ConnectTimeout timed out
server_exit 1
```
uvicorn 日志：
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:56260 - "GET / HTTP/1.1" 200 OK
```
关闭方式：脚本 `proc.terminate()`，随后 `poll=1`。这是 Windows 上终止进程的退出码，不是应用自己崩溃。

复查端口（新 socket，1.5 秒超时）`check_ports.py`：
```
port 8000 CLOSED TimeoutError timed out
port 8131 CLOSED TimeoutError timed out
```
两个端口都是超时而不是 ConnectionRefused。服务在跑时，同机 `GET http://127.0.0.1:8000/` 已经返回 200，所以「有进程在听」和「没人听」是分得开的。关掉之后 8000 不再完成握手。局域网 IP `192.168.31.86:8000` 在服务仍运行时也是 ConnectTimeout；uvicorn 日志写的是 `127.0.0.1:8000`，不能据此说它听了 0.0.0.0。

同一次探针还在另一个库 `probe-logic.db` 上做了进程内检查（TestClient），摘要：
```
PRAGMA foreign_keys 1
TOKEN_TTL 86400
HOST_CONST 127.0.0.1
idor_get_board 404
idor_list []
idor_delete_card 404
idor_get_archived 404
idor_move_cross_board 404
idor_move_other_user_card 404
orphan_cards_after_column_delete 0
board_cols_left 0 cards_without_column 0
pw_1025 400
pw_1024 401
sqli_status 200 name x'; DROP TABLE boards;--
boards_still_listed 200
bad_date 400
after_logout 401
after_expire 401
null_titles [(9, 'ab\x00cd', [97, 98, 0, 99, 100])]
```
跨用户移动得到 404，是因为列归属校验先于「不能跨看板」的 400（同用户跨看板仍由 pytest `test_move_to_other_board_rejected` 覆盖为 400）。SQL 注入字符串被当成看板名存下来，`boards` 表还在。空字节标题原样入库，没有截断。

`git status --porcelain`（探针之后）：空。仓库没有新增 `data/`、`__pycache__` 或数据库。

## 步骤 6 · 审查结束后重跑全量测试

未改源码（无 P0/P1）。仍按要求重跑。

pytest exit 0：
```
15 passed, 1 warning in 2.06s
```
警告仍是 `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`

live_selftest exit 0，末行：
```
ALL 16 CHECKS PASSED
```
时间戳 `2026-10-21T13:22:05+00:00`。一次性 token 已打码。

## 步骤 7 · git status --porcelain

命令（仓库根）：
```
git status --porcelain
```
exit 0，标准输出为空。仓库工作区无改动。
