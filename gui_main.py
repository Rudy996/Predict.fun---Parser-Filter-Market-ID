# -*- coding: utf-8 -*-
import json
import os
from pathlib import Path

BASE_URL = "https://api.predict.fun"
SETTINGS_FILE = Path(__file__).parent / ".settings.json"


def _load_settings() -> dict:
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text("utf-8"))
        except Exception:
            pass
    return {}


def _save_settings(data: dict) -> None:
    merged = _load_settings()
    merged.update(data)
    SETTINGS_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2), "utf-8")

from PySide6.QtCore import QThread, Signal, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QComboBox,
    QFileDialog,
    QScrollArea,
    QCheckBox,
    QFrame,
    QGridLayout,
    QDialog,
    QRadioButton,
)

from pipeline_runner import run_pipeline

TAGS = [
    ("Sports", "4"),
    ("Politics", "1"),
    ("Crypto", "2"),
    ("New", "3"),
    ("Culture", "13"),
    ("Economy", "6"),
    ("NBA", "78"),
    ("Soccer", "14"),
    ("Esports", "83"),
    ("NFL", "45"),
    ("NHL", "79"),
    ("CS2", "93"),
    ("LoL", "84"),
    ("Cricket", "97"),
    ("Dota 2", "96"),
    ("Olympics", "94"),
    ("Finance", "11"),
    ("NCAAM", "82"),
    ("Oscars", "87"),
]

STATUSES = [
    "",
    "REGISTERED",
    "PRICE_PROPOSED",
    "PRICE_DISPUTED",
    "PAUSED",
    "UNPAUSED",
    "RESOLVED",
    "REMOVED",
]

GLOBAL_STYLE = """
* {
    font-family: "Segoe UI", sans-serif;
}
QWidget#mainWindow {
    background-color: #1a1a1d;
}
QGroupBox {
    font-weight: 600;
    font-size: 13px;
    color: #8e8e93;
    border: 1px solid #3a3a3e;
    border-radius: 12px;
    margin-top: 14px;
    padding: 18px 14px 14px 14px;
    background-color: #2c2c30;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #e0e0e0;
}
QLabel {
    color: #e0e0e0;
    font-size: 12px;
}
QLineEdit {
    padding: 10px 14px;
    border: 1px solid #3a3a3e;
    border-radius: 8px;
    background: #252528;
    color: #e0e0e0;
    font-size: 13px;
}
QLineEdit:focus {
    border-color: #F7931A;
}
QPushButton {
    padding: 10px 20px;
    border: 1px solid #3a3a3e;
    border-radius: 8px;
    background-color: #2c2c30;
    color: #e0e0e0;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #3a3a3e;
    border-color: #F7931A;
}
QPushButton:pressed {
    background-color: #252528;
}
QPushButton#runBtn {
    background-color: #F7931A;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    border: 1px solid #c47a10;
    border-radius: 10px;
}
QPushButton#runBtn:hover {
    background-color: #ffa940;
    border-color: #F7931A;
}
QPushButton#runBtn:disabled {
    background-color: #4a4a4e;
    color: #8e8e93;
    border-color: #4a4a4e;
}
QPushButton#browseBtn {
    border: 1px solid #F7931A;
    color: #F7931A;
    background-color: rgba(247,147,26,0.08);
}
QPushButton#browseBtn:hover {
    background-color: rgba(247,147,26,0.18);
    border-color: #ffa940;
    color: #ffa940;
}
QPushButton#browseBtn:pressed {
    background-color: rgba(247,147,26,0.06);
}
QSpinBox, QComboBox {
    padding: 8px 10px;
    border: 1px solid #3a3a3e;
    border-radius: 8px;
    background: #252528;
    color: #e0e0e0;
    min-width: 150px;
    font-size: 13px;
}
QSpinBox:disabled, QComboBox:disabled {
    background: #1e1e20;
    color: #4a4a4e;
    border-color: #2c2c30;
}
QSpinBox::up-button, QSpinBox::down-button {
    background: rgba(247,147,26,0.25);
    border: none;
    width: 20px;
}
QSpinBox:disabled::up-button, QSpinBox:disabled::down-button {
    background: #2c2c30;
}
QSpinBox:focus, QComboBox:focus {
    border-color: #F7931A;
}
QComboBox::drop-down {
    border: none;
    background: rgba(247,147,26,0.25);
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    width: 24px;
}
QComboBox:disabled::drop-down {
    background: #2c2c30;
}
QComboBox QAbstractItemView {
    background: #2c2c30;
    color: #e0e0e0;
    border: 1px solid #3a3a3e;
    selection-background-color: #3a3a3e;
}
QCheckBox, QRadioButton {
    spacing: 8px;
    color: #e0e0e0;
    font-size: 12px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #3a3a3e;
    background: #252528;
}
QCheckBox::indicator:checked {
    background: #F7931A;
    border-color: #F7931A;
}
QCheckBox::indicator:hover {
    border-color: #ffa940;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 1px solid #3a3a3e;
    background: #252528;
}
QRadioButton::indicator:checked {
    background: #F7931A;
    border-color: #F7931A;
}
QRadioButton::indicator:hover {
    border-color: #ffa940;
}
QScrollArea {
    background: transparent;
    border: none;
}
QLabel#resultLabel {
    color: #4ade80;
    font-size: 13px;
    font-weight: 600;
    padding: 6px 0;
}
QLabel#errorLabel {
    color: #f87171;
    font-size: 13px;
    font-weight: 600;
    padding: 6px 0;
}
"""


class PipelineWorker(QThread):
    step_update = Signal(int, str, str)
    finished_with_result = Signal(list, str)

    def __init__(
        self,
        api_key: str,
        base_url: str,
        market_ids_file: str | None,
        use_all_markets: bool,
        exclude_tag_ids: list[str],
        exclude_tag_names: list[str],
        min_days: int | None,
        require_status: str | None,
        output_file: str,
    ):
        super().__init__()
        self._api_key = api_key
        self._base_url = base_url
        self._market_ids_file = market_ids_file
        self._use_all_markets = use_all_markets
        self._exclude_tag_ids = exclude_tag_ids
        self._exclude_tag_names = exclude_tag_names
        self._min_days = min_days
        self._require_status = require_status or None
        self._output_file = output_file

    def run(self):
        def on_step(idx: int, status: str, detail: str):
            self.step_update.emit(idx, status, detail)

        result, err = run_pipeline(
            api_key=self._api_key,
            base_url=self._base_url,
            market_ids_file=self._market_ids_file,
            use_all_markets=self._use_all_markets,
            exclude_tag_ids=self._exclude_tag_ids,
            exclude_tag_names=self._exclude_tag_names,
            min_days_until_end=self._min_days,
            require_status=self._require_status,
            output_file=self._output_file,
            date_field_order=None,
            step_callback=on_step,
        )
        self.finished_with_result.emit(result, err or "")


class StepRow(QFrame):
    SPINNER_CHARS = ["◐", "◓", "◑", "◒"]

    def __init__(self, step_index: int, label: str, parent=None):
        super().__init__(parent)
        self.step_index = step_index
        self._base_label = label
        self._spinner_idx = 0
        self._spinner_timer = QTimer(self)
        self._spinner_timer.timeout.connect(self._tick_spinner)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        self.icon_label = QLabel("○")
        self.icon_label.setFixedWidth(20)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.text_label = QLabel(label)

        self.detail_label = QLabel("")
        self.detail_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.detail_label.hide()

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.detail_label)

        self._apply_idle()

    def _show_detail(self, text: str):
        if text:
            self.detail_label.setText(text)
            self.detail_label.show()
        else:
            self.detail_label.setText("")
            self.detail_label.hide()

    def _apply_idle(self):
        self.setStyleSheet("background: transparent;")
        self.icon_label.setStyleSheet("color: #6e6e73; font-size: 13px; background: transparent;")
        self.text_label.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent;")
        self.icon_label.setText("○")
        self._show_detail("")

    def set_state(self, state: str, detail: str = ""):
        self._spinner_timer.stop()
        if state == "running":
            self._spinner_idx = 0
            self.setStyleSheet("background: rgba(247,147,26,0.12); border-radius: 6px;")
            self.icon_label.setStyleSheet("color: #F7931A; font-size: 13px; background: transparent;")
            self.text_label.setStyleSheet("color: #e0e0e0; font-size: 12px; font-weight: 600; background: transparent;")
            self.detail_label.setStyleSheet("color: #F7931A; font-size: 11px; background: transparent;")
            self.icon_label.setText(self.SPINNER_CHARS[0])
            self._show_detail(detail)
            self._spinner_timer.start(200)
        elif state == "done":
            self.setStyleSheet("background: rgba(74,222,128,0.1); border-radius: 6px;")
            self.icon_label.setStyleSheet("color: #4ade80; font-size: 13px; font-weight: bold; background: transparent;")
            self.text_label.setStyleSheet("color: #e0e0e0; font-size: 12px; background: transparent;")
            self.detail_label.setStyleSheet("color: #4ade80; font-size: 11px; background: transparent;")
            self.icon_label.setText("✓")
            self._show_detail(detail)
        elif state == "skip":
            self.setStyleSheet("background: transparent;")
            self.icon_label.setStyleSheet("color: #4a4a4e; font-size: 13px; background: transparent;")
            self.text_label.setStyleSheet("color: #4a4a4e; font-size: 12px; background: transparent;")
            self.detail_label.setStyleSheet("color: #4a4a4e; font-size: 11px; background: transparent;")
            self.icon_label.setText("−")
            self._show_detail(detail)
        elif state == "error":
            self.setStyleSheet("background: rgba(248,113,113,0.12); border-radius: 6px;")
            self.icon_label.setStyleSheet("color: #f87171; font-size: 13px; background: transparent;")
            self.text_label.setStyleSheet("color: #fca5a5; font-size: 12px; background: transparent;")
            self.detail_label.setStyleSheet("color: #f87171; font-size: 11px; background: transparent;")
            self.icon_label.setText("✗")
            self._show_detail(detail)
        else:
            self._apply_idle()

    def _tick_spinner(self):
        self._spinner_idx = (self._spinner_idx + 1) % len(self.SPINNER_CHARS)
        self.icon_label.setText(self.SPINNER_CHARS[self._spinner_idx])


def build_step_labels(
    use_all_markets: bool,
    selected_tag_names: list[str],
    has_filter: bool,
) -> list[str]:
    labels = ["Ожидаем настроек пользователя"]
    labels.append(
        "Загрузка всех маркетов с Predict.fun"
        if use_all_markets
        else "Загрузка списка маркетов из файла"
    )
    for name in selected_tag_names:
        labels.append(f"Получаем маркеты по тегу «{name}»")
    labels.append("Вычитаем из нашего списка")
    if has_filter:
        labels.append("Проверяем дату и статус")
    else:
        labels.append("Проверка даты и статуса")
    labels.append("Сохранение результата")
    return labels


class ApiKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Predict.fun — API-ключ")
        self.setFixedWidth(460)
        self.setStyleSheet("""
            QDialog { background: #1a1a1d; }
            QLabel { color: #e0e0e0; font-size: 13px; }
            QLabel#subtitle { color: #8e8e93; font-size: 11px; }
            QLineEdit {
                padding: 12px 14px; border: 1px solid #3a3a3e; border-radius: 8px;
                background: #252528; color: #e0e0e0; font-size: 14px;
            }
            QLineEdit:focus { border-color: #F7931A; }
            QPushButton#okBtn {
                padding: 12px; border-radius: 10px; border: 1px solid #c47a10;
                background: #F7931A; color: #fff; font-size: 14px; font-weight: 700;
            }
            QPushButton#okBtn:hover { background: #ffa940; }
        """)
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Введите API-ключ")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #F7931A;")
        lay.addWidget(title)

        sub = QLabel("Ключ сохранится локально и будет использоваться при следующих запусках.")
        sub.setObjectName("subtitle")
        sub.setWordWrap(True)
        lay.addWidget(sub)

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("x-api-key…")
        lay.addWidget(self.key_edit)

        self.ok_btn = QPushButton("Сохранить")
        self.ok_btn.setObjectName("okBtn")
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.clicked.connect(self._on_ok)
        lay.addWidget(self.ok_btn)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #f87171; font-size: 12px;")
        self.error_label.hide()
        lay.addWidget(self.error_label)

    def _on_ok(self):
        key = self.key_edit.text().strip()
        if not key:
            self.error_label.setText("Ключ не может быть пустым")
            self.error_label.show()
            return
        _save_settings({"api_key": key})
        self.accept()

    def get_key(self) -> str:
        return self.key_edit.text().strip()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.step_rows: list[StepRow] = []
        self.setObjectName("mainWindow")
        self.setWindowTitle("Predict.fun — Фильтр маркетов")
        self.setMinimumWidth(720)
        self.setMinimumHeight(750)
        self.resize(760, 900)

        saved = _load_settings()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #1a1a1d; border: none; }")
        container = QWidget()
        container.setStyleSheet("background: #1a1a1d;")
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(22, 22, 22, 22)
        scroll.setWidget(container)
        outer.addWidget(scroll)

        # Источник маркетов
        source_group = QGroupBox("Источник маркетов")
        source_layout = QVBoxLayout()
        self.radio_my_list = QRadioButton("Мой список (файл с id)")
        self.radio_all_markets = QRadioButton("Все маркеты Predict.fun")
        self.radio_my_list.setChecked(True)
        self.radio_all_markets.toggled.connect(self._on_source_changed)
        source_layout.addWidget(self.radio_my_list)
        source_layout.addWidget(self.radio_all_markets)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)

        # Входной файл
        file_group = QGroupBox("Входной список маркетов")
        fl = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("Путь к файлу (id через запятую)…")
        self.file_edit.setText(saved.get("market_ids_file") or "")
        self.browse_btn = QPushButton("Обзор…")
        self.browse_btn.setObjectName("browseBtn")
        self.browse_btn.clicked.connect(self._browse_input_file)
        fl.addWidget(self.file_edit, 1)
        fl.addWidget(self.browse_btn)
        file_group.setLayout(fl)
        self.file_group = file_group
        layout.addWidget(file_group)

        # Теги для исключения
        tags_group = QGroupBox("Исключить маркеты с тегами")
        grid = QGridLayout()
        grid.setSpacing(8)
        self.tag_checks: list[QCheckBox] = []
        for i, (name, tag_id) in enumerate(TAGS):
            cb = QCheckBox(f"{name}")
            cb.tag_id = tag_id
            cb.tag_name = name
            cb.stateChanged.connect(self._refresh_steps_preview)
            self.tag_checks.append(cb)
            grid.addWidget(cb, i // 4, i % 4)
        tags_group.setLayout(grid)
        layout.addWidget(tags_group)

        # Дни и статус
        opts_group = QGroupBox("Дополнительные фильтры")
        opts_layout = QVBoxLayout()
        opts_layout.setSpacing(10)

        row1 = QHBoxLayout()
        self.days_check = QCheckBox("Мин. дней до конца:")
        self.days_check.setChecked(False)
        self.days_check.stateChanged.connect(self._on_days_toggle)
        self.days_check.stateChanged.connect(self._refresh_steps_preview)
        row1.addWidget(self.days_check)
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        self.days_spin.setEnabled(False)
        self.days_spin.valueChanged.connect(self._refresh_steps_preview)
        row1.addWidget(self.days_spin)
        row1.addStretch()
        opts_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.status_check = QCheckBox("Статус маркета:")
        self.status_check.setChecked(False)
        self.status_check.stateChanged.connect(self._on_status_toggle)
        self.status_check.stateChanged.connect(self._refresh_steps_preview)
        row2.addWidget(self.status_check)
        self.status_combo = QComboBox()
        for s in STATUSES[1:]:
            self.status_combo.addItem(s, s)
        self.status_combo.setEnabled(False)
        self.status_combo.currentIndexChanged.connect(self._refresh_steps_preview)
        row2.addWidget(self.status_combo)
        row2.addStretch()
        opts_layout.addLayout(row2)

        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)

        # Результат
        out_group = QGroupBox("Файл результата")
        ol = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("result.txt")
        self.output_edit.setText("result.txt")
        self.out_browse_btn = QPushButton("Обзор…")
        self.out_browse_btn.setObjectName("browseBtn")
        self.out_browse_btn.clicked.connect(self._browse_output_file)
        ol.addWidget(self.output_edit, 1)
        ol.addWidget(self.out_browse_btn)
        out_group.setLayout(ol)
        layout.addWidget(out_group)

        # Кнопка запуска
        self.run_btn = QPushButton("Извлечь")
        self.run_btn.setObjectName("runBtn")
        self.run_btn.setMinimumHeight(48)
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.clicked.connect(self._run_pipeline)
        layout.addWidget(self.run_btn)

        # Блок шагов
        self.steps_group = QGroupBox("Ход выполнения")
        self.steps_inner_layout = QVBoxLayout()
        self.steps_inner_layout.setSpacing(2)
        self.steps_inner_layout.setContentsMargins(4, 4, 4, 4)
        self.steps_group.setLayout(self.steps_inner_layout)
        self.steps_group.setMinimumWidth(500)
        self._refresh_steps_preview()
        layout.addWidget(self.steps_group)

        # Итоговая строка
        self.result_label = QLabel("")
        self.result_label.setObjectName("resultLabel")
        layout.addWidget(self.result_label)
        layout.addStretch()

    # --- helpers ---

    def _on_source_changed(self):
        use_all = self.radio_all_markets.isChecked()
        self.file_group.setVisible(not use_all)
        self._refresh_steps_preview()

    def _on_days_toggle(self, state):
        self.days_spin.setEnabled(bool(state))

    def _on_status_toggle(self, state):
        self.status_combo.setEnabled(bool(state))

    def _browse_input_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Файл со списком id", "", "Text (*.txt);;All (*)")
        if path:
            self.file_edit.setText(path)

    def _browse_output_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Куда сохранить результат", "result.txt", "Text (*.txt);;All (*)")
        if path:
            self.output_edit.setText(path)

    def _get_selected_tags(self) -> list[tuple[str, str]]:
        return [(cb.tag_name, cb.tag_id) for cb in self.tag_checks if cb.isChecked()]

    def _clear_steps(self):
        while self.steps_inner_layout.count():
            item = self.steps_inner_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self.step_rows = []

    def _refresh_steps_preview(self, _=None):
        """Обновляет блок «Ход выполнения» при каждом изменении настроек."""
        if self.worker and self.worker.isRunning():
            return
        self._clear_steps()
        use_all = self.radio_all_markets.isChecked()
        selected = self._get_selected_tags()
        days_active = self.days_check.isChecked() and self.days_spin.value() > 0
        status_active = self.status_check.isChecked()
        has_filter = days_active or status_active
        labels = build_step_labels(use_all, [name for name, _ in selected], has_filter)
        for i, label in enumerate(labels):
            row = StepRow(i, label)
            self.step_rows.append(row)
            self.steps_inner_layout.addWidget(row)
        if self.step_rows:
            self.step_rows[0].set_state("running")

    def _build_steps_for_run(self):
        self._refresh_steps_preview()

    # --- run ---

    def _ensure_api_key(self) -> str | None:
        saved = _load_settings()
        key = saved.get("api_key") or ""
        if key:
            return key
        dlg = ApiKeyDialog(self)
        if dlg.exec() == QDialog.Accepted:
            return dlg.get_key()
        return None

    def _run_pipeline(self):
        api_key = self._ensure_api_key()
        if not api_key:
            return

        use_all = self.radio_all_markets.isChecked()
        path = self.file_edit.text().strip() if not use_all else None

        if not use_all:
            if not path:
                self._show_error("Укажите файл со списком маркетов.")
                return
            if not Path(path).exists():
                self._show_error(f"Файл не найден: {path}")
                return
            _save_settings({"market_ids_file": path})

        selected = self._get_selected_tags()
        exclude_ids = [tid for _, tid in selected]
        exclude_names = [name for name, _ in selected]
        min_days = self.days_spin.value() if self.days_check.isChecked() else None
        status = self.status_combo.currentData() if self.status_check.isChecked() else None
        output = self.output_edit.text().strip() or "result.txt"
        base_url = BASE_URL

        self._build_steps_for_run()
        if self.step_rows:
            self.step_rows[0].set_state("done", "Настройки приняты")
        self.run_btn.setEnabled(False)
        self.result_label.setText("")
        self.result_label.setObjectName("resultLabel")
        self.result_label.setStyleSheet("")
        self.result_label.style().unpolish(self.result_label)
        self.result_label.style().polish(self.result_label)

        self.worker = PipelineWorker(
            api_key=api_key,
            base_url=base_url,
            market_ids_file=path,
            use_all_markets=use_all,
            exclude_tag_ids=exclude_ids,
            exclude_tag_names=exclude_names,
            min_days=min_days,
            require_status=status,
            output_file=output,
        )
        self.worker.step_update.connect(self._on_step)
        self.worker.finished_with_result.connect(self._on_finished)
        self.worker.start()

    def _on_step(self, step_index: int, status: str, detail: str):
        for row in self.step_rows:
            if row.step_index == step_index:
                row.set_state(status, detail)
                return

    def _on_finished(self, result: list, error: str):
        self.run_btn.setEnabled(True)
        if error:
            self._show_error(f"Ошибка: {error}")
        else:
            out = self.output_edit.text() or "result.txt"
            self.result_label.setObjectName("resultLabel")
            self.result_label.setText(f"Готово. Осталось маркетов: {len(result)}. Сохранено в {out}")
            self.result_label.setStyleSheet("")
            self.result_label.style().unpolish(self.result_label)
            self.result_label.style().polish(self.result_label)

    def _show_error(self, text: str):
        self.result_label.setObjectName("errorLabel")
        self.result_label.setText(text)
        self.result_label.setStyleSheet("")
        self.result_label.style().unpolish(self.result_label)
        self.result_label.style().polish(self.result_label)


def main():
    app = QApplication([])
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_STYLE)

    saved = _load_settings()
    if not saved.get("api_key"):
        dlg = ApiKeyDialog()
        if dlg.exec() != QDialog.Accepted:
            return

    w = MainWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    main()
