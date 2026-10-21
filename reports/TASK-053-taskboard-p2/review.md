# taskboard P2 第二轮审查

结论：修前全量 pytest **15 passed, 1 warning in 2.74s**（exit 0）。没有新的 P0，没有新的 P1。上一轮 `E:\muse-bridge\out\TASK-035-taskboard\review.md` 的 P2 共 8 条，本仓库行号仍然对得上。已改 P2-1 到 P2-5。P2-6、P2-7、P2-8 保持不动，理由见各条。收尾再跑一次全量 pytest，仍是 **15 passed, 1 warning in 3.06s**（exit 0）。`git status --porcelain` 为 ` M README.md` 与 ` M app.py`。改法与每条之后的 pytest 在 `fix-report.md`。

下面行号均指修前的 `E:\muse-bridge\in\TASK-053-taskboard-p2`。命令原文在 `run.md`。

## 基线

Python `3.11.9`。虚拟环境复用 `E:\muse-bridge\work\TASK-035-taskboard\venv`，未再 pip install。`check_versions.py` 打印 `fastapi==0.156.4`、`uvicorn==0.54.0`、`httpx==0.28.1`、`pytest==9.1.1`，与本仓库 `requirements.txt`、`requirements-dev.txt` 一致。

```
15 passed, 1 warning in 2.74s
```

警告是 `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.` 来自 venv 的 `fastapi/testclient.py:1`，触发点 `tests/test_app.py:13`。`tests/test_app.py` 有 15 个 `def test_`（`63` 到 `316` 行）。修前 `git status --porcelain` 无输出，HEAD `947861b`。

## 八条现状

1. 测试数量写成 14。`README.md:54` 是「14 项自动化测试」。同一命令实测 `15 passed`。多出的是 `tests/test_app.py:110` 的 `test_change_password_revokes_other_sessions`。`DECISIONS.md:7` 的「pytest 14 项」是当时那次云端重跑的记录，不改。
2. `app.py:44` 只关了 `docs_url` 和 `redoc_url`。修前探针 `GET /openapi.json status=200`，正文不含 `admin123`。不升到 P1：schema 里没有默认口令，首页脚本也是匿名可下的。
3. `app.py:257-258` 只拒绝短于 6 位的新密码。`app.py:219` 登录口令、`app.py:259` 旧口令不限长度就进 `app.py:111-114` 的 20 万次 PBKDF2。默认只听 `127.0.0.1`（`app.py:27`），不升到 P1。
4. `app.py:219` 与 `app.py:259` 用 `!=` 比较哈希。`secrets` 已在 `app.py:11` 导入。本机 `secrets.compare_digest` 对不同长度返回 False。不升到 P1：比较耗时被 PBKDF2 盖过，且是本机单用户。
5. `app.py:683` 的 `delete_card`、`app.py:739` 的 `archive_card`、`app.py:758` 的 `restore_card` 提交前不调用 `_touch_board`（定义在 `app.py:420-423`）。新建和移动会更新（`app.py:643`、`app.py:731`）。修前探针在间隔 1.1 秒后：三处 `updated_at changed=False`。
6. 默认口令 `admin` / `admin123` 在 `app.py:25-26` 与 `README.md:9`，只提示改密。`DECISIONS.md:23` 写明「首次改密只提示、不强制」。`tests/test_app.py:10` 与 `tests/test_app.py:22` 用这个口令登录。改掉会直接打红现有测试，本任务不许改测试。
7. `tests/test_app.py:13` 的 `TestClient` 触发 Starlette 弃用警告，提示安装 `httpx2`。`requirements-dev.txt:2` 钉死 `httpx==0.28.1`。测试已通过。本任务不改依赖版本号、不改测试。
8. `app.py:51` 的 CSP 只有 `frame-ancestors 'none'`。`static/index.html:7` 起是内联样式，`static/index.html:124` 是内联脚本。补 `default-src` 就要带 `unsafe-inline`，没有实际收紧。

上一轮正文还提到 `README.md:7`「均已实现并通过测试」覆盖说得过满。分级清单没有把它单列成要改的一条，本轮不动这句。`LICENSE` 与 `UPSTREAM.md` 不改。未联网复核上游 commit。

## 分级修复清单

### P0

无。修前 15 项 pytest 已通过。

### P1

无。鉴权、改密废会话、删看板级联仍由现有测试覆盖。上面第 2、3、4 条保持 P2。

### P2

1. `README.md:54`。修法：把「14 项」改成「15 项」。
2. `app.py:44`。修法：同一处加上 `openapi_url=None`。
3. `app.py:219`、`app.py:257-259`。修法：在调用 `hash_password` 之前，拒绝长于 1024 个字符的口令（登录、旧密码、新密码）。1024 高于现有测试和默认口令，又挡住把超大请求送进 20 万次 PBKDF2。
4. `app.py:219`、`app.py:259`。修法：哈希比较改为 `secrets.compare_digest`。用户不存在时仍短路，不算哈希。
5. `app.py:690-693`、`app.py:750-751`、`app.py:773-774`。修法：真正提交变更之前调用 `_touch_board`。已经归档再归档、未归档就恢复，这两条提前返回不提交，不改 `updated_at`。
6. `app.py:25-26`、`README.md:9`。修法：不改。与 `DECISIONS.md:23` 和现有测试冲突。
7. `requirements-dev.txt:2`、`tests/test_app.py:13`。修法：不改。不许改测试，也不许改已钉死的依赖版本。
8. `app.py:51`。修法：不改。页面是内联样式和内联脚本。
