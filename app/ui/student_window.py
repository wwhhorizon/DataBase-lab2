from __future__ import annotations

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
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
from app.ui.dialogs import FormDialog


COLUMN_WIDTHS = {
    "id": 70,
    "selection_id": 90,
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
    "target_major_name": 220,
    "reason": 420,
    "status": 120,
    "apply_date": 160,
    "review_comment": 360,
    "reviewed_at": 210,
}


def fill_table(table: QTableWidget, rows, columns):
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


def build_readonly_table(rows, columns):
    table = QTableWidget()
    fill_table(table, rows, columns)
    return table


class StudentWindow(QMainWindow):
    def __init__(self, user: LoginUser, service: SystemService, logout_callback=None):
        super().__init__()
        self.user = user
        self.service = service
        self.logout_callback = logout_callback
        self.student_course_rows = []
        self.available_course_rows = []
        self.transfer_application_rows = []
        self.reward_rows = []
        self.status_change_rows = []
        self.attachment_rows = []
        self.profile_value_labels = {}
        self.setWindowTitle(f"学籍管理系统 - 学生端（{user.display_name}）")
        self.resize(1640, 1040)
        self.setMinimumSize(1280, 800)

        profile = self.service.get_student_profile(user.username)

        toolbar = QToolBar()
        self.addToolBar(toolbar)
        refresh_btn = QPushButton("刷新全部")
        refresh_btn.setProperty("variant", "secondary")
        refresh_btn.clicked.connect(self.refresh_all)
        toolbar.addWidget(refresh_btn)
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
        for index, (key, label, value) in enumerate(
            [
                ("student_no", "学号", profile["student_no"]),
                ("name", "姓名", profile["name"]),
                ("gender", "性别", profile["gender"]),
                ("phone", "电话", profile["phone"]),
                ("email", "邮箱", profile["email"]),
                ("major_name", "专业", profile["major_name"]),
                ("class_name", "班级", profile["class_name"]),
                ("status", "状态", profile["status"]),
            ]
        ):
            caption = QLabel(label)
            caption.setObjectName("StatLabel")
            content = QLabel(str(value))
            content.setObjectName("PageTitle")
            self.profile_value_labels[key] = content
            row = index // 2
            col = (index % 2) * 2
            grid.addWidget(caption, row, col)
            grid.addWidget(content, row, col + 1)
        profile_layout.addWidget(card)
        profile_layout.addStretch(1)
        tabs.addTab(profile_page, "个人信息")

        tabs.addTab(self._build_current_courses_tab(), "课程与成绩")
        tabs.addTab(self._build_course_selection_tab(), "自主选课")
        tabs.addTab(self._build_major_transfer_tab(), "转专业申请")
        tabs.addTab(self._build_reward_tab(), "奖惩记录")
        tabs.addTab(self._build_status_change_tab(), "学籍异动")
        tabs.addTab(self._build_attachment_tab(), "个人附件")
        self.refresh_all()

    def _button(self, text: str, handler=None, variant: str | None = None) -> QPushButton:
        button = QPushButton(text)
        if variant:
            button.setProperty("variant", variant)
        if handler:
            button.clicked.connect(handler)
        return button

    def _current_row(self, table, rows):
        index = table.currentRow()
        if index < 0 or index >= len(rows):
            raise ValueError("请先选择一条记录。")
        return rows[index]

    def _build_current_courses_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.student_course_table = QTableWidget()
        layout.addWidget(self.student_course_table)
        return page

    def _build_course_selection_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        top = QHBoxLayout()
        top.addWidget(self._button("选择课程", self.select_course))
        layout.addLayout(top)
        self.available_course_table = QTableWidget()
        layout.addWidget(self.available_course_table)
        return page

    def _build_major_transfer_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        top = QHBoxLayout()
        top.addWidget(self._button("提交申请", self.submit_major_transfer_application))
        layout.addLayout(top)
        self.transfer_application_table = QTableWidget()
        layout.addWidget(self.transfer_application_table)
        return page

    def _build_reward_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.reward_table = QTableWidget()
        layout.addWidget(self.reward_table)
        return page

    def _build_status_change_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.status_change_table = QTableWidget()
        layout.addWidget(self.status_change_table)
        return page

    def _build_attachment_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.attachment_table = QTableWidget()
        layout.addWidget(self.attachment_table)
        return page

    def refresh_all(self):
        self.refresh_profile()
        self.refresh_student_courses()
        self.refresh_available_courses()
        self.refresh_transfer_applications()
        self.refresh_rewards()
        self.refresh_status_changes()
        self.refresh_attachments()

    def refresh_profile(self):
        profile = self.service.get_student_profile(self.user.username)
        for key, label in self.profile_value_labels.items():
            label.setText(str(profile.get(key, "")))

    def refresh_student_courses(self):
        self.student_course_rows = self.service.list_student_courses(self.user.user_id)
        fill_table(
            self.student_course_table,
            self.student_course_rows,
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
        )

    def refresh_available_courses(self):
        self.available_course_rows = self.service.list_available_courses_for_student(self.user.user_id)
        fill_table(
            self.available_course_table,
            self.available_course_rows,
            [
                ("id", "ID"),
                ("course_code", "课程号"),
                ("course_name", "课程名"),
                ("credit", "学分"),
                ("hours", "学时"),
                ("semester", "学期"),
            ],
        )

    def select_course(self):
        try:
            row = self._current_row(self.available_course_table, self.available_course_rows)
            self.service.create_selection(self.user.user_id, row["id"])
            self.refresh_student_courses()
            self.refresh_available_courses()
            QMessageBox.information(self, "选课成功", "课程已加入你的课表。")
        except Exception as exc:
            QMessageBox.warning(self, "选课失败", str(exc))

    def refresh_transfer_applications(self):
        self.transfer_application_rows = self.service.list_student_major_transfer_applications(self.user.user_id)
        fill_table(
            self.transfer_application_table,
            self.transfer_application_rows,
            [
                ("target_major_name", "目标专业"),
                ("reason", "申请原因"),
                ("status", "状态"),
                ("apply_date", "申请日期"),
                ("review_comment", "审核意见"),
                ("reviewed_at", "审核时间"),
            ],
        )

    def refresh_rewards(self):
        self.reward_rows = self.service.list_student_rewards(self.user.user_id)
        fill_table(
            self.reward_table,
            self.reward_rows,
            [("record_type", "类型"), ("title", "标题"), ("description", "说明"), ("record_date", "日期")],
        )

    def refresh_status_changes(self):
        self.status_change_rows = self.service.list_student_status_changes(self.user.user_id)
        fill_table(
            self.status_change_table,
            self.status_change_rows,
            [("change_type", "异动类型"), ("old_value", "原值"), ("new_value", "新值"), ("change_reason", "原因"), ("change_date", "日期")],
        )

    def refresh_attachments(self):
        self.attachment_rows = self.service.list_student_attachments(self.user.user_id)
        fill_table(
            self.attachment_table,
            self.attachment_rows,
            [("file_name", "文件名"), ("file_type", "类型"), ("file_path", "路径"), ("description", "说明"), ("uploaded_at", "上传时间")],
        )

    def submit_major_transfer_application(self):
        major_options = [(row["name"], row["id"]) for row in self.service.list_majors()]
        dialog = FormDialog(
            "提交转专业申请",
            [
                {"name": "target_major_id", "label": "目标专业", "type": "combo", "options": major_options},
                {"name": "reason", "label": "申请原因", "type": "multiline"},
            ],
            parent=self,
        )
        if dialog.exec_():
            values = dialog.values()
            if not values["reason"]:
                QMessageBox.warning(self, "提交失败", "请填写申请原因。")
                return
            try:
                self.service.submit_major_transfer_application(
                    self.user.user_id,
                    values["target_major_id"],
                    values["reason"],
                )
                self.refresh_transfer_applications()
                QMessageBox.information(self, "提交成功", "转专业申请已提交，请等待审核。")
            except Exception as exc:
                QMessageBox.warning(self, "提交失败", str(exc))

    def logout(self):
        self.close()
        if self.logout_callback:
            self.logout_callback()
