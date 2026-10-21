# 修复记录

结论：`review.md` 里没有 P0，也没有 P1。按任务只修这两级，所以仓库源码一个字都没改。P2 留在清单里，本轮不动。

## 逐条

### P0

无条目。没有「跑不起来 / 阻断」。

- 文件：无
- 改法：不改
- 原因：`requirements-dev.txt` 能装上；pytest `15 passed`；`live_selftest` `ALL 16 CHECKS PASSED`；`GET /` 200
- 验证：见下方全量重跑

### P1

无条目。没有要改的安全、数据或权限缺陷。

- 文件：无
- 改法：不改
- 原因：未登录 401；跨用户 404；删列/删看板后孤儿卡片数为 0；`/docs`、`/redoc`、`/openapi.json` 为 404；默认绑 `127.0.0.1`。默认口令不强制修改是 `DECISIONS.md:23` 的口径，强行拦截会让现有测试失败，而且任务不许改测试
- 验证：见 `review.md` 的抽查输出，以及下方全量重跑

### P2-1 至 P2-7

不改。任务只允许修 P0 和 P1，最多 5 项。这 7 条都是文案过满、刷新后不再 toast、缓存头、空字节、依赖弃用警告、过期会话不清理，都不阻断运行，也不是已经复现的越权或数据丢失。

| 编号 | 文件:行号 | 改法 | 结果 |
| --- | --- | --- | --- |
| P2-1 | `README.md:7` | 未改。收紧「并通过测试」的说法 | 不在本轮范围 |
| P2-2 | `README.md:55` | 未改。去掉「完整流程」或补上未覆盖项 | 不在本轮范围 |
| P2-3 | `static/index.html:410` | 未改。恢复会话时若仍须改密就再提示一次 | 不在本轮范围 |
| P2-4 | `app.py:54-59` | 未改。`/api/` 加 `Cache-Control: no-store` | 不在本轮范围 |
| P2-5 | `app.py:75-80` | 未改。拒绝标题里的 `\x00` | 不在本轮范围 |
| P2-6 | `requirements-dev.txt:2` | 未改。不能改已钉死的 httpx 版本 | 不在本轮范围 |
| P2-7 | `app.py:137-141` | 未改。清理过期会话行 | 不在本轮范围 |

## 全量测试（审查结束后重跑）

没有失败的测试。警告仍是依赖里的 httpx 弃用提示，不是断言失败。

命令：

```
E:\muse-bridge\work\TASK-056-taskboard\.venv\Scripts\python.exe -m pytest tests/ -q -p no:cacheprovider --tb=short
```

cwd：`E:\muse-bridge\in\TASK-056-taskboard`。exit 0。

```
...............                                                          [100%]
============================== warnings summary ===============================
..\..\work\TASK-056-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-056-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
15 passed, 1 warning in 2.06s
```

命令：

```
E:\muse-bridge\work\TASK-056-taskboard\.venv\Scripts\python.exe tests/live_selftest.py
```

cwd：仓库根。exit 0。登录响应里的一次性 token 已打码，其余与终端一致。

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {"token":"<redacted>","username":"admin","must_change_password":true}
PASS 首次登录提示改密
PASS 建看板成功 | {"id":1,"name":"自测看板","created_at":"2026-10-21T13:22:05+00:00","updated_at":"2026-10-21T13:22:05+00:00","column_count":3
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

## git status --porcelain

在仓库根 `E:\muse-bridge\in\TASK-056-taskboard` 执行。exit 0。标准输出没有任何一行（原样就是空）：

```
git status --porcelain
```

输出：

（空）

空输出表示工作区相对 HEAD 没有改动。本次没有改仓库文件，所以不是改动丢失。`review.md`、`run.md`、`fix-report.md` 在 `E:\muse-bridge\out\TASK-056-taskboard\`，不在这个 git 仓库里。
