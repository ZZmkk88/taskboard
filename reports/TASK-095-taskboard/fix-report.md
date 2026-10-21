# taskboard 修复记录

P0 共 0 条，P1 共 0 条。按清单没有要改的源码，仓库文件未动。P2 共 9 条，任务只修 P0/P1，这 9 条不改。

## 问题编号

无 P0、无 P1 编号。没有「改了哪个文件」。

未改原因：审查时服务能启动，pytest 与真服务自测都通过；权限、级联删除、令牌存储、口令长度的抽查结果与实现一致。详见 `review.md` 的分级修复清单。P2 若改动，会碰到钉死的依赖版本、既有测试所依赖的默认口令，或纯文案，超出本轮范围。

未改文件包括：`tests/`、`requirements.txt`、`requirements-dev.txt`、`LICENSE`、`UPSTREAM.md`、`app.py`、`static/index.html`、`README.md`。

## 全量测试（清单确定且未改源码之后）

命令：

    E:\muse-bridge\in\TASK-095-taskboard\.venv\Scripts\python.exe E:\muse-bridge\work\TASK-095-taskboard\rerun_tests.py

工作目录为仓库根。脚本将 `TEMP`/`TMP` 设为 `E:\muse-bridge\work\TASK-095-taskboard`。

pytest 结果行：

    16 passed, 1 warning in 3.55s
    PYTEST_EXIT 0 seconds 4.76

警告原文：

    StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.

live_selftest 结果行：

    ALL 16 CHECKS PASSED
    LIVE_EXIT 0 seconds 2.46

没有失败项。弃用警告与修前相同，来自第三方 `fastapi\testclient.py:1`，不是用例失败。

## git status

命令：

    git status --porcelain

退出码：0

输出为空（下面代码块里没有任何行）：

```
```

空输出是因为没有改仓库里的跟踪文件。`.venv/`、`__pycache__/`、`.pytest_cache/`、`*.db` 在 `.gitignore` 里。虚拟环境在仓库的 `.venv`，探测数据库在 `E:\muse-bridge\work\TASK-095-taskboard\probe.db`。
