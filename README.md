# taskboard

一个本地运行的项目看板工具：用看板、列和卡片把手头的事排清楚，单用户使用，数据存在本地 SQLite 里，不依赖任何外部服务。

设计上学习了开源社区看板类工具的通行思路（看板分列、卡片流转），代码由本项目独立编写；来源与署名见 [UPSTREAM.md](UPSTREAM.md)。

## 功能清单（均已实现；后端接口有 15 项自动化测试覆盖，前端拖拽、到期高亮、确认框等界面交互靠页面验证）

- **登录**：单用户登录，登录令牌 24 小时有效；默认账号 `admin` / `admin123`，首次登录会提示修改密码，可在页面右上角改密。
- **看板**：可建多个看板（顶部标签页切换），支持新建、改名、删除；新建看板自带「待办 / 进行中 / 已完成」三列。
- **列**：每个看板可增删列、列改名、列左右调换顺序；删列时列内卡片一并删除（会先弹窗确认）。
- **卡片**：标题、描述、一个彩色标签（8 种颜色）、截止日期（到期高亮、逾期红色警告）；支持新建、编辑、删除。
- **卡片移动**：鼠标拖拽卡片到目标列的任意位置放下；拖不动时也可以用卡片上的 ◀ ▶ 按钮跨列移动、↑ ↓ 按钮在列内排序，后端移动接口统一维护顺序。
- **归档**：做完的卡片可归档进「归档箱」，归档箱里能看到它原来在哪一列，可一键恢复回原列末尾，也可彻底删除。

## 安装与启动

需要 Python 3.10 以上。

Linux / macOS：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows PowerShell：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

启动后浏览器打开 http://127.0.0.1:8000 ，用默认账号 `admin` / `admin123` 登录（首次登录请按提示改密码）。

## 环境变量（都有默认值，可不设）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `TASKBOARD_DB_PATH` | `data/taskboard.db`（相对 app.py 所在目录） | 数据库文件位置 |
| `TB_INITIAL_USERNAME` | `admin` | 首次启动时创建的管理员用户名（库里已有用户后改此变量无效） |
| `TB_INITIAL_PASSWORD` | `admin123` | 首次启动时创建的管理员密码 |
| `TASKBOARD_HOST` | `127.0.0.1` | 监听地址：默认只允许本机访问；设为 `0.0.0.0` 后局域网内其他设备可访问 |
| `PORT` | `8000` | 服务端口 |

## 测试

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q        # 15 项自动化测试（后端接口）
python tests/live_selftest.py     # 真服务自测：起真服务走一遍主流程（建看板→建卡→移动→归档→恢复），16 个检查点
```

Windows PowerShell 把 `python` 换成 `.venv\Scripts\python` 即可，其余相同。

## 后续可扩展（当前版本没有）

- 多用户与看板成员权限
- 卡片评论、子任务、附件
- 泳道、卡片搜索与跨看板汇总
- 数据导入导出

## 许可证

MIT，见 [LICENSE](LICENSE)。
