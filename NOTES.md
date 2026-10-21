# 开工记录（调研与取舍）

## 上游调研（2026-10-21 经 GitHub 接口实查）

- 参考对象：Kanboard（github.com/kanboard/kanboard），PHP 写的看板式项目管理软件，当前处于维护模式，最新版本 1.2.54。
- 默认分支 HEAD：`e4fb64e972b0ae255a92cf4b7b03489846ebbffc`（2026-10-21 的文档提交）。
- 许可证：MIT；LICENSE 署名行原文：`Copyright (c) Frédéric Guillot`（已逐字抄进 UPSTREAM.md）。
- 数据模型（读其 SQLite 建表脚本）：核心是三层——projects（看板）→ columns（列，带 position）→ tasks（卡片，带 column_id 与 position），另有 swimlanes（泳道）、tags + task_has_tags（多标签）、comments、subtasks 等一圈外围表。

## 本项目的取舍

- 只取核心三层：看板 / 列 / 卡片；排序统一用 position 字段、从 0 起连续编号，任何增删移之后都重排，保证不变量。
- 标签简化：一张卡一个彩色标签（文字 + 8 色选一），不做多标签多对多——够日常用，模型更简单。
- 归档语义：卡片用 is_archived 标记下架而不是删除，归档箱保留「原列名」方便恢复回原列。
- 不进本版：泳道、多人协作与权限、评论、子任务、附件、自动规则（这些是上游的大功能面，本版先做能真正做单的最小完整闭环）。
- 卡片移动接口语义：先把卡片从原列摘出，再按 to_index 插入目标列；前端拖拽与按钮移动共用这一条接口，避免两套顺序逻辑。

## 资源核对（动手前查过运行环境）

- 云端环境：2 核 CPU / 内存 7.7G / 无显卡。
- 本项目栈：Python + FastAPI + SQLite + 单个静态页面，无前端构建、无重依赖，运行时内存几十 MB 量级，云端完全带得动；本地 Windows 同样可直接跑。
