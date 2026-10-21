# TASK-062-taskboard 执行记录

开工时间：2026-10-21。工作目录：E:\muse-bridge\in\TASK-062-taskboard。先审查再修 P0/P1。

虚拟环境、临时库、pytest 缓存放在 `E:\muse-bridge\work\TASK-062-taskboard`。仓库里按 README 建 `.venv` 会把环境写进待审目录，因此没有建仓库内 `.venv`。

## 1. 环境探测

命令：`py -3 --version`

```
exit: 1
Unable to create process using 'E:\python.exe --version': ???????????
```

问号是控制台编码把中文错误打成了乱码，原文后半段未能还原。

命令：`python --version`

```
Python 3.11.9
```

命令：`git -C E:\muse-bridge\in\TASK-062-taskboard status --porcelain`

输出为空。

命令：`git -C E:\muse-bridge\in\TASK-062-taskboard ls-files`

跟踪文件：`.gitignore`、`DECISIONS.md`、`LICENSE`、`NOTES.md`、`README.md`、`UPSTREAM.md`、`app.py`、`requirements-dev.txt`、`requirements.txt`、`static/index.html`、`tests/live_selftest.py`、`tests/test_app.py`。

`.gitignore` 第 1–8 行忽略 `.venv/`、`data/`、`__pycache__/`、`*.pyc`、`.pytest_cache/`、`*.db`、`*.sqlite`、`*.sqlite3`、`.env`。

## 2. README 的 py 启动器

命令：`py -m venv E:\muse-bridge\work\TASK-062-taskboard\venv-py-test`

```
exit: 1
Unable to create process using 'E:\python.exe -m venv E:\muse-bridge\work\TASK-062-taskboard\venv-py-test': ???????????
```

本机 `py` 启动器指向不存在的 `E:\python.exe`。随后改用 `python -m venv`。

命令：`python -m venv E:\muse-bridge\work\TASK-062-taskboard\venv`

```
exit: 0
```

未执行 `Activate.ps1`。之后的命令都直接调用 `E:\muse-bridge\work\TASK-062-taskboard\venv\Scripts\python.exe`。

## 3. 装依赖

命令：

```
E:\muse-bridge\work\TASK-062-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-062-taskboard\requirements-dev.txt
```

`requirements-dev.txt:1` 含 `-r requirements.txt`，因此运行依赖和测试依赖一次装齐。exit: 0。片段：

```
Successfully installed ... fastapi-0.156.4 ... httpx-0.28.1 ... pytest-9.1.1 ... starlette-1.9.0 ... uvicorn-0.54.0
```

pip 提示可升级（24.0 → 26.2.2），未升级。

## 4. pytest（第一次）

运行器：`E:\muse-bridge\work\TASK-062-taskboard\run_pytest.py`（把 TEMP/TMP、PYTHONPYCACHEPREFIX 指到工作目录）。

内层命令（运行器打印）：

```
E:\muse-bridge\work\TASK-062-taskboard\venv\Scripts\python.exe -m pytest tests/ -q --tb=short -o cache_dir=E:\muse-bridge\work\TASK-062-taskboard\pytest_cache
```

工作目录：仓库根。exit: 0。

```
...............                                                          [100%]
============================== warnings summary ===============================
..\..\work\TASK-062-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-062-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
15 passed, 1 warning in 4.68s
```

## 5. 真服务自测（第一次）

运行器：`E:\muse-bridge\work\TASK-062-taskboard\run_live.py`。

内层命令：`E:\muse-bridge\work\TASK-062-taskboard\venv\Scripts\python.exe tests/live_selftest.py`  
工作目录：仓库根。端口 8131，数据库在工作目录临时目录。exit: 0。耗时 3.06 秒。

登录响应里的 token 在下面省略，其余按原样。

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {"token":"[已省略]","username":"admin","must_change_password":true}
PASS 首次登录提示改密
PASS 建看板成功 | {"id":1,"name":"自测看板",...
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
ELAPSED_SEC 3.06
```

## 6. 按 README 默认端口起服务

脚本：`E:\muse-bridge\work\TASK-062-taskboard\probe_server.py`  
未设置 `PORT` / `TASKBOARD_HOST`。数据库：`E:\muse-bridge\work\TASK-062-taskboard\probe\taskboard.db`。  
命令：`E:\muse-bridge\work\TASK-062-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-062-taskboard\probe_server.py`  
exit: 0。

服务日志片段：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:58350 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:58351 - "GET /health HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:58352 - "GET /healthz HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:58353 - "GET /api/health HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:58354 - "GET /docs HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:58355 - "GET /redoc HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:58356 - "GET /openapi.json HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:58357 - "GET /api/me HTTP/1.1" 401 Unauthorized
```

脚本摘要：`UP True`；`GET / STATUS 200`；正文含 `taskboard`，开头 `<!DOCTYPE html>`。  
`/health`、`/healthz`、`/api/health` 均为 404，正文 `{"detail":"Not Found"}`。  
`/api/me` 无令牌为 401，正文 `{"detail":"未登录"}`。  
`REPO_DATA_EXISTS False`（仓库内没有生成 `data/`）。  
进程 `terminate()` 后 `STOPPED 1`（Windows 上被终止的退出码）。随后 `check_port.py`：`CLOSED 8000 TimeoutError`，`CLOSED 8131 TimeoutError`。

这一轮用 urllib 读响应头得到了空值。下一轮改用原始 HTTP，确认头是有的。空值是读取方式的问题。

局域网地址探测（服务仍在 127.0.0.1:8000 时）：

```
LAN_IPS ['100.69.58.124', '192.168.31.86']
BIND_OK_NOT_LISTENING 100.69.58.124
CONNECT_LAN_FAIL 100.69.58.124 TimeoutError
BIND_OK_NOT_LISTENING 192.168.31.86
CONNECT_LAN_FAIL 192.168.31.86 TimeoutError
```

能在这两块网卡上绑定 8000，说明服务没有占住它们。连这两块地址的 8000 超时。

## 7. 原始响应头（第二次起服务，查完即停）

脚本：`E:\muse-bridge\work\TASK-062-taskboard\probe_headers.py`。exit: 0。

`GET /` 原始头：

```
HTTP/1.1 200 OK
date: Wed, 21 Oct 2026 14:37:10 GMT
server: uvicorn
content-type: text/html; charset=utf-8
accept-ranges: bytes
content-length: 24375
last-modified: Wed, 21 Oct 2026 14:21:28 GMT
etag: "87495114c1876d19fd3d035d2656a5ee"
x-frame-options: DENY
content-security-policy: frame-ancestors 'none'
x-content-type-options: nosniff
Connection: close
```

`GET /api/me` 原始头：

```
HTTP/1.1 401 Unauthorized
date: Wed, 21 Oct 2026 14:37:10 GMT
server: uvicorn
content-length: 22
content-type: application/json
x-frame-options: DENY
content-security-policy: frame-ancestors 'none'
x-content-type-options: nosniff
cache-control: no-store
Connection: close
```

`terminate()` 后脚本曾打出 `PORT_STILL_OPEN`（父进程已退出、监听还没收干净的瞬间）。紧接着 `find_port.py` 的 netstat 只有 `TIME_WAIT`，没有 `LISTENING`。收尾复查见第 10 节：8000 / 8131 无连接行。

## 8. 接口抽查（TestClient，库在工作目录）

脚本：`E:\muse-bridge\work\TASK-062-taskboard\probe_api.py`。exit: 0。全部 PASS，除下面这一条是脚本自己的连接没开外键开关：

```
FAIL fk pragma on | 0
```

该连接是脚本新建的 `sqlite3.connect`，没有执行 `PRAGMA foreign_keys=ON`。SQLite 默认按连接关闭外键。应用侧 `app.py:117` 每次 `get_db()` 都会打开。同一脚本里的级联结果是：

```
PASS no orphan cards | orphans=0 cards=2
PASS deleted board columns gone | 0
```

其余摘录：

```
PASS headers XFO | DENY
PASS headers CSP | frame-ancestors 'none'
PASS headers nosniff | nosniff
PASS html content-type | text/html; charset=utf-8
PASS anon me 401 | {"detail":"未登录"}
PASS api no-store | no-store
PASS same login error | {"detail":"用户名或密码不正确"}
PASS password 1025 rejected | {"detail":"密码太长了"}
PASS login 200
PASS ttl about 24h | 86400.0
PASS password not plaintext | len=64
PASS logout ok | {"ok":true}
PASS logged out token dead
PASS other token lives
PASS sql inject name stored
PASS boards still list
PASS null stripped
PASS bad leap rejected | {"detail":"截止日期不是有效日期"}
PASS good leap accepted
PASS idor get board
PASS idor list hides
PASS idor rename
PASS idor delete board
PASS idor add card
PASS idor read card via update
PASS idor delete card
PASS idor archive
PASS idor move target | {"detail":"列不存在"}
PASS other board untouched | secret-board/秘密卡
PASS expired token 401
```

错误用户名与错误密码返回同一句 `用户名或密码不正确`。直接插入的第二个用户的看板和卡片未被 admin 令牌改动。

## 9. 异常输入

脚本：`E:\muse-bridge\work\TASK-062-taskboard\probe_edges.py`。exit: 0。没有 Traceback。

```
422 ok tag null
422 ok due null
422 ok desc null
422 ok title null
422 ok name null
422 ok idx null
200 ok idx neg
422 ok reorder null
200 ok name 100
400 ok name 101 | {"detail":"看板名太长了"}
200 ok script title
board still 200 cards 2
```

`<script>alert(1)</script>` 作为标题被原样存进 JSON，接口没有把它当成 HTML 执行。页面插入处用 `esc()`（`static/index.html:133`）。

## 10. 收尾重跑与端口

pytest 重跑（同一运行器）exit: 0：

```
15 passed, 1 warning in 2.52s
```

警告正文与第 4 节相同（`StarletteDeprecationWarning`，install `httpx2`）。

真服务自测重跑 exit: 0，`ALL 16 CHECKS PASSED`，`ELAPSED_SEC 2.87`。登录行仍含 token，记录时已省略。

`final_check.py`：

```
CLOSED 8000 TimeoutError
CLOSED 8131 TimeoutError
=== NETSTAT ===
NO_ROWS
```

审查脚本 `import app` 曾在仓库生成 `__pycache__\app.cpython-311.pyc`（48080 字节，被 gitignore）。已用 Python 删掉该文件和空目录。`repo_data_exists False`。

命令：`git -C E:\muse-bridge\in\TASK-062-taskboard status --porcelain`  
输出为空。
