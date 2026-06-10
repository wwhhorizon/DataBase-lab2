from __future__ import annotations

import os

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QGridLayout,
    QLabel,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

from app.models.entities import LoginUser
from app.services.system_service import SystemService
from app.ui.dialogs import FormDialog


COLUMN_WIDTHS = {
    "id": 70,
    "student_no": 150,
    "student_name": 130,
    "name": 130,
    "gender": 90,
    "phone": 170,
    "email": 260,
    "enrollment_year": 140,
    "status": 110,
    "major_name": 220,
    "class_name": 150,
    "course_code": 150,
    "course_name": 220,
    "credit": 90,
    "hours": 90,
    "semester": 160,
    "selection_date": 160,
    "usual_score": 120,
    "final_score": 120,
    "total_score": 110,
    "grade_level": 110,
    "record_type": 120,
    "title": 200,
    "description": 320,
    "record_date": 160,
    "change_type": 150,
    "old_value": 130,
    "new_value": 130,
    "change_reason": 320,
    "change_date": 160,
    "file_name": 260,
    "file_type": 110,
    "file_path": 360,
    "uploaded_at": 210,
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


class AdminWindow(QMainWindow):
    def __init__(self, user: LoginUser, service: SystemService, logout_callback=None):
        super().__init__()
        self.user = user
        self.service = service
        self.logout_callback = logout_callback
        self.student_rows = []
        self.course_rows = []
        self.selection_rows = []
        self.reward_rows = []
        self.change_rows = []
        self.attachment_rows = []

        self.setWindowTitle(f"学籍管理系统 - 管理员端（{user.display_name}）")
        self.resize(1640, 1040)
        self.setMinimumSize(1280, 800)

        toolbar = QToolBar()
        self.addToolBar(toolbar)
        refresh_btn = self._button("刷新全部", self.refresh_all)
        toolbar.addWidget(refresh_btn)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        logout_btn = self._button("退出登录", self.logout, "secondary")
        toolbar.addWidget(logout_btn)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        self.stat_labels = {}
        dashboard = QWidget()
        dashboard_layout = QVBoxLayout(dashboard)
        dashboard_layout.setContentsMargins(40, 40, 40, 40)
        dashboard_layout.setSpacing(28)
        title = QLabel("系统概览")
        title.setObjectName("PageTitle")
        dashboard_layout.addWidget(title)
        dashboard_grid = QGridLayout()
        dashboard_grid.setSpacing(28)
        for index, (key, label) in enumerate(
            [
                ("student_count", "学生总数"),
                ("course_count", "课程总数"),
                ("selection_count", "选课记录"),
                ("attachment_count", "附件总数"),
            ]
        ):
            card, value_label = self._stat_card(label)
            self.stat_labels[key] = value_label
            dashboard_grid.addWidget(card, index // 2, index % 2)
        dashboard_layout.addLayout(dashboard_grid)
        dashboard_layout.addStretch(1)
        tabs.addTab(dashboard, "概览")

        tabs.addTab(self._build_student_tab(), "学生管理")
        tabs.addTab(self._build_course_tab(), "课程管理")
        tabs.addTab(self._build_selection_tab(), "选课与成绩")
        tabs.addTab(self._build_reward_tab(), "奖惩管理")
        tabs.addTab(self._build_change_tab(), "学籍异动")
        tabs.addTab(self._build_attachment_tab(), "附件管理")

        self.refresh_all()

    def _button(self, text: str, handler=None, variant: str | None = None) -> QPushButton:
        button = QPushButton(text)
        if variant:
            button.setProperty("variant", variant)
        if handler:
            button.clicked.connect(handler)
        return button

    def _stat_card(self, label: str):
        card = QFrame()
        card.setObjectName("StatCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(36, 30, 36, 30)
        value = QLabel("0")
        value.setObjectName("StatValue")
        caption = QLabel(label)
        caption.setObjectName("StatLabel")
        layout.addWidget(value)
        layout.addWidget(caption)
        return card, value

    def logout(self):
        self.close()
        if self.logout_callback:
            self.logout_callback()

    def _build_student_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        top = QHBoxLayout()
        self.student_search = QLineEdit()
        self.student_search.setPlaceholderText("按学号或姓名搜索")
        top.addWidget(self.student_search)
        btn_search = self._button("查询", self.refresh_students, "secondary")
        top.addWidget(btn_search)
        btn_add = self._button("新增", self.add_student)
        top.addWidget(btn_add)
        btn_edit = self._button("编辑", self.edit_student, "secondary")
        top.addWidget(btn_edit)
        btn_delete = self._button("删除", self.delete_student, "danger")
        top.addWidget(btn_delete)
        layout.addLayout(top)
        self.student_table = QTableWidget()
        layout.addWidget(self.student_table)
        return page

    def _build_course_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        top = QHBoxLayout()
        for text, handler, variant in [("新增", self.add_course, None), ("编辑", self.edit_course, "secondary"), ("删除", self.delete_course, "danger")]:
            btn = self._button(text, handler, variant)
            top.addWidget(btn)
        layout.addLayout(top)
        self.course_table = QTableWidget()
        layout.addWidget(self.course_table)
        return page

    def _build_selection_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        top = QHBoxLayout()
        btn_add = self._button("新增选课", self.add_selection)
        top.addWidget(btn_add)
        btn_score = self._button("录入/修改成绩", self.save_score, "secondary")
        top.addWidget(btn_score)
        layout.addLayout(top)
        self.selection_table = QTableWidget()
        layout.addWidget(self.selection_table)
        return page

    def _build_reward_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        top = QHBoxLayout()
        btn_add = self._button("新增奖惩", self.add_reward)
        top.addWidget(btn_add)
        btn_delete = self._button("删除奖惩", self.delete_reward, "danger")
        top.addWidget(btn_delete)
        layout.addLayout(top)
        self.reward_table = QTableWidget()
        layout.addWidget(self.reward_table)
        return page

    def _build_change_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        btn_add = self._button("登记学籍异动", self.add_status_change)
        layout.addWidget(btn_add)
        self.change_table = QTableWidget()
        layout.addWidget(self.change_table)
        return page

    def _build_attachment_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        top = QHBoxLayout()
        btn_add = self._button("上传附件", self.add_attachment)
        top.addWidget(btn_add)
        btn_open = self._button("打开附件", self.open_attachment, "secondary")
        top.addWidget(btn_open)
        btn_delete = self._button("删除附件", self.delete_attachment, "danger")
        top.addWidget(btn_delete)
        layout.addLayout(top)
        self.attachment_table = QTableWidget()
        layout.addWidget(self.attachment_table)
        return page

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_students()
        self.refresh_courses()
        self.refresh_selections()
        self.refresh_rewards()
        self.refresh_changes()
        self.refresh_attachments()

    def refresh_dashboard(self):
        stats = self.service.get_dashboard_stats()
        for key, label in self.stat_labels.items():
            label.setText(str(stats[key]))

    def refresh_students(self):
        self.student_rows = self.service.list_students(self.student_search.text().strip())
        fill_table(
            self.student_table,
            self.student_rows,
            [
                ("id", "ID"),
                ("student_no", "学号"),
                ("name", "姓名"),
                ("gender", "性别"),
                ("phone", "电话"),
                ("email", "邮箱"),
                ("enrollment_year", "入学年份"),
                ("status", "状态"),
                ("major_name", "专业"),
                ("class_name", "班级"),
            ],
        )

    def refresh_courses(self):
        self.course_rows = self.service.list_courses()
        fill_table(
            self.course_table,
            self.course_rows,
            [("id", "ID"), ("course_code", "课程号"), ("name", "课程名"), ("credit", "学分"), ("hours", "学时"), ("semester", "学期")],
        )

    def refresh_selections(self):
        self.selection_rows = self.service.list_course_selections()
        fill_table(
            self.selection_table,
            self.selection_rows,
            [
                ("id", "ID"),
                ("student_no", "学号"),
                ("student_name", "姓名"),
                ("course_code", "课程号"),
                ("course_name", "课程名"),
                ("selection_date", "选课日期"),
                ("usual_score", "平时分"),
                ("final_score", "期末分"),
                ("total_score", "总评"),
                ("grade_level", "等级"),
            ],
        )

    def refresh_rewards(self):
        self.reward_rows = self.service.list_rewards()
        fill_table(
            self.reward_table,
            self.reward_rows,
            [
                ("id", "ID"),
                ("student_no", "学号"),
                ("student_name", "姓名"),
                ("record_type", "类型"),
                ("title", "标题"),
                ("description", "说明"),
                ("record_date", "日期"),
            ],
        )

    def refresh_changes(self):
        self.change_rows = self.service.list_status_changes()
        fill_table(
            self.change_table,
            self.change_rows,
            [
                ("id", "ID"),
                ("student_no", "学号"),
                ("student_name", "姓名"),
                ("change_type", "异动类型"),
                ("old_value", "原值"),
                ("new_value", "新值"),
                ("change_reason", "原因"),
                ("change_date", "日期"),
            ],
        )

    def refresh_attachments(self):
        self.attachment_rows = self.service.list_attachments()
        fill_table(
            self.attachment_table,
            self.attachment_rows,
            [
                ("id", "ID"),
                ("student_no", "学号"),
                ("student_name", "姓名"),
                ("file_name", "文件名"),
                ("file_type", "类型"),
                ("file_path", "路径"),
                ("description", "说明"),
                ("uploaded_at", "上传时间"),
            ],
        )

    def _current_row(self, table, rows):
        index = table.currentRow()
        if index < 0 or index >= len(rows):
            raise ValueError("请先选择一条记录。")
        return rows[index]

    def _student_fields(self):
        major_options = [(row["name"], row["id"]) for row in self.service.list_majors()]
        class_options = [(row["name"], row["id"]) for row in self.service.list_classes()]
        return [
            {"name": "student_no", "label": "学号"},
            {"name": "password", "label": "登录密码", "echo_mode": "password"},
            {"name": "name", "label": "姓名"},
            {"name": "gender", "label": "性别", "type": "combo", "options": [("男", "男"), ("女", "女")]},
            {"name": "phone", "label": "电话"},
            {"name": "email", "label": "邮箱"},
            {"name": "enrollment_year", "label": "入学年份", "type": "int", "min": 2010, "max": 2100, "default": 2023},
            {"name": "status", "label": "状态", "type": "combo", "options": [("在读", "在读"), ("休学", "休学"), ("毕业", "毕业")]},
            {"name": "major_id", "label": "专业", "type": "combo", "options": major_options},
            {"name": "class_id", "label": "班级", "type": "combo", "options": class_options},
        ]

    def add_student(self):
        dialog = FormDialog("新增学生", self._student_fields(), parent=self)
        if dialog.exec_():
            values = dialog.values()
            if not values["password"]:
                QMessageBox.warning(self, "提示", "新增学生必须设置密码。")
                return
            self.service.create_student(values)
            self.refresh_students()

    def edit_student(self):
        try:
            row = self._current_row(self.student_table, self.student_rows)
        except Exception as exc:
            QMessageBox.warning(self, "提示", str(exc))
            return
        dialog = FormDialog("编辑学生", self._student_fields(), row, self)
        if dialog.exec_():
            values = dialog.values()
            values["student_no"] = row["student_no"]
            self.service.update_student(row["id"], values)
            self.refresh_students()

    def delete_student(self):
        try:
            row = self._current_row(self.student_table, self.student_rows)
            self.service.delete_student(row["id"])
            self.refresh_students()
        except Exception as exc:
            QMessageBox.warning(self, "删除失败", str(exc))

    def add_course(self):
        fields = [
            {"name": "course_code", "label": "课程号"},
            {"name": "name", "label": "课程名"},
            {"name": "credit", "label": "学分", "type": "float", "min": 0, "max": 10, "default": 3},
            {"name": "hours", "label": "学时", "type": "int", "min": 0, "max": 200, "default": 48},
            {"name": "semester", "label": "学期"},
        ]
        dialog = FormDialog("新增课程", fields, parent=self)
        if dialog.exec_():
            self.service.create_course(dialog.values())
            self.refresh_courses()

    def edit_course(self):
        try:
            row = self._current_row(self.course_table, self.course_rows)
        except Exception as exc:
            QMessageBox.warning(self, "提示", str(exc))
            return
        fields = [
            {"name": "course_code", "label": "课程号"},
            {"name": "name", "label": "课程名"},
            {"name": "credit", "label": "学分", "type": "float", "min": 0, "max": 10},
            {"name": "hours", "label": "学时", "type": "int", "min": 0, "max": 200},
            {"name": "semester", "label": "学期"},
        ]
        dialog = FormDialog("编辑课程", fields, row, self)
        if dialog.exec_():
            self.service.update_course(row["id"], dialog.values())
            self.refresh_courses()

    def delete_course(self):
        try:
            row = self._current_row(self.course_table, self.course_rows)
            self.service.delete_course(row["id"])
            self.refresh_courses()
        except Exception as exc:
            QMessageBox.warning(self, "删除失败", str(exc))

    def add_selection(self):
        student_options = [(f"{row['student_no']} - {row['name']}", row["id"]) for row in self.service.list_students()]
        course_options = [(f"{row['course_code']} - {row['name']}", row["id"]) for row in self.service.list_courses()]
        fields = [
            {"name": "student_id", "label": "学生", "type": "combo", "options": student_options},
            {"name": "course_id", "label": "课程", "type": "combo", "options": course_options},
        ]
        dialog = FormDialog("新增选课", fields, parent=self)
        if dialog.exec_():
            values = dialog.values()
            try:
                self.service.create_selection(values["student_id"], values["course_id"])
                self.refresh_selections()
            except Exception as exc:
                QMessageBox.warning(self, "新增失败", str(exc))

    def save_score(self):
        try:
            row = self._current_row(self.selection_table, self.selection_rows)
        except Exception as exc:
            QMessageBox.warning(self, "提示", str(exc))
            return
        fields = [
            {"name": "usual_score", "label": "平时分", "type": "float", "min": 0, "max": 100, "default": row.get("usual_score") or 0},
            {"name": "final_score", "label": "期末分", "type": "float", "min": 0, "max": 100, "default": row.get("final_score") or 0},
        ]
        dialog = FormDialog("成绩录入", fields, parent=self)
        if dialog.exec_():
            values = dialog.values()
            self.service.save_score(row["id"], values["usual_score"], values["final_score"])
            self.refresh_selections()

    def add_reward(self):
        student_options = [(f"{row['student_no']} - {row['name']}", row["id"]) for row in self.service.list_students()]
        fields = [
            {"name": "student_id", "label": "学生", "type": "combo", "options": student_options},
            {"name": "record_type", "label": "类型", "type": "combo", "options": [("奖励", "奖励"), ("惩罚", "惩罚")]},
            {"name": "title", "label": "标题"},
            {"name": "description", "label": "说明", "type": "multiline"},
            {"name": "record_date", "label": "日期", "type": "date"},
        ]
        dialog = FormDialog("新增奖惩", fields, parent=self)
        if dialog.exec_():
            self.service.create_reward(dialog.values())
            self.refresh_rewards()

    def delete_reward(self):
        try:
            row = self._current_row(self.reward_table, self.reward_rows)
            self.service.delete_reward(row["id"])
            self.refresh_rewards()
        except Exception as exc:
            QMessageBox.warning(self, "删除失败", str(exc))

    def add_status_change(self):
        student_rows = self.service.list_students()
        student_options = [(f"{row['student_no']} - {row['name']}", row["id"]) for row in student_rows]
        major_options = [(row["name"], row["id"]) for row in self.service.list_majors()]
        class_options = [(row["name"], row["id"]) for row in self.service.list_classes()]
        fields = [
            {"name": "student_id", "label": "学生", "type": "combo", "options": student_options},
            {"name": "change_type", "label": "异动类型", "type": "combo", "options": [("专业变更", "专业变更"), ("班级变更", "班级变更"), ("状态变更", "状态变更")]},
            {"name": "old_value", "label": "原值"},
            {"name": "new_value", "label": "新值"},
            {"name": "change_reason", "label": "原因", "type": "multiline"},
            {"name": "change_date", "label": "日期", "type": "date"},
            {"name": "new_ref_id", "label": "关联新值", "type": "combo", "options": [("无", 0)] + major_options + class_options},
        ]
        dialog = FormDialog("登记学籍异动", fields, parent=self)
        if dialog.exec_():
            self.service.add_status_change(dialog.values())
            self.refresh_changes()
            self.refresh_students()

    def add_attachment(self):
        student_options = [(f"{row['student_no']} - {row['name']}", row["id"]) for row in self.service.list_students()]
        fields = [
            {"name": "student_id", "label": "学生", "type": "combo", "options": student_options},
            {"name": "description", "label": "附件说明"},
        ]
        dialog = FormDialog("上传附件", fields, parent=self)
        if not dialog.exec_():
            return
        file_path, _ = QFileDialog.getOpenFileName(self, "选择附件")
        if not file_path:
            return
        values = dialog.values()
        self.service.add_attachment(values["student_id"], file_path, values["description"])
        self.refresh_attachments()

    def open_attachment(self):
        try:
            row = self._current_row(self.attachment_table, self.attachment_rows)
            path = row["file_path"]
            if not os.path.exists(path):
                raise FileNotFoundError("附件文件不存在。")
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as exc:
            QMessageBox.warning(self, "打开失败", str(exc))

    def delete_attachment(self):
        try:
            row = self._current_row(self.attachment_table, self.attachment_rows)
            self.service.delete_attachment(row["id"], row["file_path"])
            self.refresh_attachments()
        except Exception as exc:
            QMessageBox.warning(self, "删除失败", str(exc))
