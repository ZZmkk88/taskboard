# taskboard 验收

能跑通。pytest **16 passed**（2.97s），真服务自测 **ALL 16 CHECKS PASSED**。默认口令可登录，首页 200，文档三件套 404，越权 404，删看板无孤儿行。P0 = 0，P1 = 0，本轮不改源码。

本机 `py` 启动器坏了，8000 端口被另一个项目占用。这两件是环境限制，不是这个仓库的缺陷。

## 本地跑通记录

工作目录 `E:\muse-bridge\in\TASK-069-taskboard`。Python `python --version` → `Python 3.11.9`。

`py -3 --version` 失败（环境限制，不记项目缺陷）：

```
Unable to create process using 'E:\python.exe --version'
```

README 的 `py -m venv` 因此没往下走。改用已可用的 `python -m venv .venv`（退出码 0）。

`.venv\Scripts\python.exe -m pip install -r requirements.txt` 退出码 0，装上 `fastapi-0.156.4`、`uvicorn-0.54.0`、`starlette-1.9.0`。

`.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` 退出码 0，装上 `httpx-0.28.1`、`pytest-9.1.1`。

命令：`.venv\Scripts\python.exe -m pytest tests/ -q --tb=short -o cache_dir=E:\muse-bridge\work\TASK-069-taskboard\pytest_cache`

```
................                                                         [100%]
.venv\Lib\site-packages\fastapi\testclient.py:1
  StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
16 passed, 1 warning in 2.97s
```

命令：`.venv\Scripts\python.exe tests\live_selftest.py`（脚本自起 127.0.0.1:8131，结束时 terminate）

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {'token': '<redacted>', 'username': 'admin', 'must_change_password': True}
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

按 README 用端口 8000 起服务失败。`serve.py` 设 `TASKBOARD_DB_PATH` 到 `E:\muse-bridge\work\TASK-069-taskboard`（避免把库写进仓库），`PORT=8000`：

```
ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): 通常每个套接字地址(协议/网络地址/端口)只允许使用一次。
```

`netstat` 显示 `127.0.0.1:8000` 由 PID 33372 监听。该进程命令行是系统 Python 的 `app.py`。对它 `GET /` 得到标题 `freshfeeds · 清泉阅读`，不是本仓库。未结束该进程。

改 `PORT=8099` 后本仓库起来了：

```
INFO:     Uvicorn running on http://127.0.0.1:8099 (Press CTRL+C to quit)
```

urllib（不是 curl）结果：

- `GET /` → 200，`content-type: text/html; charset=utf-8`，正文是 taskboard 页面
- `x-frame-options: DENY`，`content-security-policy: frame-ancestors 'none'`，`x-content-type-options: nosniff`
- `GET /api/me` 无令牌 → 401 `未登录`，并带 `cache-control: no-store`
- `GET /health`、`/api/health` → 404 `{"detail":"Not Found"}`。仓库里没有健康检查路由，README 也没写
- `GET /docs`、`/redoc`、`/openapi.json`、`/app.py` → 404
- `admin` / `admin123` 登录 200，`must_change_password: true`；库里的 session 是 SHA-256，不是明文令牌
- 密码 1025 位 → 400 `密码太长了`
- 用户名 `admin' OR '1'='1` → 401
- 删看板后，该看板的列和卡片计数都是 0
- 直接往库里插入的第二个用户，读/删第一个用户的看板、列、卡片、归档都是 404，列表是 `[]`
- `/api/me` 只返回 `username` 和 `must_change_password`

不设 `TASKBOARD_HOST`、`PORT=8098` 再起一次：

```
INFO:     Uvicorn running on http://127.0.0.1:8098 (Press CTRL+C to quit)
```

`GET /` → 200，`X-Frame-Options: DENY`。两个进程都已结束。`netstat` 查 8099、8098 均无监听。

没有浏览器工具。拖拽、到期高亮、确认框只对照了 `static/index.html` 源码（投放在 292–303 行，到期样式在 239–247 行，删列确认在 340–348 行），没有在页面上点过。

## README 与实际不符处

未发现 README 与当前代码相矛盾的陈述。下面是核对过、容易看成不符、但读码或实测后相符的点。

- `README.md:7` 与 `README.md:54` 写 16 项自动化测试。`tests/test_app.py` 有 16 个 `test_` 函数，pytest 输出 `16 passed`。
- `README.md:55` 写 16 个检查点。`tests/live_selftest.py` 的 `check()` 跑完打印 `ALL 16 CHECKS PASSED`。
- `README.md:9` 写令牌 24 小时、默认 `admin` / `admin123`、首次登录提示改密、新密码 6–1024 位、登录口令超过 1024 位拒绝。对应 `app.py:24`（`24 * 60 * 60`）、`app.py:25-26`、`app.py:178`（`must_change_password=1`）、`static/index.html:156`、`app.py:278-281`、`app.py:225-226`。1025 位实测 400。改密是提示，不是拦截，README 用的词是「提示」。
- `README.md:10` 的三列与 `app.py:35` 的 `["待办", "进行中", "已完成"]` 一致。自测输出就是这三列。
- `README.md:12` 的 8 色与 `app.py:36`、`static/index.html:126` 的 8 个键一致。
- `README.md:18` 写 Python 3.11 以上，并注明 starlette 1.9.0 要求 ≥3.11。本机 Python 3.11.9。已安装包 `starlette-1.9.0.dist-info/METADATA:26` 为 `Requires-Python: >=3.11`。
- `README.md:44` 的数据库默认路径。`app.py:23` 用 `app.py` 所在目录下的 `data/taskboard.db`，不是进程当前目录。与括号里的说明一致。
- `README.md:47` 的 `TASKBOARD_HOST` 默认 `127.0.0.1`。不设该变量时，日志是 `http://127.0.0.1:8098`。
- `README.md:48` 的 `PORT` 默认 8000。`app.py:851` 为 `os.environ.get("PORT", "8000")`。本次 8000 绑不上是端口被占，不是默认值写错。
- `README.md:60-65` 写明当前没有多用户、评论、子任务、附件、泳道、搜索、导入导出。`app.py` 里没有这些路由。
- `README.md:69` 写 MIT。见下一节。

无 `/health` 只说明 README 没承诺健康检查，不构成不符。

## 许可证与署名核查

仓库内部自洽。上游仓库按任务要求未联网打开，commit 和上游许可证原文标为未核实。没有发现可以改正 `LICENSE` 或 `UPSTREAM.md` 的确凿错误，这两个文件未改。

- `LICENSE:1-3`：MIT，`Copyright (c) 2026 taskboard contributors`。正文是标准 MIT 许可。
- `README.md:5` 指向 `UPSTREAM.md`，并写代码独立编写。`README.md:67-69` 写 MIT，与 `LICENSE` 一致。
- `UPSTREAM.md:3-9`：设计参考 Kanboard，声明未复制上游代码；`license: MIT`；`attribution: Copyright (c) Frédéric Guillot`；commit `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`。
- `NOTES.md:5-7` 与上面的 commit、许可证、署名行一致。
- 仓库里没有 Kanboard 的 PHP 源码。`app.py` 是独立的 FastAPI + SQLite 实现，和「未复制上游代码」相符。思路借鉴不要求把上游版权写进本仓库 `LICENSE`。
- 已安装依赖的包元数据（不是本仓库的声明）：fastapi `License-Expression: MIT`；starlette 与 uvicorn 为 `BSD-3-Clause`。依赖没有打进仓库，不需要把 `LICENSE` 改成 BSD。

## 分级修复清单

### P0

无。测试和真服务都能跑。8000 绑失败是本机 freshfeeds 占用，换 `PORT` 后正常。

### P1

无。登录有长度上限和 `compare_digest`（`app.py:225-236`、`app.py:284-287`），会话入库是 SHA-256（`app.py:264-266`），改密会删掉其他会话（`app.py:296-301`），看板/列/卡片都按 `user_id` 过滤。第二用户越权实测 404。文档页关闭（`app.py:47-49`），`/docs`、`/redoc`、`/openapi.json` 实测 404。安全头实测存在（`app.py:54-63`）。删看板外键级联，孤儿计数为 0。

### P2

1. `requirements-dev.txt:2` 的 `httpx==0.28.1` 触发 starlette 弃用警告（pytest 原文见上）。修法：不改已钉版本；要消警告得另评 `httpx2`，本轮不动。
2. `app.py:223-236` 登录不限速。修法：默认只听 127.0.0.1，本机攻击者可以直接读库，维持现状。
3. `app.py:174-180` 把 `must_change_password` 置 1，但没有任何接口因此拒绝业务请求；`static/index.html:156` 和 `static/index.html:412` 只 toast。修法：这是 `DECISIONS.md:23` 记下的产品决定，拦截业务接口会让现有测试失败，不改。
4. `app.py:332-337` 的卡片字段默认是空字符串，`app.py:686-697` 按全量更新。少传字段会清空描述、标签、截止日期。修法：调用方传齐字段；不改成部分更新。
5. `app.py:233` 在用户不存在时短路，不做等长哈希。修法：先对固定哑盐做一次 `compare_digest` 再返回 401。用户名已写在 `README.md:9`，不改。
6. `app.py:851` 的 `uvicorn.run` 没关 `server_header`。uvicorn `config.py:226` 默认 True，响应里有 `server: uvicorn`。修法：传入 `server_header=False`。信息不敏感，不改。
7. `app.py:649-653` 新建卡片用 `MAX(position)+1`，并发双击可能得到相同 position。修法：插入后在同一事务里重排。单用户本地场景，不改。
8. `requirements.txt:1` 只钉了 fastapi/uvicorn，starlette 是传递依赖。`README.md:18` 写死 1.9.0，今天解析结果一致。修法：若要防止以后漂移，把 `starlette==1.9.0` 写进 requirements。今天不是不符，不改。
9. `tests/live_selftest.py:14` 把自测端口写死为 8131。修法：测试文件禁止改，不改。

本轮只修 P0 和 P1。上面 9 条都不修。
