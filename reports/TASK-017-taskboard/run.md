# TASK-017-taskboard 执行记录

开工时间：2026-10-21。工作目录：E:\muse-bridge\in\TASK-017-taskboard。本文件随步骤追加，不攒到最后。

## 步骤 1：环境探查

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

说明：README Windows 段写的是 `py -m venv`。本机 `py` 启动器指向损坏的 `E:\python.exe`，这条起不来。后续改用已可用的 `python`（3.11.9，满足 README「3.10 以上」）。这是本机启动器问题，不是仓库代码缺陷。

命令：

```
git -C E:\muse-bridge\in\TASK-017-taskboard rev-parse --is-inside-work-tree
git -C E:\muse-bridge\in\TASK-017-taskboard status --porcelain
```

输出：

```
true
```

`status --porcelain` 无输出，工作区干净。

## 步骤 2：创建虚拟环境

虚拟环境放在工作目录，不放进仓库：

```
python -m venv E:\muse-bridge\work\TASK-017-taskboard\venv
```

退出码 0。解释器：`E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe`。

## 步骤 3：安装依赖

命令（耗时约 33.56s，退出码 0）：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-017-taskboard\requirements.txt -r E:\muse-bridge\in\TASK-017-taskboard\requirements-dev.txt
```

输出片段：

```
Collecting fastapi==0.156.4
Collecting uvicorn==0.54.0
Collecting httpx==0.28.1
Collecting pytest==9.1.1
Successfully installed annotated-doc-0.0.5 annotated-types-0.8.0 anyio-4.15.1 certifi-2026.10.19 click-8.5.0 colorama-0.4.6 fastapi-0.156.4 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.20 iniconfig-2.3.1 opentelemetry-api-1.45.1 packaging-26.3 pluggy-1.7.0 pydantic-2.14.1 pydantic-core-2.50.1 pygments-2.21.0 pytest-9.1.1 starlette-1.9.0 typing-extensions-4.16.0 typing-inspection-0.4.4 uvicorn-0.54.0
```

版本与 requirements 锁定一致，没有改版本号。pip 提示可升级（24.0 -> 26.2.2），未执行升级。

## 步骤 4：全量 pytest

命令（退出码 0）：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\run_pytest.py
```

启动器把 TEMP/TMP 指到 `E:\muse-bridge\work\TASK-017-taskboard`，并设置 `PYTHONDONTWRITEBYTECODE=1`，工作目录切到仓库后执行：

```
pytest tests/ -q -p no:cacheprovider --basetemp E:\muse-bridge\work\TASK-017-taskboard\pytest_basetemp
```

输出：

```
..............                                                           [100%]
============================== warnings summary ===============================
app.py:159
  E:\muse-bridge\in\TASK-017-taskboard\app.py:159: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
          ...
    @app.on_event("startup")

fastapi\applications.py:4723
  DeprecationWarning: on_event is deprecated, use lifespan event handlers instead.
    return self.router.on_event(event_type)

fastapi\testclient.py:1
  StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
14 passed, 3 warnings in 1.95s
```

14 项与 README 写的数量一致。3 条是弃用警告，不是失败。

## 步骤 5：按 README 端口起服务，查首页和健康检查，然后关掉

数据库放在工作目录，不写进仓库。

第一次启动命令：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\serve.py
```

`serve.py` 用 `os.execv` 换成 `python -u app.py`。外壳任务约 2.32s 就退出（退出码 0，无日志），服务进程留在外面。`netstat` 看到：

```
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       29548
```

进程命令行：`python.exe -u app.py`。用 `os.kill(29548, SIGTERM)` 停掉。之后 `netstat -ano | findstr LISTENING | findstr :8000` 退出码 1，没有 LISTENING。

探针（`probe.py`，httpx，不用 curl）在停掉之前已经打过这个进程，要点：

```
GET / status=200 body=<!DOCTYPE html> ... <title>taskboard · 项目看板</title>
GET /health status=404 body={"detail":"Not Found"}
GET /healthz status=404 body={"detail":"Not Found"}
GET /api/health status=404 body={"detail":"Not Found"}
GET /docs status=200
GET /api/me status=401 body={"detail":"未登录"}
POST login bad status=401 body={"detail":"用户名或密码不正确"}
POST login ok status=200  must_change_password=True token_len=43
POST board name=探针' OR 1=1 --  status=200  名字按原文存下，列是 待办/进行中/已完成
DELETE column 之后 GET archived 从 1 条变成 []
GET /api/me 另一条已登录会话，在改密成功后仍是 status=200
响应头只有 server 和 content-type，没有 X-Frame-Options
```

登录令牌原文不写入本记录。文档页外链（`probe_docs.py`）：

```
/docs status 200 external ['https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js', 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css', 'https://fastapi.tiangolo.com/img/favicon.png']
/redoc status 200 external ['https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js', 'https://fastapi.tiangolo.com/img/favicon.png', 'https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700']
```

第二次启动（同一进程里跑 `app.py`，日志留得住）：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\serve_attached.py
```

等待 2 秒后读到：

```
app.py:159: DeprecationWarning:
        on_event is deprecated, use lifespan event handlers instead.
INFO:     Started server process [28064]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

再请求一次首页：

```
status 200
content_type text/html; charset=utf-8
has_taskboard True
has_login True
x_frame_options None
```

随后停掉该后台进程。`netstat -ano | findstr LISTENING | findstr :8000` 退出码 1，8000 上没有 LISTENING。

没有浏览器工具，页面上的拖拽、改密弹窗、删列确认框没有点过。首页能打开，接口按上面的探针走过。

## 步骤 6：真服务自测

命令（退出码 0）：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\run_live.py
```

实际执行 `tests/live_selftest.py`（TEMP 指到工作目录）。输出：

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {"token":"***","username":"admin","must_change_password":true}
PASS 首次登录提示改密
PASS 建看板成功
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

令牌原文已省略。自测结束自己关掉了 8131。`netstat -ano | findstr LISTENING | findstr :8131` 退出码 1。

此步骤之前 `git status --porcelain` 无输出，仓库仍干净。

## 步骤 7：按清单改 P1，并逐项验证

只改了 `app.py` 和 `static/index.html`。每改一项都重跑 pytest，结果摘要如下。完整条目在 `fix-report.md`。

- P1-1 改绑 `127.0.0.1` 后：`14 passed, 3 warnings in 1.84s`。日志 `Uvicorn running on http://127.0.0.1:8000`。netstat：`TCP 127.0.0.1:8000 LISTENING`。`GET /` 200。
- P1-2 关掉 `/docs` 和 `/redoc` 后：`14 passed, 3 warnings in 1.76s`。`/docs` 404，`/redoc` 404，`/` 200。
- P1-3 加响应头后：`14 passed, 3 warnings in 1.81s`。`/` 的响应头为 `xfo DENY`、`csp frame-ancestors 'none'`、`nosniff nosniff`。
- P1-4 删列确认文案后：`14 passed, 3 warnings in 2.16s`。`check_confirm.py` 显示旧文案已不在，新文案四段都在。
- P1-5 未改代码。现有测试要求改密后旧令牌仍可用。

全量收尾：

```
14 passed, 3 warnings in 1.83s
ALL 16 CHECKS PASSED
```

3 条警告仍在，是 P2，没有当失败。
