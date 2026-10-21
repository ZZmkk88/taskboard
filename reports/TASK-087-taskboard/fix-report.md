# taskboard 修复记录

结论：`review.md` 分级清单里 P0 0 项、P1 0 项。没有改仓库源码。P2 五项按清单不修。

## 问题编号

无可实施的 P0 / P1。

| 编号 | 文件:行号 | 改法 | 验证 | 原因 |
| --- | --- | --- | --- | --- |
| P0 | 无 | 未改 | 见下方全量测试 | 安装、pytest、真服务自测、8000 首页均已跑通，没有阻断项 |
| P1 | 无 | 未改 | 见下方全量测试 | 未发现未授权访问、越权或删数据后残留。归属检查、令牌哈希、文档页关闭、安全响应头均在审查中核对过 |
| P2-1 | `requirements-dev.txt:2` | 未改 | pytest 仍出现 StarletteDeprecationWarning，但 `16 passed` | 修法是升级 httpx。禁止改已钉版本；`DECISIONS.md:67` 已关闭 |
| P2-2 | `app.py:293-312` | 未改 | 审查探针：新旧密码同为 admin123 时改密返回 200，`must_change_password` 变为 false。未再改代码，故未重跑该探针 | 只清提示、不增加权限。`DECISIONS.md:23` 规定该标志不拦截业务 |
| P2-3 | `static/index.html:398` | 未改 | 未改代码，无新的失败测试。依据是源码切片与自测时间戳 `2026-10-21T17:06:19+00:00` | 归档箱日期文案问题，不阻断、不丢数据 |
| P2-4 | `app.py:658-677` | 未改 | 现有移动/建卡测试通过 | `DECISIONS.md:77` 暂缓。单用户本机 |
| P2-5 | `requirements.txt:1-2` | 未改 | 本次安装的 starlette 仍是 1.9.0，与 README 一致 | `DECISIONS.md:82` 决定不钉。当前没有版本冲突 |

未改测试，未改断言，未加 skip，未改 `LICENSE` 与 `UPSTREAM.md`。

## 全量测试

审查结束后重跑。工作目录 `E:\muse-bridge\in\TASK-087-taskboard`。解释器 `E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe`。

命令：

```
E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe -m pytest tests/ -q
```

输出（exit 0）：

```
................                                                         [100%]
============================== warnings summary ===============================
..\..\work\TASK-087-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-087-taskboard\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 2.74s
```

没有失败项。那条警告是依赖弃用提示，见 P2-1，不记为测试失败。

命令：

```
E:\muse-bridge\work\TASK-087-taskboard\.venv\Scripts\python.exe tests/live_selftest.py
```

输出（exit 0）：

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {'token': '<redacted>', 'username': 'admin', 'must_change_password': True}
PASS 首次登录提示改密
PASS 建看板成功 | {"id":1,"name":"自测看板","created_at":"2026-10-21T17:06:19+00:00","updated_at":"2026-10-21T17:06:19+00:00","column_count":3
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

命令：

```
git -C E:\muse-bridge\in\TASK-087-taskboard status --porcelain
```

输出（原样，exit 0，无行）：

```
```

porcelain 为空是因为本轮没有改仓库文件，与开工时的干净工作区一致，不是改动丢失。报告在 `E:\muse-bridge\out\TASK-087-taskboard\`，不在该仓库里。
