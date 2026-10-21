# taskboard 修复记录

只改 review.md 里点名的 P1。P0 没有。P1-5 不改，原因写在对应条目。

## P1-1 监听地址

- 问题编号：P1-1
- 文件:行号：`app.py:784`（改前这一行是 `host="0.0.0.0"`，改后仍是 784 行）
- 改法：`uvicorn.run` 的 `host` 从 `0.0.0.0` 改为 `127.0.0.1`。

验证命令：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\run_pytest.py
```

输出：

```
14 passed, 3 warnings in 1.84s
```

绑定验证：启动 `serve_attached.py` 后日志为

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

`netstat -ano | findstr LISTENING | findstr :8000`：

```
TCP    127.0.0.1:8000         0.0.0.0:0              LISTENING       25936
```

`GET /` 为 `status 200`，正文含 `taskboard`。查完已停掉该进程。

## P1-2 关掉会加载外部脚本的文档页

- 问题编号：P1-2
- 文件:行号：`app.py:36`
- 改法：`FastAPI(...)` 增加 `docs_url=None, redoc_url=None`。`openapi.json` 不执行第三方脚本，按清单没有关掉。

验证命令：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\run_pytest.py
```

输出：

```
14 passed, 3 warnings in 1.76s
```

再起服务后 `probe_routes.py`：

```
/ status 200
/docs status 404
/redoc status 404
/openapi.json status 200
/api/me status 401
```

首页仍是 200。`/docs` 和 `/redoc` 不再返回带 jsDelivr 脚本的页面。

## P1-3 点击劫持响应头

- 问题编号：P1-3
- 文件:行号：`app.py:39-45`（新增中间件，紧挨在 `app.py:36` 的应用对象后面）
- 改法：HTTP 中间件给每个响应加上 `X-Frame-Options: DENY`、`Content-Security-Policy: frame-ancestors 'none'`、`X-Content-Type-Options: nosniff`。

验证命令：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\run_pytest.py
```

输出：

```
14 passed, 3 warnings in 1.81s
```

再起服务后 `probe_routes.py`：

```
/ status 200 xfo DENY csp frame-ancestors 'none' nosniff nosniff
/docs status 404 xfo DENY csp frame-ancestors 'none' nosniff nosniff
/api/me status 401 xfo DENY csp frame-ancestors 'none' nosniff nosniff
```

查完已停掉该进程。

## P1-4 删列确认框漏掉归档卡

- 问题编号：P1-4
- 文件:行号：`static/index.html:333-341`
- 改法：删除前请求 `/api/boards/{id}/archived`，按 `column_id` 数出该列归档卡。确认文案改成「N 张未归档卡片」，归档数大于 0 时加上「另有 N 张已归档卡片也会删除」。接口语义没变，仍然是删列连带删卡。

验证命令：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\run_pytest.py
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\check_confirm.py
```

pytest 输出：

```
14 passed, 3 warnings in 2.16s
```

文案检查输出：

```
old_phrase_present False
present True api(`/api/boards/${current.id}/archived`)
present True k.column_id === colId
present True 另有 ${archived} 张已归档卡片也会删除
present True 张未归档卡片会一起删掉
```

没有浏览器，确认框没有在页面上点过。后端删列级联行为没改，原有 `test_delete_column_cascades_cards` 仍在这 14 项里通过。

## P1-5 改密不撤销其他会话

- 问题编号：P1-5
- 文件:行号：`app.py:244-259`（插入中间件之后；审查时是 `app.py:234-250`）
- 改法：未改。
- 原因：正确修法是删掉该用户除当前令牌以外的会话。`tests/test_app.py:79` 的 `auth` 是模块级夹具，`tests/test_app.py:101-105` 用另一次登录的新令牌把密码改回去，后面的用例继续用最初的令牌。撤销其他会话会让这些用例 401。不许改测试，所以这条不落地。审查时的探针已经看到：会话 A 改密成功后，会话 B 的 `GET /api/me` 仍是 200。

## 全量重跑

改动全部落地后重跑。失败项：无。仍有 3 条弃用警告，属于审查清单里的 P2，这次不改。

pytest：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\run_pytest.py
```

```
14 passed, 3 warnings in 1.83s
```

警告仍是 `app.py:168` 的 `on_event is deprecated`，以及 Starlette 的 `install httpx2 instead`。

真服务自测：

```
E:\muse-bridge\work\TASK-017-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-017-taskboard\run_live.py
```

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {"token":"***","username":"admin","must_change_password":true}
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

令牌原文已省略。监听地址在插入中间件后位于 `app.py:793`，值为 `127.0.0.1`。

## git status

收尾前执行：

```
git -C E:\muse-bridge\in\TASK-017-taskboard status --porcelain
```

```
 M app.py
 M static/index.html
```
