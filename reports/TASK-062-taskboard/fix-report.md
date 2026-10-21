# 修复报告

结论：`review.md` 清单里 P0 为 0 条、P1 为 0 条。任务只允许修这两级，最多 5 项。本次没有改仓库源码。

## P0

无条目。本机 pytest 与真服务自测均通过，`http://127.0.0.1:8000/` 返回 200。没有对应的文件改动。

## P1

无条目。跨用户访问、级联删除、口令哈希、监听地址的抽查记录在 `review.md` 的「本地跑通记录」和 `run.md` 第 6–8 节。没有对应的文件改动。

## 清单中的 P2（按任务不修）

每条都留在原文件，没有补丁。

1. 编号 P2-1。位置 `README.md:13`，`static/index.html:54`，`static/index.html:291-293`。修法：拖拽事件绑到整列并加高空列投放区。未改。原因：属于界面与文案差距，服务和测试都能跑。
2. 编号 P2-2。位置 `README.md:9`，`app.py:225-226`，`app.py:273-277`。修法：README 补上密码 6 到 1024 位。未改。原因：文档遗漏，接口行为已有测试覆盖。
3. 编号 P2-3。位置 `README.md:18`；已安装的 starlette 1.9.0 `METADATA:26` 写 `Requires-Python: >=3.11`。修法：先在 Python 3.10 上实装，确认失败再改 README。未改。原因：本机只有 3.11.9，没有 3.10 的失败证据。
4. 编号 P2-4。位置 `requirements-dev.txt:2`（`httpx==0.28.1`）。修法：保持现有版本。未改。原因：测试通过，只多一条弃用警告；`DECISIONS.md:46` 已决定不升级；任务禁止改已有依赖版本号，除非是依赖冲突。
5. 编号 P2-5。位置 `tests/live_selftest.py:53`。修法：标准输出里去掉令牌。未改。原因：任务禁止改测试文件。
6. 编号 P2-6。位置 `app.py:223-236`。修法：登录失败计数。未改。原因：默认绑定 127.0.0.1，已实测局域网地址连不上 8000。
7. 编号 P2-7。位置 `app.py:140-144`，`app.py:238-241`。修法：会话表存令牌哈希。未改。原因：数据库文件已被 `.gitignore:6` 忽略，威胁面是本机文件。
8. 编号 P2-8。位置 `static/index.html:239-245`。修法：到期文案经过 `esc()`。未改。原因：`app.py:86-97` 已限制日期格式，抽查写不进标签。

## 收尾全量测试

未改代码之后重跑。两次都从仓库根目录执行，临时目录在 `E:\muse-bridge\work\TASK-062-taskboard`。

命令：

```
E:\muse-bridge\work\TASK-062-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-062-taskboard\run_pytest.py
```

运行器打印的内层命令：

```
E:\muse-bridge\work\TASK-062-taskboard\venv\Scripts\python.exe -m pytest tests/ -q --tb=short -o cache_dir=E:\muse-bridge\work\TASK-062-taskboard\pytest_cache
```

exit: 0。结果行：

```
...............                                                          [100%]
============================== warnings summary ===============================
..\..\work\TASK-062-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-062-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
15 passed, 1 warning in 2.52s
```

警告与 P2-4 是同一条，15 项通过，不记为失败。

命令：

```
E:\muse-bridge\work\TASK-062-taskboard\venv\Scripts\python.exe E:\muse-bridge\work\TASK-062-taskboard\run_live.py
```

内层命令：`tests/live_selftest.py`。exit: 0。结果行（登录响应中的 token 已省略）：

```
ALL 16 CHECKS PASSED
ELAPSED_SEC 2.87
```

16 条检查均为 `PASS`，没有失败项。

审查脚本曾在仓库生成 gitignore 掉的 `__pycache__\app.cpython-311.pyc`。该字节码已删除。源码文件没有改动。

## git status --porcelain

命令：

```
git -C E:\muse-bridge\in\TASK-062-taskboard status --porcelain
```

输出：

```
```

（命令 exit 0，标准输出为空。仓库工作区没有未提交改动。）
