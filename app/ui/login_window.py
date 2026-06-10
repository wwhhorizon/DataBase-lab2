from __future__ import annotations

from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtCore import Qt

from app.services.auth_service import AuthService
from app.services.system_service import SystemService
from app.ui.admin_window import AdminWindow
from app.ui.student_window import StudentWindow


class LoginWindow(QMainWindow):
    def __init__(self, auth_service: AuthService, system_service: SystemService):
        super().__init__()
        self.auth_service = auth_service
        self.system_service = system_service
        self.child_window = None
        self.setWindowTitle("学籍管理系统 - 登录")
        self.resize(1640, 1040)
        self.setMinimumSize(1280, 800)

        container = QWidget()
        self.setCentralWidget(container)
        shell = QHBoxLayout(container)
        shell.setContentsMargins(140, 110, 140, 110)
        shell.setSpacing(90)

        intro = QVBoxLayout()
        intro.setSpacing(24)
        title = QLabel("学籍管理系统")
        title.setObjectName("AppTitle")
        subtitle = QLabel("C/S 架构课程设计 · 学生档案、成绩、学籍异动与附件统一管理")
        subtitle.setObjectName("SubtleText")
        subtitle.setWordWrap(True)
        intro.addStretch(1)
        intro.addWidget(title)
        intro.addWidget(subtitle)
        intro.addSpacing(48)
        for text in ["MySQL 数据库", "PyQt5 桌面客户端", "存储过程 / 函数 / 事务 / 触发器"]:
            label = QLabel(text)
            label.setObjectName("SubtleText")
            intro.addWidget(label)
        intro.addStretch(1)
        shell.addLayout(intro, 1)

        card = QFrame()
        card.setObjectName("LoginCard")
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        card.setFixedWidth(620)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(52, 56, 52, 56)
        layout.setSpacing(28)

        form_title = QLabel("账号登录")
        form_title.setObjectName("PageTitle")
        layout.addWidget(form_title)
        hint_top = QLabel("请选择身份并输入账号密码")
        hint_top.setObjectName("SubtleText")
        layout.addWidget(hint_top)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setSpacing(24)
        self.role_box = QComboBox()
        self.role_box.addItems(["管理员", "学生"])
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("管理员 admin / 学生 PB23111001")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("请输入密码")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form.addRow("角色", self.role_box)
        form.addRow("账号", self.username_edit)
        form.addRow("密码", self.password_edit)
        layout.addLayout(form)

        button = QPushButton("登录")
        button.setMinimumHeight(58)
        button.clicked.connect(self.handle_login)
        layout.addWidget(button)

        hint = QLabel("默认管理员：admin / Admin@123\n默认学生：PB23111001 / Stu@123")
        hint.setObjectName("SubtleText")
        layout.addWidget(hint)
        layout.addStretch(1)
        shell.addWidget(card)

    def handle_login(self):
        try:
            user = self.auth_service.login(
                self.role_box.currentText(),
                self.username_edit.text().strip(),
                self.password_edit.text().strip(),
            )
        except Exception as exc:
            QMessageBox.warning(self, "登录失败", str(exc))
            return

        if user.role == "管理员":
            self.child_window = AdminWindow(user, self.system_service, self.show_login_again)
        else:
            self.child_window = StudentWindow(user, self.system_service, self.show_login_again)
        self.child_window.show()
        self.hide()

    def show_login_again(self):
        self.child_window = None
        self.password_edit.clear()
        self.show()
