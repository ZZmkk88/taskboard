# taskboard P2 修复记录

修前基线：`15 passed, 1 warning in 2.74s`。每条之后都重跑全量 pytest。未改 `tests/`、`LICENSE`、`UPSTREAM.md`、`requirements*.txt`。

## P2-1 README 测试数量

- 文件：`README.md:54`
- 改法：`14 项自动化测试` 改为 `15 项自动化测试`。与 `tests/test_app.py` 里 15 个 `def test_` 以及修前 `15 passed` 对齐。`DECISIONS.md:7` 的历史记录未改。
- 验证命令：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\run_pytest.py
```

```
15 passed, 1 warning in 2.55s
```

exit 0。

## P2-2 关闭 /openapi.json

- 文件：`app.py:44-50`
- 改法：`FastAPI(...)` 增加 `openapi_url=None`。`docs_url` 与 `redoc_url` 仍为 `None`。
- 验证命令：同上全量 pytest。

```
15 passed, 1 warning in 2.34s
```

exit 0。另外用 TestClient 看三条匿名文档路由：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\check_openapi.py
```

```
GET /openapi.json status=404 has_admin123=False
GET /docs status=404 has_admin123=False
GET /redoc status=404 has_admin123=False
```

exit 0。

## P2-3 过长密码在哈希前拒绝

- 文件：`app.py:34` 增加 `MAX_PASSWORD = 1024`；登录 `app.py:220-221`；改密 `app.py:270-273`。
- 改法：登录口令、旧密码、新密码只要长于 1024 个字符，就在调用 `hash_password` 之前返回 400。1024 个字符仍会进入原来的 PBKDF2，用来确认边界没有把正常长度误杀。短于 6 位的新密码仍是「新密码至少 6 位」。
- 验证命令：同上全量 pytest。

```
15 passed, 1 warning in 2.64s
```

exit 0。边界探针：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\check_password_len.py
```

```
login default status=200
login 1024 status=401 detail=用户名或密码不正确
login 1025 status=400 detail=密码太长了
new short status=400 detail=新密码至少 6 位
new 1025 status=400 detail=新密码太长了
old 1025 status=400 detail=旧密码太长了
old wrong status=400 detail=旧密码不正确
session still valid status=200 must_change=True
```

exit 0。1025 位没有去算 20 万次 PBKDF2；1024 位错误口令仍是 401。

## P2-4 哈希比较改为 secrets.compare_digest

- 文件：登录 `app.py:228-230`；改密 `app.py:276-278`。`secrets` 原本就在 `app.py:11` 导入，没有新依赖。
- 改法：两处 `!=` 改为 `not secrets.compare_digest(算出的哈希, 库存哈希)`。用户不存在时 `not user` 仍短路，不会去读盐、也不会算哈希。
- 验证：全量 pytest 覆盖错密码、正确登录、改密往返、改密作废其他会话。

```
15 passed, 1 warning in 2.95s
```

exit 0。

## P2-5 删卡、归档、恢复更新看板时间

- 文件：删除 `app.py:710-713`；归档 `app.py:772-775`；恢复 `app.py:799-802`。
- 改法：这三处在 `conn.commit()` 之前查出列所属 `board_id`，调用已有的 `_touch_board`。已经归档再归档（`app.py:765-766`）、未归档就恢复（`app.py:788-789`）仍提前返回，不提交，也不改 `updated_at`。
- 验证命令：同上全量 pytest。

```
15 passed, 1 warning in 2.70s
```

exit 0。行为探针（每次操作前先等 1.1 秒）：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\check_touch_board.py
```

```
delete_card changed=True before=2026-10-21T11:57:01+00:00 after=2026-10-21T11:57:02+00:00
archive_card changed=True before=2026-10-21T11:57:02+00:00 after=2026-10-21T11:57:03+00:00
archive_again changed=False before=2026-10-21T11:57:03+00:00 after=2026-10-21T11:57:03+00:00
restore_card changed=True before=2026-10-21T11:57:03+00:00 after=2026-10-21T11:57:06+00:00
restore_again changed=False before=2026-10-21T11:57:06+00:00 after=2026-10-21T11:57:06+00:00
```

exit 0。修前同一脚本逻辑下这三处都是 `changed=False`。

## P2-6 默认口令只提示改密

- 未改。`DECISIONS.md:23` 写明「首次改密只提示、不强制」。`tests/test_app.py:10` 与 `tests/test_app.py:22` 用 `admin` / `admin123` 登录。改默认口令或改成强制改密会打红现有测试，本任务不许改测试。

## P2-7 httpx 弃用警告

- 未改。警告来自 venv 的 `fastapi/testclient.py:1`，触发点是 `tests/test_app.py:13`。`requirements-dev.txt:2` 钉死 `httpx==0.28.1`。测试已通过。本任务不改测试，也不改已钉死的依赖版本。

## P2-8 CSP 不补 default-src

- 未改。`app.py:57` 的 CSP 仍只有 `frame-ancestors 'none'`。`static/index.html:7` 起是内联样式，`static/index.html:124` 是内联脚本。补 `default-src` 就要带 `unsafe-inline`，没有实际收紧。

## 收尾全量 pytest

代码改完后另跑一次，不是上面某一条的复述。

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\run_pytest.py
```

```
15 passed, 1 warning in 3.06s
```

exit 0。15 passed。

## git status --porcelain

```
git -C E:\muse-bridge\in\TASK-053-taskboard-p2 status --porcelain
```

```
 M README.md
 M app.py
```

工作区非空。`git diff --stat` 只有这两个文件：`README.md` 1 行，`app.py` 增 32 删 3。没有 `tests/`，没有 `LICENSE`，没有 `UPSTREAM.md`，没有 `requirements*.txt`。未执行 commit、push、restore。

