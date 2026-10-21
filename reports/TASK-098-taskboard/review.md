# taskboard 验收

能跑通。pytest **16 passed**（3.66s，1 条弃用警告）。真服务自测 **ALL 16 CHECKS PASSED**。默认监听 `http://127.0.0.1:8000`，首页 200。没有健康检查路由，`/health`、`/healthz`、`/api/health` 都是 404。P0、P1 为 0，未改源码。

证据文件都在仓库 `E:\muse-bridge\in\TASK-098-taskboard`。命令细节在同目录 `run.md`。

## 本地跑通记录

本机 `python` 为 **Python 3.11.9**。README 第 32 行的 `py -m venv .venv` 在这台机器上失败，原文：

```
Unable to create process using 'E:\python.exe --version'
```

这是本机 `py` 启动器指向了不存在的 `E:\python.exe`。改用 `python -m venv .venv` 后装依赖、跑测试、起服务都成功。Linux/macOS 安装段没有在本机执行。

运行依赖（退出码 0）：

```
.venv\Scripts\python.exe -m pip install -r requirements.txt
Successfully installed ... fastapi-0.156.4 ... starlette-1.9.0 ... uvicorn-0.54.0
```

`starlette-1.9.0.dist-info\METADATA` 第 26 行是 `Requires-Python: >=3.11`，与 README.md:18 一致。

开发依赖（退出码 0）：

```
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Successfully installed ... httpx-0.28.1 ... pytest-9.1.1
```

pytest。临时库和缓存放在 `E:\muse-bridge\work\TASK-098-taskboard`（脚本 `run_pytest.py` 设置 TEMP/TMP 后调用 `pytest.main(["tests/", "-q", ...])`，对应 README.md:54）：

```
................                                                         [100%]
.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
16 passed, 1 warning in 3.66s
```

真服务自测（`run_live.py` 执行 `tests/live_selftest.py`，端口 8131，结束时 `proc.terminate()`）：

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

按 README 起服务：不设置 `PORT` 和 `TASKBOARD_HOST`，`TASKBOARD_DB_PATH` 指到工作目录。导入默认值：

```
E:\muse-bridge\in\TASK-098-taskboard\data\taskboard.db
'127.0.0.1'
86400
```

日志：`Uvicorn running on http://127.0.0.1:8000`。随后 `proc.terminate()`，子进程 `poll=1`。仓库里没有生成 `data\`。

| 请求 | 状态 | 响应片段 |
| --- | --- | --- |
| GET / | 200 | `<title>taskboard · 项目看板</title>`，`content-type: text/html; charset=utf-8` |
| GET /health | 404 | `{"detail":"Not Found"}` |
| GET /healthz | 404 | `{"detail":"Not Found"}` |
| GET /api/health | 404 | `{"detail":"Not Found"}` |
| GET /docs、/redoc、/openapi.json | 404 | `{"detail":"Not Found"}` |
| GET /api/me、/api/boards（无令牌） | 401 | `{"detail":"未登录"}` |
| POST /api/login admin/admin123 | 200 | `LOGIN 200 must_change True`（令牌未写入本报告） |

首页响应头含 `x-frame-options: DENY`、`content-security-policy: frame-ancestors 'none'`、`x-content-type-options: nosniff`。`/api/me` 另有 `cache-control: no-store`。

删列后该列已归档卡片为 0 行；删看板后 `boards=0 cols=0 cards=0`。会话表令牌长度为 64，明文令牌不在库里。

关掉之后进程列表没有 `app.py`。对 127.0.0.1:8000 和 8131 做阻塞连接，2 秒超时，没有连上。

前端拖拽、确认框、到期高亮没有在浏览器里点过。核对了 `static/index.html` 的事件绑定（整列 drop，按纵坐标算插入位置；删列/删看板/删卡有 `confirm`）。

## README 与实际不符处

1. **README.md:9** 写「新密码需 6–1024 位」。**static/index.html:164** 的标签是「新密码（至少 6 位）」，页面上没有 1024 的上限。**app.py:34** 的 `MAX_PASSWORD = 1024`，**app.py:287-290** 对短于 6 位或长于 1024 位返回 400。后端行为和 README 一致，不一致的是页面提示。

除此之外，下面这些声明和代码一致（行号是核对位置）：

- README.md:7、README.md:54 的 16 项测试：`tests/test_app.py` 有 16 个 `test_` 函数，pytest 输出 `16 passed`。
- README.md:55 的 16 个检查点：`tests/live_selftest.py` 的 `check()` 共 16 次，输出 `ALL 16 CHECKS PASSED`。
- README.md:9 的 24 小时令牌、默认账号 admin/admin123：app.py:24-26，导入打印 `86400`；登录返回 `must_change_password True`。
- README.md:18 的 Python ≥3.11 与 starlette 1.9.0：本次安装的 METADATA 为 `Requires-Python: >=3.11`。
- README.md:44-48 的环境变量：app.py:23-27 与 app.py:860。未设置时数据库路径是 app.py 旁的 `data\taskboard.db`，主机 `127.0.0.1`，日志端口 8000。
- README.md:10-14 的看板、三列、列操作、8 色标签、归档恢复：live_selftest 走通；颜色表 app.py:36 与 static/index.html:126 都是 8 个。
- README.md:69 的 MIT：LICENSE 第 1 行就是 `MIT License`。
- DECISIONS.md:28、DECISIONS.md:43 里的「15 项」是 2026-10-21 的历史记录。当前 README 写的是 16，和这次 pytest 一致。

## 许可证与署名核查

自洽，有一项未核实。

- LICENSE:1-3 是 MIT，版权行 `Copyright (c) 2026 taskboard contributors`。README.md:69 指向这个文件。
- README.md:5 写代码独立编写，署名见 UPSTREAM.md。UPSTREAM.md:3-8 写未复制上游代码，参考 `https://github.com/kanboard/kanboard`，commit `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`，许可证 MIT，署名 `Copyright (c) Frédéric Guillot`。
- NOTES.md:3-7 与 UPSTREAM 的对象、commit、许可证、署名行一致，并写明该署名行是逐字抄来的。
- 本仓库是 Python + 一个静态页，没有 Kanboard 的 PHP 源码树。这和「未复制上游代码、因此 LICENSE 只署本项目」对得上。两份版权人不同，是因为一个是本项目、一个是设计参考，不是互相否定。
- commit 是否仍是上游 HEAD、署名行是否与上游 LICENSE 逐字相同：任务禁止抓取外网，**未核实**。本次不改 LICENSE，不改 UPSTREAM.md。

## 分级修复清单

### P0

无。服务能起，测试能过。

### P1

无。删列/删看板会级联清掉卡片（探针计数为 0）。会话入库是 SHA-256（长度 64，明文不在库里）。未登录接口 401。文档页 404。安全头在真实响应里存在。

### P2

1. **P2-1** `static/index.html:164`。改密标签只写「至少 6 位」。修法：改成「新密码（6–1024 位）」，与 README.md:9 和 app.py:287-290 对齐。
2. **P2-2** `static/index.html:398`。归档日期取 UTC 时间字符串前 10 位；app.py:70-75 用 `timezone.utc` 生成该字符串。探针里的 `updated_at` 是 `2026-10-21T17:32:29+00:00`，切片为 `2026-10-21`，当时本机是 `2026-10-22T01:34:59+08:00`（中国标准时间），页面会显示前一天。到期高亮已经按本地日历日比较（static/index.html:234-237）。修法：归档日期也按本地年月日显示。
3. **P2-3** `requirements-dev.txt:2`（httpx==0.28.1）。pytest 警告 `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead`，出处是已安装的 `fastapi/testclient.py:1`。修法：不改这个钉死版本；测试是通过的，只是弃用警告。DECISIONS.md:67 已经决定不为此升级。

以下按仓库里已有决定保持现状，不升成 P1，本轮也不改：

- 首次登录只提示改密，不拦截业务接口。DECISIONS.md:23、DECISIONS.md:69。
- 登录不限速。DECISIONS.md:61、DECISIONS.md:80。app.py:228。
- CSP 只设 `frame-ancestors 'none'`。DECISIONS.md 里写明保持这样；本次响应头与 app.py:57-59 一致。
- 新建卡片的 position 用 `MAX+1`，没有包进 `BEGIN IMMEDIATE`。DECISIONS.md:77 记为单用户场景暂缓。app.py:658-662。
