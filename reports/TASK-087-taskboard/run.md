# TASK-087-taskboard 执行记录

开工：2026-10-22。工作目录 `E:\muse-bridge\in\TASK-087-taskboard`。先读仓库与 README，再装依赖、跑测试、起服务。

## 环境探测

命令：

```
python --version
```

输出：

```
Python 3.11.9
```

命令（README Windows 节写的是 `py -m venv`）：

```
py --version
py -m venv E:\muse-bridge\work\TASK-087-taskboard\.venv
```

输出（两条都是 exit 1）：

```
Unable to create process using 'E:\python.exe --version': ???????????
Unable to create process using 'E:\python.exe -m venv E:\muse-bridge\work\TASK-087-taskboard\.venv': ???????????
```

判定：本机 `py` 启动器指向不存在的 `E:\python.exe`，属环境限制。改用已验证可用的 `python`（3.11.9，满足 README「Python 3.11 以上」）。虚拟环境放到 `E:\muse-bridge\work\TASK-087-taskboard\.venv`，避免在仓库里落数据文件。

git：`git status --porcelain` 为空；`git rev-parse --short HEAD` = `8f930ba`。

## 创建虚拟环境

命令：

```
python -m venv E:\muse-bridge\work\TASK-087-taskboard\.venv
```

输出：exit 0，无报错。

## 安装依赖

命令：

```
E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-087-taskboard\requirements.txt
```

输出摘要（exit 0）：

```
Successfully installed annotated-doc-0.0.5 annotated-types-0.8.0 anyio-4.15.1 click-8.5.0 fastapi-0.156.4 h11-0.16.0 idna-3.20 opentelemetry-api-1.45.1 pydantic-2.14.1 pydantic-core-2.50.1 starlette-1.9.0 typing-extensions-4.16.0 typing-inspection-0.4.4 uvicorn-0.54.0
```

其中 `starlette-1.9.0`。本地 METADATA `Requires-Python: >=3.11`（`starlette-1.9.0.dist-info\METADATA` 第 26 行），与 README 第 18 行一致。

命令：

```
E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-087-taskboard\requirements-dev.txt
```

输出摘要（exit 0）：

```
Successfully installed certifi-2026.10.19 colorama-0.4.6 httpcore-1.0.9 httpx-0.28.1 iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0 pytest-9.1.1
```

## pytest

命令（在仓库根目录）：

```
E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe -m pytest tests/ -q
```

输出：

```
................                                                         [100%]
============================== warnings summary ===============================
..\..\work\TASK-087-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-087-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 3.56s
```

## 真服务自测

命令：

```
E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe tests/live_selftest.py
```

输出（exit 0）：

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {'token': '<redacted>', 'username': 'admin', 'must_change_password': True}
PASS 首次登录提示改密
PASS 建看板成功 | {"id":1,"name":"自测看板",...}
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

## 行为探针（TestClient，库文件在 work 目录）

命令：

```
E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe E:\muse-bridge\work\TASK-087-taskboard\probe_behavior.py
```

输出摘要（exit 0）：

```
home_status 200，页面含 taskboard
安全头：X-Frame-Options=DENY，CSP=frame-ancestors 'none'，X-Content-Type-Options=nosniff
/docs 404，/redoc 404，/openapi.json 404
/health 404，/api/health 404
未登录 GET /api/boards = 401
登录 200；GET /api/me Cache-Control=no-store
删列 200；删看板后 boards/columns/cards 计数均为 0
登录口令 1024 字符 → 401（进入校验，不因长度拒绝）；1025 字符 → 400
新旧密码同为 admin123 的改密 → 200，must_change_password 变为 false
```

## 按 README 起服务

数据库放到 work 目录。宿主与端口按 README 默认值传入（`127.0.0.1` / `8000`）。`live_selftest.py` 未设置 `TASKBOARD_HOST`，仍连上 `127.0.0.1:8131`，说明代码默认宿主生效。

命令：

```
E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe E:\muse-bridge\work\TASK-087-taskboard\serve_once.py
```

启动日志：

```
INFO:     Started server process [38388]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

用 `http.client` 直连（未用 curl）。`GET /` 原始响应头：

```
GET / -> 200
server: uvicorn
content-type: text/html; charset=utf-8
x-frame-options: DENY
content-security-policy: frame-ancestors 'none'
x-content-type-options: nosniff
body 开头: <!DOCTYPE html> ... <title>taskboard · 项目看板</title>
```

同一次探测：

```
GET /health -> 404 {"detail":"Not Found"}
GET /api/health -> 404，且 cache-control: no-store
GET /docs -> 404
GET /redoc -> 404
GET /openapi.json -> 404
GET /api/boards -> 401，cache-control: no-store
GET /api/me -> 401
POST /api/login -> 200 {"token":"<redacted>","username":"admin","must_change_password":true}，cache-control: no-store
```

访问日志只有路径和状态码，没有令牌或口令。README 没有健康检查路径；`/` 返回 200，`/health` 为 404。

关闭：结束上述后台进程。之后 `netstat -ano | findstr :8000` 没有 LISTENING，只有 TIME_WAIT（pid 0）。服务已停。

耗时：首次 pytest 输出为 3.56s。pip、自测和本次起服务未另计墙钟时间。

## 审查后全量重跑（未改源码）

命令：

```
E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe -m pytest tests/ -q
```

输出（exit 0）：

```
................                                                         [100%]
16 passed, 1 warning in 2.74s
```

警告仍是 `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`

命令：

```
E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe tests/live_selftest.py
```

输出末行（exit 0）：

```
ALL 16 CHECKS PASSED
```

命令：

```
git -C E:\muse-bridge\in\TASK-087-taskboard status --porcelain
```

输出：空（exit 0）。
