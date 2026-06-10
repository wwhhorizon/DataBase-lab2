from __future__ import annotations

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QToolBar,
)
from PyQt5.QtCore import Qt

from app.models.entities import LoginUser
from app.services.system_service import SystemService


COLUMN_WIDTHS = {
    "course_code": 150,
    "course_name": 240,
    "credit": 90,
    "hours": 90,
    "semester": 160,
    "usual_score": 120,
    "final_score": 120,
    "total_score": 110,
    "grade_level": 110,
    "record_type": 120,
    "title": 220,
    "description": 360,
    "record_date": 160,
    "change_type": 150,
    "old_value": 130,
    "new_value": 130,
    "change_reason": 360,
    "change_date": 160,
    "file_name": 260,
    "file_type": 110,
    "file_path": 420,
    "uploaded_at": 210,
}


def build_readonly_table(rows, columns):
    table = QTableWidget()
    table.setRowCount(len(rows))
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels([col[1] for col in columns])
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(44)
    table.horizontalHeader().setStretchLastSection(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    for row_idx, row in enumerate(rows):
        for col_idx, (key, _) in enumerate(columns):
            item = QTableWidgetItem(str(row.get(key, "")))
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            table.setItem(row_idx, col_idx, item)
    table.resizeColumnsToContents()
    for col_idx, (key, _) in enumerate(columns):
        if key in COLUMN_WIDTHS:
            table.setColumnWidth(col_idx, COLUMN_WIDTHS[key])
    return table


class StudentWindow(QMainWindow):
    def __init__(self, user: LoginUser, service: SystemService, logout_callback=None):
        super().__init__()
        self.user = user
        self.service = service
        self.logout_callback = logout_callback
        self.setWindowTitle(f"学籍管理系统 - 学生端（{user.display_name}）")
        self.resize(1640, 1040)
        self.setMinimumSize(1280, 800)

        profile = self.service.get_student_profile(user.username)

        toolbar = QToolBar()
        self.addToolBar(toolbar)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        logout_btn = QPushButton("退出登录")
        logout_btn.setProperty("variant", "secondary")
        logout_btn.clicked.connect(self.logout)
        toolbar.addWidget(logout_btn)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        profile_page = QWidget()
        profile_layout = QVBoxLayout(profile_page)
        profile_layout.setContentsMargins(40, 40, 40, 40)
        profile_layout.setSpacing(28)
        title = QLabel("个人学籍档案")
        title.setObjectName("PageTitle")
        profile_layout.addWidget(title)
        card = QFrame()
        card.setObjectName("ProfileCard")
        grid = QGridLayout(card)
        grid.setContentsMargins(42, 38, 42, 38)
        grid.setHorizontalSpacing(64)
        grid.setVerticalSpacing(28)
        for index, (label, value) in enumerate(
            [
                ("学号", profile["student_no"]),
                ("姓名", profile["name"]),
                ("性别", profile["gender"]),
                ("电话", profile["phone"]),
                ("邮箱", profile["email"]),
                ("专业", profile["major_name"]),
                ("班级", profile["class_name"]),
                ("状态", profile["status"]),
            ]
        ):
            caption = QLabel(label)
            caption.setObjectName("StatLabel")
            content = QLabel(str(value))
            content.setObjectName("PageTitle")
            row = index // 2
            col = (index % 2) * 2
            grid.addWidget(caption, row, col)
            grid.addWidget(content, row, col + 1)
        profile_layout.addWidget(card)
        profile_layout.addStretch(1)
        tabs.addTab(profile_page, "个人信息")

        tabs.addTab(
            build_readonly_table(
                self.service.list_student_courses(user.user_id),
                [
                    ("course_code", "课程号"),
                    ("course_name", "课程名"),
                    ("credit", "学分"),
                    ("hours", "学时"),
                    ("semester", "学期"),
                    ("usual_score", "平时分"),
                    ("final_score", "期末分"),
                    ("total_score", "总评"),
                    ("grade_level", "等级"),
                ],
            ),
            "课程与成绩",
        )
        tabs.addTab(
            build_readonly_table(
                self.service.list_student_rewards(user.user_id),
                [("record_type", "类型"), ("title", "标题"), ("description", "说明"), ("record_date", "日期")],
            ),
            "奖惩记录",
        )
        tabs.addTab(
            build_readonly_table(
                self.service.list_student_status_changes(user.user_id),
                [("change_type", "异动类型"), ("old_value", "原值"), ("new_value", "新值"), ("change_reason", "原因"), ("change_date", "日期")],
            ),
            "学籍异动",
        )
        tabs.addTab(
            build_readonly_table(
                self.service.list_student_attachments(user.user_id),
                [("file_name", "文件名"), ("file_type", "类型"), ("file_path", "路径"), ("description", "说明"), ("uploaded_at", "上传时间")],
            ),
            "个人附件",
        )

    def logout(self):
        self.close()
        if self.logout_callback:
            self.logout_callback()
