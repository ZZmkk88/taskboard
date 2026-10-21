# taskboard 验收报告

能跑通。pytest **16 passed**（2.36s，另有 1 条 httpx 弃用警告）。真服务自测 **16 个检查点全部 PASS**。按 README 端口起的服务在 `http://127.0.0.1:8000` 首页返回 200，安全头齐全，随后已关掉。P0、P1 均为 0，仓库源码未改。

无浏览器工具，拖拽、到期高亮、确认框没有在页面上点过，只对照了 `static/index.html` 源码。Linux 安装段未在本机执行。Kanboard 的 commit 未访问 GitHub 复核（任务禁止抓取外部页面）。

## 本地跑通记录

环境：Windows，`python --version` 输出 `Python 3.11.9`。虚拟环境放在 `E:\muse-bridge\work\TASK-078-taskboard\venv`（仓库 `.gitignore` 虽忽略 `.venv/`，临时文件仍按任务放到 work 目录）。

README 写的 Windows 第一步在本机失败。命令 `py --version`，退出码 1，原文：

```
Unable to create process using 'E:\python.exe --version': ???????????
```

这是本机 `py` 启动器配置，安装改走已可用的 `python -m venv`。依赖安装成功。`requirements.txt` 解析到 fastapi 0.156.4、uvicorn 0.54.0、starlette 1.9.0。已安装包 `starlette-1.9.0.dist-info\METADATA` 第 26 行是 `Requires-Python: >=3.11`。

全量 pytest（收尾重跑）：

```
E:\muse-bridge\work\TASK-078-taskboard\venv\Scripts\python.exe -B -m pytest E:\muse-bridge\in\TASK-078-taskboard\tests -q -p no:cacheprovider --rootdir E:\muse-bridge\in\TASK-078-taskboard
```

```
16 passed, 1 warning in 2.36s
```

警告原文：`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.` 来自 site-packages 的 `fastapi\testclient.py:1`，测试仍通过。第一次同样命令是 `16 passed, 1 warning in 3.28s`。

真服务自测（收尾重跑）退出码 0，末行 `ALL 16 CHECKS PASSED`。脚本监听 `127.0.0.1:8131`（`tests/live_selftest.py:14` 与 `:31`），结束时 `terminate`。登录打印已是 `<redacted>`。项目测试自己用 `tempfile.mkdtemp` 写到系统临时目录（`tests/test_app.py:9`、`tests/live_selftest.py:28`），未改测试，没有改道。

按 README 用端口 8000 另起一次 `app.py`（数据库在 work 目录的 `smoke.db`）。启动日志：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

约 1.67s 后可访问。`GET /` 返回 200，`content-type: text/html; charset=utf-8`，正文含 `<title>taskboard · 项目看板</title>`。响应头：`X-Frame-Options: DENY`，`Content-Security-Policy: frame-ancestors 'none'`，`X-Content-Type-Options: nosniff`。`POST /api/login`（admin / admin123）200，`must_change_password` 为 true，记录里令牌已打码。`GET /api/me` 带令牌 200，`Cache-Control: no-store`；不带令牌 401 `未登录`。

仓库没有健康检查路由。`GET /health` 与 `GET /api/health` 都是 404 `{"detail":"Not Found"}`。`/docs`、`/redoc`、`/openapi.json` 也是 404。进程已 `terminate`，退出码 1，日志无 traceback，这是主动结束的退出码。

另用 TestClient 做了权限抽查（work 目录 `probe.db`）：不存在的用户与 `' OR 1=1 --` 都是 401，文案同为「用户名或密码不正确」。1025 位密码登录返回 400。直接往库里插入第二个用户后，该用户 `GET /api/boards` 为 200 且列表为空；访问、改、删第一个用户的看板、列、卡片均为 404。第一个用户删除看板后，`boards`、`board_columns`、`cards` 计数都是 0。

## README 与实际不符处

无实质不符。下面每条都是 README 说法和代码位置，两边一致。

- README.md:7、README.md:54 写 16 项后端测试。`tests/test_app.py` 有 16 个 `test_` 函数（65、70、76、81、112、130、155、162、178、205、217、245、273、291、305、336 行）。pytest 输出 `16 passed`。
- README.md:55 写真服务自测 16 个检查点。`tests/live_selftest.py` 的 `check(` 共 16 处（50、55、57、61、64、68、80、84、88、92、96、99、101、104、107、110 行）。输出 `ALL 16 CHECKS PASSED`。
- README.md:9 默认账号 admin / admin123、令牌 24 小时、首次登录提示改密、新密码 6–1024 位、登录口令超过 1024 位拒绝。对应 app.py:24–26、app.py:34、app.py:178、app.py:225–226、app.py:278–281。页面提示在 static/index.html:156 与 :412，不拦截接口。
- README.md:10 多看板、改名删除、新建自带三列。列名在 app.py:35，创建在 app.py:477–481。自测输出 `['待办', '进行中', '已完成']`。
- README.md:11 列的增删改和调序，删列会先确认并连带删卡。接口在 app.py:528–618。确认框在 static/index.html:340–348，文案含未归档数和归档数。
- README.md:12–13 卡片字段、8 色、到期高亮、拖拽和方向按钮。颜色列表 app.py:36 与 static/index.html:126 都是 8 个。本地日历日比较在 static/index.html:234–246。拖拽绑在整列 static/index.html:292–303。移动接口 app.py:730–766。
- README.md:14 归档、原列、恢复到列尾、彻底删除。接口 app.py:770–836。归档箱 static/index.html:392–408。自测恢复后顺序为 `['约访谈', '买咖啡豆']`。
- README.md:44–48 环境变量默认值。数据库 app.py:23，用户名密码 app.py:25–26，监听 app.py:27，端口 app.py:851。启动日志是 `127.0.0.1:8000`。
- README.md:18 写 starlette 1.9.0 且 Python ≥3.11。本次 pip 安装到 starlette 1.9.0，METADATA 第 26 行 `Requires-Python: >=3.11`。本机 3.11.9 跑通。同句「3.11 以上」口语上可能读成不含 3.11，括号里的 ≥3.11 与实测一致，不记为矛盾。`requirements.txt:1-2` 没有钉死 starlette，它是 fastapi 的传递依赖；本次解析结果与 README 相同。
- README.md:60–65 写明当前没有多用户、评论、子任务、附件、泳道、导入导出。代码里没有这些路由。
- README.md:38 首页 `http://127.0.0.1:8000`。实测 `GET /` 200。没有 `/health`，README 也没承诺健康检查 URL。

`DECISIONS.md:7` 的「pytest 14 项」和 `DECISIONS.md:28` 的「pytest 15 项」是当时那一轮的记录。当前 README 写的是 16，与现在的测试数一致。

## 许可证与署名核查

自洽。未改 LICENSE 与 UPSTREAM。

- LICENSE:1-3 是 MIT 全文，版权行为 `Copyright (c) 2026 taskboard contributors`。
- README.md:5 写代码独立编写，署名见 UPSTREAM.md。README.md:69 写 MIT，见 LICENSE。
- UPSTREAM.md:3-4 写独立编写、未复制上游代码。UPSTREAM.md:6-9 记录 Kanboard、commit `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`、license MIT、`Copyright (c) Frédéric Guillot`。
- NOTES.md:6-8 与 UPSTREAM 的 commit、许可证和署名行一致，并写明署名行是逐字抄来的。
- app.py 与 static/index.html 是 Python 和单个 HTML 页面。抽查未见 Kanboard 的 PHP 源码或成段复制。

`source_commit` 是否仍是上游仓库 HEAD、署名行是否与 GitHub 上的 LICENSE 逐字相同，本次未联网，标为未核实。仓库内部三份声明彼此一致，没有足够依据去改 LICENSE 或 UPSTREAM。

## 分级修复清单

### P0

无。安装、pytest、真服务自测、8000 端口首页均已跑通。

### P1

无。匿名文档三件套返回 404。越权抽查均为 404（第二用户的看板列表为空）。删看板后三张业务表计数为 0。登录错误不区分「无此用户」和「密码错」。1025 位密码在进 PBKDF2 前返回 400。

以下是代码里已有、且与 README 一致的取舍，不单列成待修项：默认口令只提示不强制（README.md:9，app.py:178，DECISIONS.md:23）；默认只听 127.0.0.1（app.py:27，README.md:47）；登录不限速（DECISIONS.md:61）。强制改密会让 `tests/test_app.py` 里模块级登录夹具走不通，而测试文件不能改。

### P2

1. `static/index.html:398` 归档日期用 `updated_at` 的前 10 个字符，这是服务端 UTC 的 ISO 日期。到期芯片已改成本地日历日（同文件 234–237 行，DECISIONS.md:18 写过东八区误判）。修法：把 `updated_at` 解析成 `Date`，再取本地年月日。
2. `static/index.html:164` 改密框只写「至少 6 位」。后端 `app.py:280` 会拒绝长于 1024 的新密码（上限常量 `app.py:34`）。修法：标签改成「6–1024 位」。
3. `requirements-dev.txt:2` 的 `httpx==0.28.1` 让 pytest 打出 Starlette 弃用警告（见上面的 pytest 输出）。没有版本冲突，16 项仍然通过。修法：保持钉死版本，本轮不改依赖。
