# TASK-078 taskboard 执行记录

- 开工: 2026-10-22
- 工作目录: E:\muse-bridge\in\TASK-078-taskboard
- 状态: 已确认 Python，正在装依赖

## 环境

命令:

```
python --version
```

输出:

```
Python 3.11.9
```

命令:

```
python -m venv E:\muse-bridge\work\TASK-078-taskboard\venv
```

退出码: 0（无输出）

命令:

```
E:\muse-bridge\work\TASK-078-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-078-taskboard\requirements.txt
```

退出码: 0。关键行:

```
Successfully installed annotated-doc-0.0.5 annotated-types-0.8.0 anyio-4.15.1 click-8.5.0 fastapi-0.156.4 h11-0.16.0 idna-3.20 opentelemetry-api-1.45.1 pydantic-2.14.1 pydantic-core-2.50.1 starlette-1.9.0 typing-extensions-4.16.0 typing-inspection-0.4.4 uvicorn-0.54.0
```

传递依赖实际解析到 starlette-1.9.0。

命令:

```
E:\muse-bridge\work\TASK-078-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-078-taskboard\requirements-dev.txt
```

退出码: 0。关键行:

```
Successfully installed certifi-2026.10.19 colorama-0.4.6 httpcore-1.0.9 httpx-0.28.1 iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0 pytest-9.1.1
```

## 全量 pytest

命令:

```
E:\muse-bridge\work\TASK-078-taskboard\venv\Scripts\python.exe -B -m pytest E:\muse-bridge\in\TASK-078-taskboard\tests -q -p no:cacheprovider --rootdir E:\muse-bridge\in\TASK-078-taskboard
```

退出码: 0。输出:

```
................                                                         [100%]
============================== warnings summary ===============================
..\..\work\TASK-078-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-078-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 3.28s
```

## 真服务自测 live_selftest

命令:

```
E:\muse-bridge\work\TASK-078-taskboard\venv\Scripts\python.exe -B E:\muse-bridge\in\TASK-078-taskboard\tests\live_selftest.py
```

退出码: 0。输出:

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

自测脚本把服务绑在 127.0.0.1:8131（tests/live_selftest.py 第 14、31 行），跑完会 terminate。登录响应里的 token 已被脚本打成 `<redacted>`。

## README 的 py 启动器（补充核对）

命令:

```
py --version
```

退出码: 1。输出原文:

```
Unable to create process using 'E:\python.exe --version': ???????????
```

本机 `py` 启动器指向无效的 `E:\python.exe`。安装没有走这条命令，改用已验证可用的 `python`（3.11.9）。虚拟环境放在 `E:\muse-bridge\work\TASK-078-taskboard\venv`，避免把 `.venv` 写进待审仓库。这是本机启动器配置问题，不记为项目缺陷。

## 端口 8000 真服务与权限抽查

脚本: `E:\muse-bridge\work\TASK-078-taskboard\smoke_check.py`

命令:

```
E:\muse-bridge\work\TASK-078-taskboard\venv\Scripts\python.exe -B E:\muse-bridge\work\TASK-078-taskboard\smoke_check.py
```

退出码: 0。关键输出:

```
login 200 {'username': 'admin', 'must_change_password': True}
missing-user 401 {'detail': '用户名或密码不正确'}
sqli-login 401 {'detail': '用户名或密码不正确'}
login-1025 400
idor list 200 []
idor get/put/addcol/reorder/archived/delboard 404 看板不存在
idor updcol/addcard/delcol 404 列不存在
idor updcard/movecard/archive/delcard 404 卡片不存在
owner-still 200 保密看板 cards 1
owner-delete 200
after-delete fk=0 boards=0 cols=0 cards=0
route / 200
route /health /api/health /docs /redoc /openapi.json 404

pid 29436
up True elapsed 1.67
GET / 200 ctype text/html; charset=utf-8
headers x-frame-options=DENY, content-security-policy=frame-ancestors 'none', x-content-type-options=nosniff, server=uvicorn
body_has_taskboard True
body_snippet <title>taskboard · 项目看板</title>
GET /api/me 401 {"detail":"未登录"}
POST /api/login 200 token=<redacted> must_change_password=True
GET /api/me 200 cache no-store
server_exit 1
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

`after-delete fk=0` 是探测脚本另开的 sqlite 连接（没执行 PRAGMA）读到的默认值。删除发生在应用连接上，删后 boards/cols/cards 都是 0，级联生效。`server_exit 1` 是主动 terminate 之后的退出码，日志里没有 traceback。服务已退出。

starlette 元数据（已安装包）`starlette-1.9.0.dist-info\METADATA` 第 26 行: `Requires-Python: >=3.11`。

## 收尾重跑（未改源码）

命令:

```
E:\muse-bridge\work\TASK-078-taskboard\venv\Scripts\python.exe -B -m pytest E:\muse-bridge\in\TASK-078-taskboard\tests -q -p no:cacheprovider --rootdir E:\muse-bridge\in\TASK-078-taskboard
```

退出码: 0。输出:

```
................                                                         [100%]
============================== warnings summary ===============================
..\..\work\TASK-078-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-078-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 2.36s
```

命令:

```
E:\muse-bridge\work\TASK-078-taskboard\venv\Scripts\python.exe -B E:\muse-bridge\in\TASK-078-taskboard\tests\live_selftest.py
```

退出码: 0。输出末行: `ALL 16 CHECKS PASSED`。时间戳片段: `2026-10-21T16:26:28+00:00`。16 条均为 PASS。

## git status

命令:

```
git status --porcelain
```

工作目录: `E:\muse-bridge\in\TASK-078-taskboard`。退出码: 0。输出为空（无行）。未改仓库源码。




