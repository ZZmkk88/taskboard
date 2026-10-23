# taskboard 修复记录

P0 0 条，P1 0 条。没有改仓库源码。P2 共 9 条，按审查清单不修。

清单在 `review.md` 末节。下面按编号说明。

## P0

无条目。服务与测试都跑通，没有「跑不起来 / 阻断」要改的文件。

## P1

无条目。跨用户访问、级联删除、令牌哈希、文档页、超长口令已在跑通记录里核对，没有要改的安全或数据缺陷。

## P2（未修）

1. 问题编号 P2-1。文件 `README.md:7`、`README.md:54`。未改。修法本是改测试计数的称呼。纯文案，不在 P0/P1 范围内。
2. 问题编号 P2-2。文件 `README.md:9`（对应行为在 `app.py:309-310`）。未改。补一句「新旧密码不能相同」即可，不在本次修复范围。
3. 问题编号 P2-3。文件 `README.md:12`、`README.md:14`（对应 `app.py:709-710`、`app.py:760-761`）。未改。补归档后的限制说明即可，不在本次修复范围。
4. 问题编号 P2-4。文件 `requirements-dev.txt:2`。未改。警告来自已安装的 `fastapi/testclient.py`，测试仍然 19 passed。要消警告就得动已钉死的 httpx 版本，而当前没有依赖冲突。
5. 问题编号 P2-5。文件 `app.py:489`、`static/index.html:156`。未改。改成「不改密不能用看板」会让 `tests/live_selftest.py:60` 失败，测试文件不许改。`DECISIONS.md:69` 已决定只提示、不拦截。
6. 问题编号 P2-6。文件 `app.py:240`。未改。`DECISIONS.md:80` 维持无限速，默认监听 `app.py:28` 的 `127.0.0.1`。
7. 问题编号 P2-7。文件 `app.py:672-676`。未改。`DECISIONS.md:101` 将并发取号标为暂缓。
8. 问题编号 P2-8。文件 `requirements.txt:1-2`。未改。本次安装解析到 starlette 1.9.0，与 README 一致，没有版本冲突。
9. 问题编号 P2-9。文件 `app.py:882`。未改。`DECISIONS.md:81` 保留默认 Server 响应头。

## 全量测试（审查结束后重跑）

工作目录 `E:\muse-bridge\in\TASK-103-taskboard`。解释器 `E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe`。

```
E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe -m pytest tests/ -q -o cache_dir=E:\muse-bridge\work\TASK-103-taskboard\pytest-cache
```

```
...................                                                      [100%]
============================== warnings summary ===============================
..\..\work\TASK-103-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-103-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
19 passed, 1 warning in 3.82s
```

exit 0。这 1 条是依赖弃用警告，不是失败。

```
E:\muse-bridge\work\TASK-103-taskboard\.venv\Scripts\python.exe tests/live_selftest.py
```

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {'token': '<redacted>', 'username': 'admin', 'must_change_password': True}
PASS 首次登录提示改密
PASS 建看板成功 | {"id":1,"name":"自测看板","created_at":"2026-10-23T16:03:41+00:00","updated_at":"2026-10-23T16:03:41+00:00","column_count":3
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

exit 0。没有失败项。

## git status

在 `E:\muse-bridge\in\TASK-103-taskboard` 执行。审查过程没有改仓库文件，空输出是预期结果，不是改动丢失。

```
git status --porcelain
```

```
```

exit 0，无输出。
