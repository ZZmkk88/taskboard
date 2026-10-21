# TASK-083-taskboard 执行记录

开工时间：2026-10-22（本地执行方 Grok Build）
工作目录：E:\muse-bridge\in\TASK-083-taskboard
临时目录：E:\muse-bridge\work\TASK-083-taskboard

## 步骤 0 · 环境探测

命令：`python --version`；`py -V`；`py -3.11 -c "import sys; print(sys.version)"`；`git status --porcelain`；`Get-NetTCPConnection -LocalPort 8000,8131`

输出摘要：

- `python` = `E:\muse-bridge\env\TASK-083-taskboard\Scripts\python.exe`，版本 `3.11.9`（tags/v3.11.9:de54cf5, Apr 2 2024, MSC v.1938 64 bit AMD64）。
- `py -V` 失败原文：`Unable to create process using 'E:\python.exe -V'`（`py -0p` 显示默认 `-V:3.14 * E:\python.exe`，该解释器起不来）。
- `py -3.11` 可用：`3.11.9`，路径 `C:\Users\xzm\AppData\Local\Programs\Python\Python311\python.exe`。
- `git status --porcelain` 空（工作区干净）。
- 本机 8000、8131 端口无监听。
- 预置环境已有 fastapi 0.156.4、uvicorn 0.54.0、starlette 1.9.0；尚无 pytest / httpx。starlette METADATA：`Requires-Python >=3.11`。fastapi 依赖为 `starlette>=0.46.0`（未钉死 1.9.0）。

结论：README 写的 Windows 第一步 `py -m venv` 在本机会走到坏掉的 3.14，属环境限制。后续改用 `py -3.11` 在临时目录建 venv，不把 `.venv` 写进待审仓库。

## 步骤 1 · 建虚拟环境并安装 requirements.txt

命令：

```text
py -3.11 -m venv E:\muse-bridge\work\TASK-083-taskboard\venv
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-083-taskboard\requirements.txt
```

结果：venv 创建 exit 0。pip exit 0。解析到的关键版本：

- fastapi==0.156.4
- uvicorn==0.54.0
- starlette==1.9.0（从 fastapi 的 `starlette>=0.46.0` 解析而来，与 README 第 18 行一致）
- pydantic==2.14.1
- opentelemetry-api==1.45.1（fastapi 的直接依赖，应用代码未配置导出）

pip 末尾原文：`Successfully installed annotated-doc-0.0.5 annotated-types-0.8.0 anyio-4.15.1 click-8.5.0 fastapi-0.156.4 h11-0.16.0 idna-3.20 opentelemetry-api-1.45.1 pydantic-2.14.1 pydantic-core-2.50.1 starlette-1.9.0 typing-extensions-4.16.0 typing-inspection-0.4.4 uvicorn-0.54.0`

## 步骤 2 · 安装 requirements-dev.txt

命令：

```text
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-083-taskboard\requirements-dev.txt
```

结果：exit 0。新增 httpx==0.28.1、pytest==9.1.1（以及 httpcore、certifi、pluggy 等传递依赖）。fastapi/uvicorn 版本未变。

pip 末尾原文：`Successfully installed certifi-2026.10.19 colorama-0.4.6 httpcore-1.0.9 httpx-0.28.1 iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0 pytest-9.1.1`

## 步骤 3 · pytest

命令（经临时脚本把 TEMP/TMP 指到工作目录，并加 `-p no:cacheprovider`，避免把缓存写进仓库）：

```text
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe -m pytest tests -q --tb=short -p no:cacheprovider
```

工作目录：`E:\muse-bridge\in\TASK-083-taskboard`

输出原文：

```text
................                                                         [100%]
============================== warnings summary ===============================
..\..\work\TASK-083-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-083-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 3.24s
```

exit 0。16 项全过。警告来自 Starlette 对 httpx（非 httpx2）的弃用提示，测试未失败。

## 步骤 4 · 真服务自测 live_selftest.py（端口 8131）

命令：

```text
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe E:\muse-bridge\in\TASK-083-taskboard\tests\live_selftest.py
```

工作目录：仓库根。TEMP/TMP 指向 `E:\muse-bridge\work\TASK-083-taskboard`。脚本自己把数据库放到临时目录、端口设为 8131，结束后 `proc.terminate()`。

输出原文（16 行 PASS，末行）：

```text
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

exit 0。

## 步骤 5 · 按 README 默认端口起真服务并关掉

数据库放到工作目录，避免在仓库里生成 `data/taskboard.db`。未设置 `TASKBOARD_HOST`，走代码默认值。

命令：

```text
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-083-taskboard\serve_check.py
```

进程日志原文：

```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:64603 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:64603 - "GET /health HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:64603 - "GET /docs HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:64603 - "GET /redoc HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:64603 - "GET /openapi.json HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:64603 - "GET /api/me HTTP/1.1" 401 Unauthorized
INFO:     127.0.0.1:64603 - "GET /api/boards HTTP/1.1" 401 Unauthorized
INFO:     127.0.0.1:64603 - "POST /api/login HTTP/1.1" 200 OK
INFO:     127.0.0.1:64603 - "GET /api/me HTTP/1.1" 200 OK
```

响应摘要：

- `GET /` → 200，`content-type: text/html; charset=utf-8`，正文以 `<title>taskboard · 项目看板</title>` 开头。
- 安全头：`X-Frame-Options: DENY`，`Content-Security-Policy: frame-ancestors 'none'`，`X-Content-Type-Options: nosniff`。`/api/me` 另有 `Cache-Control: no-store`。
- `GET /health` → 404 `{"detail":"Not Found"}`。代码没有健康检查路由（`app.py` 路由清单无 `/health`）。首页 200 作为存活判断。
- `GET /docs`、`/redoc`、`/openapi.json` → 404。
- 未带令牌的 `/api/me`、`/api/boards` → 401 `{"detail":"未登录"}`。
- `POST /api/login` 默认账号 → 200，`must_change_password` 为 true，令牌长度 43。再调 `/api/me` → 200。

结束方式：脚本对子进程 `terminate()`（未使用 taskkill）。随后绑定检查 8000 与 8131 均为 `FREE`。`terminate` 后退出码 1，端口已释放。

## 步骤 6 · 套件未覆盖的抽查（TestClient + 直接查 SQLite）

命令：

```text
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-083-taskboard\probe_extra.py
```

数据库：`E:\muse-bridge\work\TASK-083-taskboard\probe.db`。

输出原文：

```text
login 200
login_1025 400 {"detail":"密码太长了"}
sqli_name 200 '; DROP TABLE cards; --
null_desc 'ab'
del_col 200
orphan_cards_after_col_delete 0 archived_title_left 0
pragma_fk_on_raw_connect 0
other_login 200
idor_get_board 404 {"detail":"看板不存在"}
idor_put_card 404 {"detail":"卡片不存在"}
idor_del_board 404 {"detail":"看板不存在"}
owner_del_board 200
after_board_delete boards 0 cols 0 cards_for_deleted_col_title 0
cascade_board2 cols 0 titles []
tables ['board_columns', 'boards', 'cards', 'sessions', 'sqlite_sequence', 'users']
```

读法：看板名里的 SQL 片段被当成普通字符串存下来，表还在。描述里的 `\x00` 被去掉。删列后归档卡不留孤儿行。另一个用户访问别人的看板/卡片得到 404。删看板后列和卡片行数为 0。裸连 SQLite 时 `PRAGMA foreign_keys` 为 0，应用连接在 `get_db()` 里打开外键后级联才生效。

## 步骤 7 · 确定不改源码后重跑全量测试

清单结论是 P0/P1 均为 0，未改仓库。重跑命令（`run_final.py` 串行）：

```text
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe -m pytest tests -q --tb=short -p no:cacheprovider
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe E:\muse-bridge\in\TASK-083-taskboard\tests\live_selftest.py
```

pytest：`16 passed, 1 warning in 3.47s`，墙钟 `ELAPSED_S 4.76`，exit 0。警告仍是 httpx / httpx2 弃用提示。

live_selftest：`ALL 16 CHECKS PASSED`，墙钟 `ELAPSED_S 2.35`，exit 0。

`FINAL_FAIL 0`。

## 步骤 8 · git status

命令：

```text
git -C E:\muse-bridge\in\TASK-083-taskboard status --porcelain
```

退出码 0，标准输出为空。仓库相对开工时没有新增或修改的文件。
