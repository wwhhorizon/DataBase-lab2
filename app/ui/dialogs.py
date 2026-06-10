from __future__ import annotations

from typing import Any

from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QDoubleSpinBox,
)
from PyQt5.QtCore import QDate


class FormDialog(QDialog):
    def __init__(self, title: str, fields: list[dict[str, Any]], data: dict[str, Any] | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(460, 320)
        self.fields = fields
        self.widgets: dict[str, Any] = {}
        layout = QFormLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)
        data = data or {}

        for field in fields:
            name = field["name"]
            kind = field.get("type", "text")
            if kind == "combo":
                widget = QComboBox()
                for label, value in field["options"]:
                    widget.addItem(label, value)
                if name in data:
                    idx = widget.findData(data[name])
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
            elif kind == "multiline":
                widget = QPlainTextEdit()
                widget.setPlainText(str(data.get(name, "")))
            elif kind == "int":
                widget = QSpinBox()
                widget.setRange(field.get("min", 0), field.get("max", 999999))
                widget.setValue(int(data.get(name, field.get("default", 0))))
            elif kind == "float":
                widget = QDoubleSpinBox()
                widget.setDecimals(2)
                widget.setRange(field.get("min", 0), field.get("max", 100))
                widget.setValue(float(data.get(name, field.get("default", 0))))
            elif kind == "date":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                date_value = data.get(name)
                widget.setDate(QDate.fromString(date_value, "yyyy-MM-dd") if date_value else QDate.currentDate())
            else:
                widget = QLineEdit()
                widget.setText(str(data.get(name, "")))
                if field.get("echo_mode") == "password":
                    widget.setEchoMode(QLineEdit.Password)
            self.widgets[name] = widget
            layout.addRow(field["label"], widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def values(self) -> dict[str, Any]:
        result = {}
        for field in self.fields:
            widget = self.widgets[field["name"]]
            kind = field.get("type", "text")
            if kind == "combo":
                result[field["name"]] = widget.currentData()
            elif kind == "multiline":
                result[field["name"]] = widget.toPlainText().strip()
            elif kind in {"int", "float"}:
                result[field["name"]] = widget.value()
            elif kind == "date":
                result[field["name"]] = widget.date().toString("yyyy-MM-dd")
            else:
                result[field["name"]] = widget.text().strip()
        return result
