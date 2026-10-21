# TASK-053-taskboard-p2 执行记录

开工：2026-10-21。工作目录 `E:\muse-bridge\in\TASK-053-taskboard-p2`。本轮只处理上一轮 `E:\muse-bridge\out\TASK-035-taskboard\review.md` 中的 P2 条目（P0/P1 上轮已修），最多 8 条。先只读打开上一轮审查报告。

已读完上一轮报告。P2 共 8 条。接着核对已有 venv 的版本，并跑修前全量 pytest。临时目录 `E:\muse-bridge\work\TASK-053-taskboard-p2`。复用 `E:\muse-bridge\work\TASK-035-taskboard\venv`（依赖版本与本仓库 requirements 钉死值相同），不在仓库里建 `.venv`。

## 环境与修前基线

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe --version
```

```
Python 3.11.9
```

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\check_versions.py
```

```
fastapi==0.156.4
uvicorn==0.54.0
httpx==0.28.1
pytest==9.1.1
```

与 `requirements.txt`、`requirements-dev.txt` 钉死版本一致。未再执行 pip install。

```
git -C E:\muse-bridge\in\TASK-053-taskboard-p2 status --porcelain
```

无输出。`git rev-parse --short HEAD` 为 `947861b`。

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\run_pytest.py
```

脚本把 TEMP/TMP 指到工作目录，chdir 到仓库根，`-p no:cacheprovider`。

```
...............                                                          [100%]
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
15 passed, 1 warning in 2.74s
```

exit 0。警告来自 venv 的 `fastapi/testclient.py:1`，触发点是 `tests/test_app.py:13`。`tests/test_app.py` 有 15 个 `def test_`。

修前行为探针（临时库 `baseline-probe.db`，操作间隔 1.1 秒，避免同一秒时间戳看不出变化）：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\check_baseline_p2.py
```

```
GET /openapi.json status=200 has_admin123=False
delete_card updated_at changed=False before=2026-10-21T11:53:28+00:00 after=2026-10-21T11:53:28+00:00
archive_card updated_at changed=False before=2026-10-21T11:53:30+00:00 after=2026-10-21T11:53:30+00:00
restore_card updated_at changed=False before=2026-10-21T11:53:30+00:00 after=2026-10-21T11:53:30+00:00
```

exit 0。`secrets.compare_digest` 在本机 Python 3.11.9 上对不同长度返回 False，不抛异常（`check_compare_digest.py`）。

## P2-1 之后

改 `README.md:54` 的「14 项」为「15 项」，再跑全量 pytest。

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\run_pytest.py
```

```
15 passed, 1 warning in 2.55s
```

exit 0。

## P2-2 之后

`app.py` 的 `FastAPI(...)` 增加 `openapi_url=None`，再跑全量 pytest。

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\run_pytest.py
```

```
15 passed, 1 warning in 2.34s
```

exit 0。

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\check_openapi.py
```

```
GET /openapi.json status=404 has_admin123=False
GET /docs status=404 has_admin123=False
GET /redoc status=404 has_admin123=False
```

exit 0。

## P2-3 之后

`app.py:34` 增加 `MAX_PASSWORD = 1024`。登录与改密在 `hash_password` 之前拒绝更长的口令。再跑全量 pytest。

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\run_pytest.py
```

```
15 passed, 1 warning in 2.64s
```

exit 0。

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

exit 0。

## P2-4 之后

登录 `app.py:228-230`、改密 `app.py:276-278` 的哈希比较改为 `secrets.compare_digest`。再跑全量 pytest。

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\run_pytest.py
```

```
15 passed, 1 warning in 2.95s
```

exit 0。

## P2-5 之后

`delete_card`、`archive_card`、`restore_card` 在提交前调用 `_touch_board`。再跑全量 pytest。

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\run_pytest.py
```

```
15 passed, 1 warning in 2.70s
```

exit 0。

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

exit 0。P2-6、P2-7、P2-8 未改代码。

## 收尾

全部代码改完后再跑一次全量 pytest。

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-053-taskboard-p2\run_pytest.py
```

```
15 passed, 1 warning in 3.06s
```

exit 0。

```
git -C E:\muse-bridge\in\TASK-053-taskboard-p2 status --porcelain
```

```
 M README.md
 M app.py
```

```
git -C E:\muse-bridge\in\TASK-053-taskboard-p2 diff --stat
```

```
 README.md |  2 +-
 app.py    | 35 ++++++++++++++++++++++++++++++++---
 2 files changed, 33 insertions(+), 4 deletions(-)
```

`git diff -- README.md` 只有 `14 项` 改为 `15 项`。
