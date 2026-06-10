# 学籍管理系统（C/S 架构）

本项目是一个基于 `Python + PyQt5 + MySQL` 的桌面端学籍管理系统，符合数据库课程设计对 `C/S` 架构、`MySQL`、媒体附件管理、存储过程、函数、事务、触发器等要求。

## 功能概览

- 双角色登录：管理员、学生
- 学生档案管理：基本信息、专业、班级、状态
- 课程管理：课程信息维护
- 选课管理：学生选课、重复选课拦截
- 成绩管理：录入、修改、查询、等级展示
- 奖惩管理：奖惩信息维护
- 学籍异动管理：专业变更、班级变更、状态变更
- 附件管理：图片、视频、文件上传与下载
- 统计概览：学生数、课程数、选课数、附件数

## 目录结构

```text
student_management_system/
├─ app/
│  ├─ config/
│  ├─ dao/
│  ├─ db/
│  ├─ models/
│  ├─ services/
│  ├─ ui/
│  └─ utils/
├─ attachments/
├─ docs/
├─ sql/
├─ tests/
├─ main.py
└─ requirements.txt
```

## 运行环境

- Windows
- Python 3.10+
- MySQL 8.0+

## 快速开始

1. 安装依赖：

```powershell
python -m pip install -r requirements.txt
```

2. 执行数据库脚本：

```powershell
mysql -u root -p
```

密码输入：

```text
123456
```

进入 `mysql>` 后执行：

```sql
SOURCE E:/database/student_management_system/sql/schema.sql;
```

3. 复制配置模板并修改数据库连接：

```powershell
Copy-Item app\config\config.ini.example app\config\config.ini
```

4. 启动系统：

```powershell
python main.py
```

## 默认账号

- 管理员：`admin / Admin@123`
- 学生：`PB23111001 / Stu@123`

## 课程设计配套文档

- 报告：[docs/report.md](E:\database\student_management_system\docs\report.md)
- 需求分析与 ER 图：[docs/需求分析说明与概要设计ER图.md](E:\database\student_management_system\docs\需求分析说明与概要设计ER图.md)
- ER 图与架构图：[docs/diagrams.md](E:\database\student_management_system\docs\diagrams.md)
- 测试用例：[docs/test_cases.md](E:\database\student_management_system\docs\test_cases.md)
- 使用说明：[docs/usage_guide.md](E:\database\student_management_system\docs\usage_guide.md)
