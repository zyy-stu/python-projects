# 数据库设计

tasks 的 id 为 INTEGER 自增主键，title TEXT 非空且去空白长度 1–200，description TEXT 默认空且上限 10000。priority 限定 low/normal/high，status 限定 pending/completed。due_date 为可空 ISO 日期文本。created_at、updated_at 为非空 UTC ISO 文本。应用验证日期和时区，SQLite CHECK 验证标题、描述、枚举。按 status/priority 组合及 due_date 建索引，无外键。事务成功提交、异常回滚，每次操作关闭连接。

[项目首页](../README.md)
