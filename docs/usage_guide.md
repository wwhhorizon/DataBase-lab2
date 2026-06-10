# 学籍管理系统使用说明

## 1. 文档目的

本说明用于指导教师、助教或使用者在本地 Windows 环境中完成学籍管理系统的安装、初始化、启动和演示操作。

## 2. 运行环境

- 操作系统：Windows 10 或 Windows 11
- Python：3.10 及以上
- MySQL：8.0 及以上
- 必要 Python 依赖：
  - `PyQt5`
  - `PyMySQL`

## 3. 项目路径

项目根目录：

`E:\database\student_management_system`

关键文件：

- 启动入口：[main.py](E:\database\student_management_system\main.py)
- 数据库脚本：[schema.sql](E:\database\student_management_system\sql\schema.sql)
- 配置文件：[config.ini](E:\database\student_management_system\app\config\config.ini)
- 课程报告：[report.md](E:\database\student_management_system\docs\report.md)

## 4. 首次部署步骤

### 4.1 安装 Python 依赖

在项目根目录打开 PowerShell，执行：

```powershell
python -m pip install -r requirements.txt
```

### 4.2 启动 MySQL 服务

确保本机 MySQL 已正常安装并启动，能够通过命令行或 MySQL Workbench 连接。

### 4.3 登录 MySQL

本项目默认使用本机 MySQL 的 `root` 用户连接数据库，你的本地数据库密码为 `123456`。

在 PowerShell 或命令提示符中执行：

```powershell
mysql -u root -p
```

系统提示输入密码时，输入：

```text
123456
```

注意：输入密码时命令行通常不会显示任何字符，这是正常现象。输入完成后按回车即可登录。

登录成功后会进入 MySQL 命令行，通常可以看到类似下面的提示符：

```text
mysql>
```

如果提示 `mysql` 不是内部或外部命令，说明 MySQL 的 `bin` 目录没有加入系统环境变量。可以改用 MySQL Workbench 执行脚本，或使用 MySQL 安装目录下的完整路径执行 `mysql.exe`。

### 4.4 初始化数据库

执行以下两种方式之一：

方式一：在 MySQL 命令行执行

```sql
SOURCE E:/database/student_management_system/sql/schema.sql;
```

方式二：在 MySQL Workbench 中打开并运行 [schema.sql](E:\database\student_management_system\sql\schema.sql)。

执行完成后将自动生成：

- 数据库 `student_management`
- 业务表、约束和索引
- 函数
- 存储过程
- 触发器
- 示例数据

### 4.5 修改数据库连接配置

打开 [config.ini](E:\database\student_management_system\app\config\config.ini)，按本机实际情况修改：

```ini
[database]
host = 127.0.0.1
port = 3306
user = root
password = 123456
database = student_management
charset = utf8mb4

[storage]
attachment_root = attachments
```

若本地数据库密码不同，必须先修改再运行程序。

## 5. 启动方法

在项目根目录执行：

```powershell
python main.py
```

启动成功后会出现“学籍管理系统 - 登录”窗口。

## 6. 默认测试账号

- 管理员：`admin / Admin@123`
- 学生：`PB23111001 / Stu@123`

## 7. 功能使用说明

### 7.1 登录

1. 打开程序；
2. 在角色下拉框中选择“管理员”或“学生”；
3. 输入账号与密码；
4. 点击“登录”。

### 7.2 管理员端功能说明

#### 7.2.1 概览

登录后默认可查看系统统计信息，包括：

- 学生总数
- 课程总数
- 选课记录数
- 附件总数

#### 7.2.2 学生管理

支持：

- 按学号或姓名查询学生；
- 新增学生；
- 编辑学生信息；
- 删除学生。

新增或编辑时可维护字段：

- 学号
- 登录密码
- 姓名
- 性别
- 电话
- 邮箱
- 入学年份
- 学籍状态
- 专业
- 班级

#### 7.2.3 课程管理

支持：

- 新增课程；
- 编辑课程；
- 删除课程。

课程字段包括：

- 课程号
- 课程名
- 学分
- 学时
- 开课学期

#### 7.2.4 选课与成绩

支持：

- 为指定学生新增选课记录；
- 为已有选课记录录入成绩；
- 修改成绩。

成绩录入时系统会自动完成：

- 总评计算
- 等级映射
- 成绩修改时间更新
- 成绩变更审计日志写入

#### 7.2.5 奖惩管理

支持：

- 新增奖励记录；
- 新增惩罚记录；
- 删除已有奖惩记录。

#### 7.2.6 学籍异动

支持：

- 专业变更
- 班级变更
- 学籍状态变更

系统会在一次事务中同时完成异动记录写入和学生主档更新。

#### 7.2.7 附件管理

支持：

- 上传图片、视频或普通文件；
- 打开附件；
- 删除附件。

附件会被复制到项目目录下的：

`attachments/{student_id}/`

数据库中保存的是附件元数据和路径。

### 7.3 学生端功能说明

学生登录后主要以查询为主，可查看：

- 个人信息
- 课程与成绩
- 奖惩记录
- 学籍异动记录
- 个人附件列表

## 8. 验收演示步骤

建议按以下顺序向老师演示：

1. 打开登录界面；
2. 使用管理员账号登录；
3. 展示概览页；
4. 在学生管理中搜索并编辑一个学生；
5. 在课程管理中查看课程；
6. 在选课与成绩中为某学生录入或修改成绩；
7. 说明数据库函数和触发器的作用；
8. 在学籍异动中登记一次状态变更；
9. 上传一个图片或文件附件；
10. 切换学生账号登录，展示成绩和附件查询功能。

## 9. 数据库高级特性验证方法

### 9.1 验证存储过程

执行学生新增或修改操作后，可在数据库中确认学生记录发生变化。  
相关存储过程为：

`sp_upsert_student_profile`

### 9.2 验证函数

录入成绩后，查看 `score.total_score` 和 `score.grade_level` 字段，可验证：

- `fn_calculate_total_score`
- `fn_score_to_level`

### 9.3 验证事务

执行学籍异动时，系统会在事务中写入 `student_status_change` 并更新 `student` 主档。  
如出现异常，系统会整体回滚。

### 9.4 验证触发器

修改已有成绩后，检查：

- `score.last_updated`
- `score_audit_log`

可以看到触发器自动执行后的结果。

## 10. 常见问题与处理

### 10.1 程序启动时报数据库连接失败

原因：

- MySQL 未启动；
- `config.ini` 中用户名、密码或数据库名错误；
- 本机端口不是 `3306`。

处理方式：

- 检查 MySQL 服务状态；
- 重新核对配置文件；
- 确认数据库脚本已执行。

### 10.2 登录失败

原因：

- 账号或密码输入错误；
- 数据库示例数据未成功导入。

处理方式：

- 检查默认账号；
- 重新执行 [schema.sql](E:\database\student_management_system\sql\schema.sql)。

### 10.3 附件无法打开

原因：

- 原始文件被删除后路径异常；
- 文件路径中存在权限限制；
- 文件未成功复制到附件目录。

处理方式：

- 检查 `attachments/` 目录中是否存在对应文件；
- 重新上传附件。

### 10.4 成绩修改后没有看到触发器效果

原因：

- 修改的是首次插入而不是更新；
- 没有刷新数据库查询结果。

处理方式：

- 对同一条已有成绩再次执行修改；
- 查询 `score_audit_log` 表确认日志是否写入。

## 11. 提交建议

最终提交建议包含以下内容：

- 项目源码目录
- `sql/schema.sql`
- `docs/report.md`
- `docs/diagrams.md`
- `docs/test_cases.md`
- 本说明文档 `docs/usage_guide.md`
- 本地运行截图

## 12. 结语

通过本说明文档，使用者可以从零开始完成学籍管理系统的部署、运行和演示。该系统已经具备课程设计提交所需的主要要素，适合作为数据库课程设计成果进行验收展示。
