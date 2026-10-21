# 修复报告

审查清单里 P0 为 0 条、P1 为 0 条。任务只修这两级，最多 5 项。本轮没有改仓库源码。P2 三条留在清单里，没有动手。

## P0

没有条目。没有对应文件可改。

## P1

没有条目。没有对应文件可改。

级联删除、会话哈希、未登录 401、文档页关闭、安全响应头都在审查阶段核对过，见 review.md「本地跑通记录」。这些不是待修缺陷。

## P2（未改）

### P2-1

- 文件：`static/index.html:164`
- 改法：未改。页面提示缺 1024 上限，后端 `app.py:287-290` 已经按这个上限拒绝。它不阻断启动，也不是安全或数据权限问题。
- 验证：无代码改动，不单跑这一条。全量结果见文末。

### P2-2

- 文件：`static/index.html:398`（时间来源 `app.py:70-75`）
- 改法：未改。归档日期显示可能在东八区凌晨差一天，库存的 UTC 时间本身是对的。不阻断，也不改已有数据。
- 验证：无代码改动。

### P2-3

- 文件：`requirements-dev.txt:2`
- 改法：未改。修它要动已钉死的 httpx 版本号。任务禁止改 requirements 里已有依赖的版本号，除非是依赖冲突。测试能通过，只是 `StarletteDeprecationWarning`。DECISIONS.md:67 也写了不为此升级。
- 验证：重跑 pytest 时警告仍在，16 项通过。见下方输出。

## 全量重跑

未改源码之后重跑。失败项：无。

命令：

```
E:\muse-bridge\in\TASK-098-taskboard\.venv\Scripts\python.exe -B E:\muse-bridge\work\TASK-098-taskboard\run_pytest.py
```

输出（退出码 0）：

```
................                                                         [100%]
============================== warnings summary ===============================
.venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\in\TASK-098-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 2.70s
```

命令：

```
E:\muse-bridge\in\TASK-098-taskboard\.venv\Scripts\python.exe -B E:\muse-bridge\work\TASK-098-taskboard\run_live.py
```

输出（退出码 0）：

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {'token': '<redacted>', 'username': 'admin', 'must_change_password': True}
PASS 首次登录提示改密
PASS 建看板成功 | {"id":1,"name":"自测看板","created_at":"2026-10-21T17:37:46+00:00","updated_at":"2026-10-21T17:37:46+00:00","column_count":3
PASS 自带三列 待办/进行中/已完成 | ['待办', '进行中', '已完成']
PASS 加一列成功 | {"id":4,"title":"待评审","position":3}
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

## git status

空输出是因为没有改过被跟踪的文件，不是改动写完又丢了。P0/P1 为空，P2 按任务不改，工作区里本来就没有需要留下的源码 diff。`.venv/` 和 `__pycache__/` 被 `.gitignore` 忽略，不会出现在 porcelain 里。

命令：

```
git status --porcelain
```

输出（退出码 0，无行）。下面这个代码块就是原样输出，里面没有字符：

```
```
