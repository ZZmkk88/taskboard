# taskboard 验收报告

结论：本机按 README 装好依赖后，pytest 16 项全过，真服务自测 16 个检查点全过，默认地址 `http://127.0.0.1:8000` 首页返回 200。没有 P0，没有 P1，所以没有改仓库源码。README 有 2 处轻微文字落差。许可证与署名在仓库内部自洽；上游 commit 与上游 LICENSE 原文未联网复核。

## 本地跑通记录

环境：`py` 启动器不可用（见下）。改用 `py -3.11`（Python 3.11.9，`C:\Users\xzm\AppData\Local\Programs\Python\Python311\python.exe`）。虚拟环境放在 `E:\muse-bridge\work\TASK-083-taskboard\venv`，没有写进待审仓库。临时数据库同样放在该工作目录。

环境限制：本机 `py -V` 原文为 `Unable to create process using 'E:\python.exe -V'`。`py -0p` 显示默认解释器是 `-V:3.14 * E:\python.exe`。这是本机启动器损坏，不是仓库缺陷。README 要求的 Python ≥3.11 由 3.11.9 满足。

### 装依赖

```text
py -3.11 -m venv E:\muse-bridge\work\TASK-083-taskboard\venv
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-083-taskboard\requirements.txt
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe -m pip install -r E:\muse-bridge\in\TASK-083-taskboard\requirements-dev.txt
```

两次 pip 均为 exit 0。运行时解析结果：fastapi 0.156.4、uvicorn 0.54.0、starlette 1.9.0。开发依赖：httpx 0.28.1、pytest 9.1.1。已安装包的 starlette 元数据 `Requires-Python` 为 `>=3.11`。fastapi 声明的是 `starlette>=0.46.0`，本次解析落到 1.9.0。

### pytest

```text
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe -m pytest tests -q --tb=short -p no:cacheprovider
```

工作目录是仓库根。`TEMP`/`TMP` 指向工作目录。输出：

```text
................                                                         [100%]
16 passed, 1 warning in 3.24s
```

警告原文：`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.` 来源是已安装的 `fastapi/testclient.py:1`。测试没有失败。

### 真服务自测（脚本自带端口 8131）

```text
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe E:\muse-bridge\in\TASK-083-taskboard\tests\live_selftest.py
```

末行原文：`ALL 16 CHECKS PASSED`。exit 0。登录打印为 `{'token': '<redacted>', 'username': 'admin', 'must_change_password': True}`。

### 默认端口 8000

```text
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-083-taskboard\serve_check.py
```

日志原文：`Uvicorn running on http://127.0.0.1:8000`。

| 请求 | 状态 | 证据 |
| --- | --- | --- |
| `GET /` | 200 | `text/html`，标题 `taskboard · 项目看板` |
| `GET /health` | 404 | `{"detail":"Not Found"}`。`app.py` 没有 `/health` 路由 |
| `GET /docs`、`/redoc`、`/openapi.json` | 404 | 与 `app.py:47-49` 关闭文档页一致 |
| `GET /api/me`、`/api/boards` 无令牌 | 401 | `{"detail":"未登录"}`，`Cache-Control: no-store` |
| `POST /api/login` admin/admin123 | 200 | `must_change_password` 为 true |

首页响应头：`X-Frame-Options: DENY`，`Content-Security-Policy: frame-ancestors 'none'`，`X-Content-Type-Options: nosniff`。

进程用 `terminate()` 关掉（未使用 taskkill）。之后绑定检查 8000 与 8131 都是 `FREE`。

`/health` 返回 404 不记入缺陷：README 没有健康检查路径，首页 200 即本次存活证据。

### 套件外抽查

`probe_extra.py`（库文件 `E:\muse-bridge\work\TASK-083-taskboard\probe.db`）结果：

- 1025 位登录口令 → 400 `密码太长了`
- 看板名 `'; DROP TABLE cards; --` 原样保存，表仍在
- 描述 `a\x00b` 存成 `ab`
- 删列后孤儿卡片 0，已归档标题也不留
- 第二个用户读/改/删别人的看板或卡片 → 404
- 主人删看板后，该看板的列数 0、卡片标题查不到

未做浏览器点击。拖拽、确认框、到期高亮只对照了 `static/index.html` 的实现。

## README 与实际不符处

写反的句子没有发现。下面 2 条是文字和界面不完全对齐，都不阻断运行。

1. 改密弹窗没写上限。README.md:9 写「新密码需 6–1024 位」。static/index.html:164 的标签是「新密码（至少 6 位）」。后端 app.py:278-281 按 6 到 1024 拒绝越界新密码，和 README 一致，落差在页面文案。
2. README 少写旧密码上限。README.md:9 只写「登录口令超过 1024 位会被拒绝」。app.py:282-283 对旧密码同样 `len > 1024` 时返回 400「旧密码太长了」。已写的那句为真，缺了旧密码这一条。

已核对且与代码一致的陈述：

| README | 代码 | 结果 |
| --- | --- | --- |
| README.md:9 令牌 24 小时、默认 admin/admin123、首次登录提示改密 | app.py:24-26、app.py:178 `must_change_password=1`、index.html:156 只 toast | 一致。提示，不拦截业务接口 |
| README.md:10 新看板自带待办/进行中/已完成 | app.py:35 | 一致。pytest 与自测都通过 |
| README.md:11 删列连同卡片，先确认 | app.py:600-607 级联删除；index.html:347 `confirm` | 一致。抽查归档卡也被删掉 |
| README.md:12 八色标签、逾期红色 | app.py:36 八色；index.html:126 同八色；index.html:244 逾期加 `overdue` | 一致 |
| README.md:18 Python ≥3.11，starlette 1.9.0 | 本次 pip 解析 starlette 1.9.0，元数据 `Requires-Python >=3.11` | 一致 |
| README.md:44-48 五个环境变量默认值 | app.py:23-27、app.py:851 | 一致。真服务日志是 `127.0.0.1:8000` |
| README.md:54-55 16 项 pytest、16 个自测检查点 | tests/test_app.py 有 16 个 `def test_`；live_selftest.py 有 16 次 `check(` | 一致。输出 `16 passed` 与 `ALL 16 CHECKS PASSED` |
| README.md:69 MIT | LICENSE:1 | 一致 |

## 许可证与署名核查

自洽，本轮不改 LICENSE 和 UPSTREAM。

- LICENSE:1-3 是 MIT，版权行 `Copyright (c) 2026 taskboard contributors`。README.md:67-69 指向该文件并写 MIT。
- UPSTREAM.md:3 写代码由本项目独立编写、未复制上游代码。UPSTREAM.md:6-9 记录参考来源 `https://github.com/kanboard/kanboard`、commit `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`、许可证 MIT、署名 `Copyright (c) Frédéric Guillot`。
- NOTES.md:5-7 与 UPSTREAM 的 commit、MIT、署名句相同，并写明上游是 PHP。
- 在 `*.py`、`*.html`、`*.txt`、`*.md` 中检索 `kanboard`、`Guillot`、`swimlane`、`Frédéric`，只命中 NOTES.md 与 UPSTREAM.md。业务代码里没有 PHP、没有上游源码片段。
- 本仓库 LICENSE 署的是 taskboard，UPSTREAM 另记上游署名。在「未复制代码、只记录设计参考」这个前提下，两份声明不互相否定。

未核实（任务禁止抓取外网，不能改写成已核对）：该 commit 是否仍是上游默认分支、Kanboard 1.2.54 是否属实、上游 LICENSE 是否逐字就是 `Copyright (c) Frédéric Guillot`。仓库内没有确凿反证，所以不改 LICENSE 与 UPSTREAM 的事实性声明。

## 分级修复清单

### P0

无。安装、pytest、真服务自测、8000 端口首页都已跑通。

### P1

无。未登录接口 401；他人资源 404；删列/删看板后无孤儿行；超长口令在进 PBKDF2 前被拒绝；会话令牌哈希由 `tests/test_app.py:112` 覆盖且本次通过；文档三路径在真服务上为 404。

以下两项容易被当成安全问题，本轮不升到 P1，也不改代码：

- 默认口令只提示不强制。DECISIONS.md:23 记了用户决定。tests/test_app.py:30-33 的模块夹具登录后直接调业务接口，若改成拦截，现有测试会失败，而测试文件不许改。
- 登录不限速。DECISIONS.md:61 已决定不修。本次真服务监听的是 `127.0.0.1`（app.py:27 的默认值）。

### P2

本轮不改。每条只留一句修法。

1. static/index.html:164 改密标签只有「至少 6 位」。修法：改成「6–1024 位」。
2. README.md:9 未写旧密码上限。修法：补上「旧密码超过 1024 位同样拒绝」，对应 app.py:282-283。
3. requirements-dev.txt:2 钉死 `httpx==0.28.1`，pytest 因此打出 httpx2 弃用警告。修法：另装 httpx2 供 Starlette TestClient 使用。DECISIONS.md:60 已决定不修，测试是绿的。
4. app.py:233-236 用户不存在时直接返回，存在时才做 PBKDF2。修法：无此用户时用固定盐做一次等长比较再返回 401。
5. app.py:174-180 初始口令入库前不查长度。修法：空串或超过 1024 位时拒绝创建，避免环境变量设坏后无法登录。默认 `admin123` 不受影响。
6. app.py:680 已归档卡片仍可 PUT，`updated_at` 会变，归档箱里的日期跟着变（index.html:398 用 `updated_at` 前 10 位当归档日）。修法：已归档时返回 400。
7. app.py:851 `int(os.environ.get("PORT", "8000"))` 遇到非数字会直接抛异常。修法：转换失败时打印并退出。
8. tests/live_selftest.py:2 注释写 whole user flow，脚本没有覆盖改密、删除、退出。修法：注释改成与 README.md:55 一致的主流程。不许改测试文件，本轮不动。
9. requirements.txt:1 只钉 fastapi，starlette 版本靠解析。修法：若要锁定 README.md:18 的 1.9.0，增加精确版本。本次安装已经是 1.9.0，没有冲突，不动依赖版本。
