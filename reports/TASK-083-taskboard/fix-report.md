# taskboard 修复报告

结论：review.md 的分级清单里 P0 为 0 条、P1 为 0 条。本轮只允许修这两级，所以没有改仓库源码。P2 共 9 条，全部保持不动。

## P0

无条目。没有对应的文件改动。

## P1

无条目。没有对应的文件改动。

清单里点名、但明确不升到 P1 的两项也没改：

- 默认口令只提示不强制。位置 DECISIONS.md:23、app.py:308-313。修法本来是业务接口在未改密时返回 403。不改的原因：这是已记录的产品决定；tests/test_app.py:30-33 的夹具在未改密时就调用看板接口，改了会弄红测试，而测试文件不许改。
- 登录不限速。位置 app.py:223、DECISIONS.md:61。不改的原因：既有决定写明维持现状，默认监听地址是 127.0.0.1（本次真服务日志 `Uvicorn running on http://127.0.0.1:8000`）。

## P2（未改）

| 编号 | 文件:行号 | 改法（未执行） | 原因 |
| --- | --- | --- | --- |
| P2-1 | static/index.html:164 | 改密标签写成「6–1024 位」 | 文案问题，不阻断，不属于 P0/P1 |
| P2-2 | README.md:9 | 补旧密码超过 1024 位也会拒绝，对应 app.py:282-283 | 文档少写，后端行为已正确 |
| P2-3 | requirements-dev.txt:2 | 增加 httpx2 消除 TestClient 弃用警告 | DECISIONS.md:60 已决定不修；pytest 16 项通过，只是 1 条警告 |
| P2-4 | app.py:233-236 | 用户不存在时补一次等长哈希比较 | 单用户且用户名写在 README，默认只听本机 |
| P2-5 | app.py:174-180 | 初始口令入库前拒绝空串和超长值 | 默认 admin123 可登录，只在改环境变量时才会踩到 |
| P2-6 | app.py:680 | 已归档卡片拒绝 PUT | 仍要登录，且只能改自己的卡，不是越权 |
| P2-7 | app.py:851 | PORT 非数字时打印并退出 | 默认 8000 已启动成功 |
| P2-8 | tests/live_selftest.py:2 | 注释改成「主流程」 | 禁止改测试文件 |
| P2-9 | requirements.txt:1 | 钉死 starlette==1.9.0 | 本次安装已解析到 1.9.0，没有依赖冲突；任务不许在无冲突时改已有版本 |

## 全量测试（清单确定为不改源码之后重跑）

命令：

```text
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe -m pytest tests -q --tb=short -p no:cacheprovider
E:\muse-bridge\work\TASK-083-taskboard\venv\Scripts\python.exe E:\muse-bridge\in\TASK-083-taskboard\tests\live_selftest.py
```

工作目录：`E:\muse-bridge\in\TASK-083-taskboard`。由 `run_final.py` 串起来跑，TEMP/TMP 指向工作目录。

pytest 结果行：

```text
16 passed, 1 warning in 3.47s
EXIT 0 ELAPSED_S 4.76
```

警告原文仍是：`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.` 没有失败用例。

live_selftest 结果行：

```text
ALL 16 CHECKS PASSED
EXIT 0 ELAPSED_S 2.35
```

`FINAL_FAIL 0`。没有失败项需要解释。

## git status --porcelain

命令：

```text
git -C E:\muse-bridge\in\TASK-083-taskboard status --porcelain
```

输出原样（标准输出 0 行，退出码 0）：

```text

```

输出为空，是因为本轮没有修改仓库里的文件。审查开始时这条命令同样是空的。review.md、run.md、fix-report.md 写在 `E:\muse-bridge\out\TASK-083-taskboard\`，不在待审仓库内。不存在「改动丢失需要改回」的文件。
