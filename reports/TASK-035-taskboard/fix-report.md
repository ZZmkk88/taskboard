# taskboard 修复记录

结论：审查清单里 **P0 无、P1 无**。按任务只修这两级，P2 不改。仓库源码没有改动。

## 未改条目

### P0

无对应文件。服务能安装、pytest 与真服务自测能通过、8000 首页返回 200，进程已退出。见 `review.md` 本地跑通记录。

### P1

无对应文件。鉴权、级联删除、注入探针和文档页关闭的实测写在 `review.md`。没有要改的权限或数据损坏点。

### P2-1

- 文件：`README.md:54`
- 改法：未改。若要改，把「14 项」写成「15 项」。
- 原因：P2 文档数字，不阻断运行。任务只要求修 P0/P1。
- 验证：未改文件，无单独补丁测试。全量结果见文末。

### P2-2

- 文件：`app.py:44`
- 改法：未改。若要改，加上 `openapi_url=None`。
- 原因：`GET /openapi.json` 匿名返回 200，但正文没有默认口令，也不加载外部脚本。首页脚本同样匿名可访问。定为 P2。
- 验证：未改文件。此前 `run_server_check.py` 已看到 `GET /openapi.json status=200`。

### P2-3

- 文件：`app.py:257`、`app.py:219`
- 改法：未改。若要改，哈希前拒绝过长密码。
- 原因：默认只听 `127.0.0.1`，不构成当前跑通或越权问题。
- 验证：未改文件。

### P2-4

- 文件：`app.py:219`、`app.py:259`
- 改法：未改。若要改，哈希比较换成 `secrets.compare_digest`。
- 原因：比较的是等长十六进制哈希，不升到 P1。
- 验证：未改文件。

### P2-5

- 文件：`app.py:683`、`app.py:739`、`app.py:758`
- 改法：未改。若要改，这三处在提交前调用 `_touch_board`。
- 原因：只影响看板 `updated_at`，卡片数据还在。
- 验证：未改文件。

### P2-6

- 文件：`app.py:25-26`、`README.md:9`、`DECISIONS.md:23`
- 改法：未改。保持默认口令 `admin` / `admin123`，只提示改密。
- 原因：`DECISIONS.md:23` 写明这是已确认口径。改成强制改密或换掉默认口令会和现有登录测试冲突。
- 验证：未改文件。pytest 里 `test_login_ok_and_must_change` 与改密往返仍然通过，见文末。

### P2-7

- 文件：`tests/test_app.py:13`、`requirements-dev.txt:2`
- 改法：未改。保持 `httpx==0.28.1`。
- 原因：只是 Starlette 弃用警告，测试 exit 0。任务禁止改测试，也禁止在没有依赖冲突时改版本号。
- 验证：文末 pytest 仍是 `15 passed, 1 warning`。

### P2-8

- 文件：`app.py:51`
- 改法：未改。CSP 维持 `frame-ancestors 'none'`。
- 原因：页面脚本是内联的，再收紧要配 `unsafe-inline`。点击劫持相关的两个头本次响应里已经有。
- 验证：未改文件。此前首页响应含 `X-Frame-Options: DENY` 与该 CSP。

## 全量测试

未改代码之后重跑。工作目录脚本把 TEMP 放在 `E:\muse-bridge\work\TASK-035-taskboard`，并 chdir 到仓库根。

命令：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_pytest.py
```

输出（exit 0）：

```
...............                                                          [100%]
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
15 passed, 1 warning in 2.22s
```

命令：

```
E:\muse-bridge\work\TASK-035-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-035-taskboard\run_live.py
```

输出（exit 0，令牌已截断）：

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {"token":"8CpaHbpZ…(已截断)","username":"admin","must_change_password":true}
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

没有失败项。弃用警告仍在，按 P2-7 不处理。

## git status --porcelain

在仓库 `E:\muse-bridge\in\TASK-035-taskboard` 执行：

```
git status --porcelain
```

输出为空（命令 exit 0，没有任何文件行）。

```
git diff --stat
```

输出同样为空。

空输出是预期：清单里没有 P0/P1，所以没有改仓库文件，不存在「改动丢失」。报告在 `E:\muse-bridge\out\TASK-035-taskboard\`，不在这个 git 仓库里。
