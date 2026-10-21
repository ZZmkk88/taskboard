# taskboard 验收报告

结论：仓库能在本机跑通。pytest **16 passed**（3.56s，1 条依赖弃用警告）；真服务自测 **ALL 16 CHECKS PASSED**；`http://127.0.0.1:8000/` 返回 **200**，正文是看板页。P0 0 项，P1 0 项，未改源码。

HEAD `8f930ba`。开工时 `git status --porcelain` 为空。

## 本地跑通记录

本机 `python --version` 为 `Python 3.11.9`。README 写的 Windows 启动器 `py -m venv` 失败，原文：

```
Unable to create process using 'E:\python.exe -m venv E:\muse-bridge\work\TASK-087-taskboard\.venv': ???????????
```

这是本机 `py` 指向缺失的 `E:\python.exe`，记为环境限制。随后用 `python -m venv` 在 `E:\muse-bridge\work\TASK-087-taskboard\.venv` 建环境，依赖与数据库都放在该目录，仓库内未落 `.venv` 或 `data/`。

安装（exit 0）：

```
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

装上 `fastapi-0.156.4`、`uvicorn-0.54.0`、`starlette-1.9.0`、`httpx-0.28.1`、`pytest-9.1.1`。`starlette-1.9.0.dist-info\METADATA` 第 26 行：`Requires-Python: >=3.11`。

pytest（仓库根目录，exit 0）：

```
.venv\Scripts\python.exe -m pytest tests/ -q
................                                                         [100%]
16 passed, 1 warning in 3.56s
```

警告原文：`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`（来自已安装的 `fastapi\testclient.py:1`）。

真服务自测（exit 0，令牌已由脚本打成 `<redacted>`）：

```
.venv\Scripts\python.exe tests/live_selftest.py
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功
...
PASS 看板改名
ALL 16 CHECKS PASSED
```

按 README 起服务：进程日志 `Uvicorn running on http://127.0.0.1:8000`。`GET /` → 200，`content-type: text/html; charset=utf-8`，正文含 `<title>taskboard · 项目看板</title>`，并带 `X-Frame-Options: DENY`、`Content-Security-Policy: frame-ancestors 'none'`、`X-Content-Type-Options: nosniff`。`POST /api/login`（admin / admin123）→ 200，`must_change_password: true`。未登录 `GET /api/boards` → 401。`/docs`、`/redoc`、`/openapi.json` → 404。`/health` 与 `/api/health` → 404（代码里没有这两条路由，见 `app.py` 路由表）。访问日志无口令、无令牌。查完已停进程；`netstat` 上 8000 无 LISTENING。

前端拖拽、确认框没有在浏览器里点击。接口主流程以 live_selftest 为准，页面行为以 `static/index.html` 源码为准。

## README 与实际不符处

未发现 README 陈述与当前代码或本次实测矛盾。核对过的主张如下。

| 主张 | README | 代码 / 实测 |
| --- | --- | --- |
| 16 项后端测试 | README.md:7、README.md:54 | `tests/test_app.py` 有 16 个 `test_*`（自第 65 行起）；pytest 输出 `16 passed` |
| 自测 16 个检查点，主流程含建看板、建卡、移动、归档、恢复 | README.md:55 | `tests/live_selftest.py:50-110` 共 16 次 `check(`；输出 `ALL 16 CHECKS PASSED` |
| 令牌 24 小时；默认 admin / admin123；首次提示改密；新密码 6–1024 位；登录口令超过 1024 位拒绝 | README.md:9 | `app.py:24-26`、`app.py:228-231`、`app.py:287-290`。探针：1024 位口令 → 401（进入校验），1025 位 → 400 |
| 新看板三列「待办 / 进行中 / 已完成」 | README.md:10 | `app.py:35`；自测 `['待办', '进行中', '已完成']` |
| 删列连带卡片并先确认；确认文案含归档数 | README.md:11 | 删列 `app.py:609-616`（外键 CASCADE）；确认框 `static/index.html:340-348`。探针删看板后 boards/columns/cards 计数均为 0 |
| 8 色标签、到期高亮、逾期变红 | README.md:12 | `app.py:36` 与 `static/index.html:126` 同为 8 色；高亮在 `static/index.html:239-246`（本地日历日） |
| 拖拽与 ◀▶↑↓ 共用移动接口 | README.md:13 | 投放 `static/index.html:295-302`；按钮 `static/index.html:327-330`；接口 `app.py:739-774` |
| 归档后可见原列，恢复到原列末尾，可彻底删除 | README.md:14 | `app.py:779-843`；自测「归档箱里有 1 张且记着原列」「恢复后回到待办末尾」 |
| Python ≥3.11，因为 starlette 1.9.0 要求 ≥3.11 | README.md:18 | 本次解析 `starlette-1.9.0`，METADATA 第 26 行 `Requires-Python: >=3.11`。版本未写进 `requirements.txt`，见 P2-5 |
| 环境变量默认值 | README.md:44-48 | `app.py:23-27`、`app.py:860`。自测只改了 `PORT=8131`，仍连上 `127.0.0.1` |
| 启动地址 http://127.0.0.1:8000 | README.md:38 | 进程日志与 `GET /` 200 |
| 多用户、评论、子任务、附件、泳道、搜索、导入导出当前没有 | README.md:60-65 | `app.py` 无对应路由或表 |
| 许可证 MIT | README.md:68 | `LICENSE:1` 为 MIT License |

`/health` 返回 404 不记为不符：README 没有健康检查路径。本机 `py` 启动器失败不记为仓库缺陷。

## 许可证与署名核查

仓库内部自洽，未改 `LICENSE` 与 `UPSTREAM.md`。

- `LICENSE:1-3`：MIT License，版权行 `Copyright (c) 2026 taskboard contributors`。`README.md:68` 指向该文件。
- `UPSTREAM.md:3-9`：本项目代码独立编写、未复制上游；参考 `https://github.com/kanboard/kanboard`，commit `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`，上游许可证 MIT，署名 `Copyright (c) Frédéric Guillot`。
- `NOTES.md:5-7` 与 UPSTREAM 的 commit、署名字符串一致，并写明该署名「已逐字抄进 UPSTREAM.md」。两处字符串相同。
- 在仓库 `*.py`、`*.html`、`*.md`、`*.txt` 中检索 Guillot / kanboard / Copyright，命中只在 `NOTES.md` 与 `UPSTREAM.md`。`app.py` 与 `static/index.html` 无上游文件头，也没有 PHP 源码。这与「独立编写、另附上游参考署名」一致：项目版权行与上游署名各管各的作品，不互相覆盖。

上游 commit 是否仍是默认分支头、LICENSE 是否只有这一行、版本号 1.2.54：未联网复核（本任务禁止抓取外网页面）。因此不把 NOTES 里的「已逐字」「最新版本 1.2.54」写成经外部证实的事实，也不据此改 LICENSE / UPSTREAM。

运行依赖的许可证随 site-packages 走（例如已安装的 Starlette METADATA 为 `License-Expression: BSD-3-Clause`）。项目 LICENSE 只声明本仓库代码，与 UPSTREAM 的分工不冲突。

## 分级修复清单

### P0 跑不起来 / 阻断

无。安装、pytest、真服务自测、8000 端口首页均已跑通。

### P1 安全 / 数据 / 权限

无。未登录接口返回 401；看板 / 列 / 卡片查询带 `user_id` 归属（如 `app.py:354-384`）；会话令牌以 SHA-256 入库（`app.py:273-275`，测试 `tests/test_app.py:112`）；删看板后子表行数为 0；`/docs`、`/redoc`、`/openapi.json` 为 404（`app.py:45-50`）；安全响应头在真服务上存在（`app.py:54-63`）。

以下项按 `DECISIONS.md` 已关闭，不升为 P1：首次改密只提示、不拦截业务（`DECISIONS.md:23`，`DECISIONS.md:69`）；登录不限速（`DECISIONS.md:81`，默认只听 `127.0.0.1`，`app.py:27`）；CSP 只保留 `frame-ancestors`（`DECISIONS.md:82`，`app.py:58`）。

### P2

本轮不改 P2。

1. **P2-1 测试弃用警告。** `requirements-dev.txt:2` 钉死 `httpx==0.28.1`，pytest 因此打出 StarletteDeprecationWarning。修法：换用 httpx2 或升级 httpx。不修：`DECISIONS.md:67` 已关闭，且禁止改已钉版本号。测试仍然通过。
2. **P2-2 改密允许新旧相同。** `app.py:293-312` 在旧密码正确后把 `must_change_password` 写成 0，没有比较新旧是否相同。探针：新旧都是 `admin123` 时返回 200，标志变为 false。修法：新旧相同则返回 400。不修：该标志不拦截接口（`DECISIONS.md:23`），清掉提示不增加权限。
3. **P2-3 归档日期显示跨日。** `static/index.html:398` 把 `updated_at` 切前 10 个字符。该字符串由 `app.py:74-75` 以 UTC `isoformat` 生成。自测样例 `2026-10-21T16:57:09+00:00`，东八区已是 2026-10-22，页面会显示 10-21。修法：按本地日历日格式化后再显示。不修：只影响归档箱上的日期文案，接口里的时间字段未错。
4. **P2-4 建卡序号的并发窗口。** `app.py:658-677` 先 `SELECT MAX(position)` 再 `INSERT`，中间没有 `BEGIN IMMEDIATE`。修法：把读改写放进立即事务。不修：`DECISIONS.md:77` 已暂缓；单用户本机；现有测试全过。
5. **P2-5 starlette 未钉版本。** `requirements.txt:1-2` 只钉了 fastapi 与 uvicorn。README.md:18 写的 1.9.0 与本次安装一致，日后解析变了这句话会失真。修法：在 requirements 中增加 `starlette==1.9.0`。不修：`DECISIONS.md:82` 决定本轮不动，当前没有漂移。

另登记、不新开：自测端口写死 `tests/live_selftest.py:14` 的 8131（测试文件禁止改，`DECISIONS.md:70`）。
