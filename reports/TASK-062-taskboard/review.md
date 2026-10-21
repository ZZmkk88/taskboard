# taskboard 验收

结论：在本机 Python 3.11.9 上能跑通。pytest **15 passed**（第一次 4.68 秒，收尾重跑 2.52 秒），真服务自测 **ALL 16 CHECKS PASSED**。默认 `http://127.0.0.1:8000/` 返回 200，正文是看板页。没有独立健康检查路由，`/health` 为 404。P0 0 条，P1 0 条，未改仓库源码。

本会话没有浏览器。拖拽、确认框、到期颜色只核对了 `static/index.html` 源码。

## 本地跑通记录

依赖装在 `E:\muse-bridge\work\TASK-062-taskboard\venv`。`requirements-dev.txt:1` 的 `-r requirements.txt` 把运行依赖一起装上。完整命令和输出在 `run.md`。

本机 `py` 启动器失败（README 的 Windows 安装第一步）。原文：

```
Unable to create process using 'E:\python.exe -m venv E:\muse-bridge\work\TASK-062-taskboard\venv-py-test': ???????????
```

`python --version` 为 `Python 3.11.9`。改用 `python -m venv` 后，pip exit 0，装上 fastapi 0.156.4、uvicorn 0.54.0、httpx 0.28.1、pytest 9.1.1、starlette 1.9.0。

pytest（工作目录为仓库根）：

```
15 passed, 1 warning in 4.68s
```

警告原文：`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.` 来自已安装的 `fastapi/testclient.py:1`。15 项仍通过。

真服务自测 `tests/live_selftest.py`（端口 8131）16 条 PASS，末行 `ALL 16 CHECKS PASSED`，耗时 3.06 秒。登录 JSON 里的 token 已从记录中省略。

默认配置起 `python app.py`（未设置 `PORT` / `TASKBOARD_HOST`，库在工作目录）：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:58350 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:58351 - "GET /health HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:58357 - "GET /api/me HTTP/1.1" 401 Unauthorized
```

`/docs`、`/redoc`、`/openapi.json` 均为 404。首页原始响应含 `content-type: text/html; charset=utf-8`、`x-frame-options: DENY`、`content-security-policy: frame-ancestors 'none'`、`x-content-type-options: nosniff`。`/api/me` 另有 `cache-control: no-store`。

`100.69.58.124:8000` 与 `192.168.31.86:8000` 连接超时，且能在这两块地址上另行绑定 8000。默认监听停在 127.0.0.1。查完后进程已退出。收尾 netstat 对 8000 和 8131 `NO_ROWS`。

抽查（库在工作目录，命令见 `run.md` 第 8–9 节）：令牌有效期实测 `86400.0` 秒；口令哈希长度 64（`PASS password not plaintext | len=64`）；退出只使当前令牌失效；过期令牌 401；删看板/删列后孤立卡片 0；第二个用户的看板 admin 令牌全部 404，库里名称仍是 `secret-board`。空值和超长名称返回 422 或 400，响应里没有 Traceback。

## README 与实际不符处

核对过且与代码一致的，不重复列进不符清单：15 项测试（`README.md:54`，pytest `15 passed`）、16 个检查点（`README.md:55`，`ALL 16 CHECKS PASSED`）、默认三列（`README.md:10`，`app.py:35`）、令牌 24 小时（`README.md:9`，`app.py:24`，实测 86400 秒）、默认账号（`README.md:9`，`app.py:25-26`）、五个环境变量的默认值（`README.md:44-48`，`app.py:23-27` 与 `app.py:846`）、MIT（`README.md:68`，`LICENSE:1`）。

1. 拖拽投放区小于「任意位置」。`README.md:13` 写「鼠标拖拽卡片到目标列的任意位置放下」。`static/index.html:291-293` 只在 `.cardList` 上监听 drop，`static/index.html:54` 把空列表的 `min-height` 设为 12px。列头、加卡片按钮和列的内边距不接收放下。有卡片时，在卡片列表内部可以按纵坐标插入到任意序号。
2. 密码长度写在代码和页面上，README 的登录说明没写。`README.md:9` 只给了默认账号。`static/index.html:164` 写新密码至少 6 位。`app.py:273-277` 拒绝短于 6 或长于 1024 的新密码。`app.py:34` 与 `app.py:225-226` 拒绝长于 1024 的登录口令。抽查 `"a"*1025` 返回 400 `密码太长了`。
3. Python 下限和本次解析到的 starlette 元数据不一致。`README.md:18` 写「需要 Python 3.10 以上」。本机 3.11.9 上 pip 装到的 starlette 1.9.0，其 `METADATA:26` 为 `Requires-Python: >=3.11`（文件在工作目录 venv 的 `starlette-1.9.0.dist-info`）。同一环境里 fastapi 0.156.4 的 `METADATA:39` 仍是 `Requires-Python: >=3.10`。本机没有 Python 3.10，没有实测 3.10 会不会被解析到旧版 starlette 后装上。

`py` 启动器失败记在跑通记录里，是本机启动器指向 `E:\python.exe`，README 的 `py -m venv` 写法本身与代码无关。

## 许可证与署名核查

仓库内几处声明彼此一致。

- `LICENSE:1-3`：MIT License，`Copyright (c) 2026 taskboard contributors`。正文是通用 MIT 许可文本。
- `README.md:68`：MIT，见 LICENSE。
- `README.md:5`：代码由本项目独立编写，来源与署名见 UPSTREAM.md。
- `UPSTREAM.md:4`：未复制上游代码。`UPSTREAM.md:6-9`：`https://github.com/kanboard/kanboard`，commit `e4fb64e972b0ae255a92cf4b7b03489846ebbffc`，license MIT，attribution `Copyright (c) Frédéric Guillot`。
- `NOTES.md:7` 的署名句与 `UPSTREAM.md:9` 字面相同。

`git ls-files` 里没有 PHP 或 Kanboard 源码，应用代码是 `app.py` 与 `static/index.html`。「未复制上游代码」只做到仓库内观察。上游 commit、版本号 1.2.54（`NOTES.md:5`）、上游 LICENSE 原文本次没有联网核对，标为未核实。任务禁止抓取外部页面。

没有发现仓库内部的事实冲突，因此未改 `LICENSE` 与 `UPSTREAM.md`。项目自己的版权行是 taskboard contributors；上游署名写在 `UPSTREAM.md`，与「只参考设计、代码独立编写」的说法放在一起，内部是自洽的。上游说法是否属实，未核实。

## 分级修复清单

### P0

无。本机按上面的步骤可以安装、通过 15 项测试、通过 16 个自测点，并在 127.0.0.1:8000 返回首页 200。

### P1

无。抽查覆盖了默认只监听本机、文档页关闭、口令哈希、登录错误不区分用户名是否存在、退出与过期令牌、改密吊销其他会话（`tests/test_app.py:110-130` 已通过）、跨用户看板/列/卡片拒绝、删列删看板后无孤立卡片。`.gitignore:2` 与 `.gitignore:6` 忽略 `data/` 和 `*.db`。

默认口令 `admin` / `admin123`（`app.py:25-26`，`README.md:9`）按 `DECISIONS.md:23` 只提示改密、不拦截业务接口。自动化测试依赖这一行为。本次实测服务没有绑到局域网地址。不列入待修。

### P2

1. `README.md:13` 与 `static/index.html:54`、`static/index.html:291-293`。修法：把 dragover/drop 绑到整列，空列的投放区加高。
2. `README.md:9` 未写密码长度；规则在 `app.py:225-226`、`app.py:273-277`、`static/index.html:164`。修法：README 补上一句，新密码 6 到 1024 位，登录口令超过 1024 位拒绝。
3. `README.md:18` 写 Python 3.10 以上；本次装到的 starlette 1.9.0 `METADATA:26` 要求 `>=3.11`。修法：在 3.10 上实装一次，装不上再把 README 改成 3.11 以上。本次未改。
4. pytest 警告要求改用 httpx2；`requirements-dev.txt:2` 钉死 `httpx==0.28.1`。`DECISIONS.md:46` 写明这个警告不修。修法：保持钉死版本，测试已通过，没有版本冲突。
5. `tests/live_selftest.py:53` 把登录响应前 120 个字符打到标准输出，其中有令牌。修法：打印时去掉 token。本任务禁止改测试文件，不修。
6. `app.py:223-236` 登录没有失败次数限制。修法：对连续失败做内存计数。默认只听 127.0.0.1，本次不修。
7. `app.py:140-144` 与 `app.py:238-241` 把会话令牌明文写入 `sessions`。修法：库里改存令牌哈希。`.gitignore:6` 已忽略 `*.db`，本次不修。
8. `static/index.html:239-245` 的到期文案没有走 `esc()`。`app.py:86-97` 只接受 `YYYY-MM-DD`，当前接口写不进 HTML 标签。修法：到期文案先 `esc()` 再插入。

本次只允许修 P0 和 P1，最多 5 项。上面 8 条都是 P2，未改代码。
