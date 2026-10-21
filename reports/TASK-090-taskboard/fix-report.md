# taskboard 修复记录

P0 为 0，P1 为 0。按任务只修这两级，所以没有改仓库源码。P2 共 9 条留在 `review.md`，本轮不修。

## 修复条目

无。没有问题编号对应的代码改动，也就没有「改了哪个文件」的条目。

P2 不修的原因：

- P2-1：测试已通过，只是弃用警告。`requirements-dev.txt:2` 的 httpx 版本在没有依赖冲突时不许改。
- P2-2、P2-3：`DECISIONS.md` 已定口径，默认只听本机；P2-3 再改会顶上现有测试。
- P2-4、P2-6、P2-7、P2-8：不是跑不起来，也不是已经发生的越权或数据损坏。
- P2-5：当前解析已经是 starlette 1.9.0，不许顺手钉版本。
- P2-9：测试文件不许改。

## 全量测试

审查结束、确认不改源码之后重跑。工作目录 `E:\muse-bridge\in\TASK-090-taskboard`。临时目录指到 `E:\muse-bridge\work\TASK-090-taskboard`。

命令：

```
E:\muse-bridge\work\TASK-090-taskboard\venv\Scripts\python.exe -m pytest tests/ -q -p no:cacheprovider
```

退出码 0。结果行：

```
................                                                         [100%]
============================== warnings summary ===============================
..\..\work\TASK-090-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-090-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 2.69s
```

没有失败用例。那 1 条是依赖弃用警告，不是断言失败。

命令：

```
E:\muse-bridge\work\TASK-090-taskboard\venv\Scripts\python.exe E:\muse-bridge\in\TASK-090-taskboard\tests\live_selftest.py
```

退出码 0。结果行：

```
ALL 16 CHECKS PASSED
```

## git status

收尾命令（仓库目录 `E:\muse-bridge\in\TASK-090-taskboard`）：

```
git status --porcelain
```

输出为空，退出码 0。工作区没有源码改动。空输出是因为 P0/P1 没有落盘修改，不是改动丢失。
