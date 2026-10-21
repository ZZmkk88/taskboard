# 修复报告

P0、P1 均为 0（见 review.md「分级修复清单」）。没有改仓库里的任何文件。P2 三条按任务范围不修。

## 条目

无 P0/P1 条目。

| 项 | 内容 |
| --- | --- |
| 问题编号 | 无 |
| 文件:行号 | 未改 |
| 改法 | 未改。清单里没有跑不起来、阻断、安全、数据或权限方面要动代码的项 |
| 验证 | 见下方全量重跑 |

P2 不修的原因：

- P2-1 `static/index.html:398` 只影响归档日期的显示，库存的是完整 ISO 时间。
- P2-2 `static/index.html:164` 是文案缺了上限，后端已经拒绝超长新密码。
- P2-3 `requirements-dev.txt:2` 钉死了 `httpx==0.28.1`。警告不导致失败，任务禁止改已有依赖版本号（除非冲突）。这里没有冲突。

## 全量测试（确认清单之后重跑）

命令：

```
E:\muse-bridge\work\TASK-078-taskboard\venv\Scripts\python.exe -B -m pytest E:\muse-bridge\in\TASK-078-taskboard\tests -q -p no:cacheprovider --rootdir E:\muse-bridge\in\TASK-078-taskboard
```

退出码 0。输出：

```
................                                                         [100%]
============================== warnings summary ===============================
..\..\work\TASK-078-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1
  E:\muse-bridge\work\TASK-078-taskboard\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
16 passed, 1 warning in 2.36s
```

命令：

```
E:\muse-bridge\work\TASK-078-taskboard\venv\Scripts\python.exe -B E:\muse-bridge\in\TASK-078-taskboard\tests\live_selftest.py
```

退出码 0。输出：

```
PASS 首页能打开且是 taskboard 页面
PASS 默认账号登录成功 | {'token': '<redacted>', 'username': 'admin', 'must_change_password': True}
PASS 首次登录提示改密
PASS 建看板成功 | {"id":1,"name":"自测看板","created_at":"2026-10-21T16:26:28+00:00","updated_at":"2026-10-21T16:26:28+00:00","column_count":3
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

失败：无。唯一警告是上面的 httpx / Starlette 弃用，对应清单 P2-3，不改依赖。

## git status --porcelain

工作目录 `E:\muse-bridge\in\TASK-078-taskboard`。

命令：

```
git status --porcelain
```

退出码：0

输出原样（空，无任何行）：

```
```

P0/P1 为 0，仓库源码没有改动。空输出表示工作区本来就是干净的，不是改动写完又丢了。报告在 `E:\muse-bridge\out\TASK-078-taskboard\`，不在这个仓库里。
