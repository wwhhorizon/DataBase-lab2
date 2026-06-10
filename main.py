from PyQt5.QtWidgets import QApplication, QMessageBox

from app.config.settings import Settings
from app.db.connection import Database
from app.services.auth_service import AuthService
from app.services.system_service import SystemService
from app.ui.login_window import LoginWindow
from app.ui.theme import APP_STYLESHEET


def main() -> int:
    settings = Settings.load()
    app = QApplication([])
    app.setApplicationName("学籍管理系统")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    try:
        database = Database(settings.database)
    except Exception as exc:  # pragma: no cover - UI startup path
        QMessageBox.critical(None, "数据库连接失败", str(exc))
        return 1

    auth_service = AuthService(database)
    system_service = SystemService(database, settings)
    window = LoginWindow(auth_service, system_service)
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
