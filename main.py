import sys
import urllib3

from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont, QRadialGradient

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from floating_ball import FloatingBall
from task_window import TaskWindow
from jira_client import load_config, save_config, fetch_jira_tasks, CONFIG_PATH
from mock_data import generate_mock_tasks


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Jira 配置")
        self.setFixedSize(400, 220)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Jira 服务器地址:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://jira.calterah.com")
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel("Personal Access Token (PAT):"))
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setPlaceholderText("MTgyMDcy...")
        layout.addWidget(self.token_input)

        pat_hint = QLabel("生成 PAT: Jira右上角个人头像 → 个人访问令牌")
        pat_hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(pat_hint)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("保存")
        self.ok_btn.clicked.connect(self.on_save)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def on_save(self):
        url = self.url_input.text().strip()
        token = self.token_input.text().strip()

        if not url or not token:
            QMessageBox.warning(self, "错误", "所有字段都必须填写。")
            return

        if not url.startswith("http"):
            url = "https://" + url

        config = {
            "jira_url": url,
            "api_token": token,
        }

        try:
            tasks = fetch_jira_tasks(config)
            save_config(config)
            if tasks:
                QMessageBox.information(self, "成功", f"连接成功，找到 {len(tasks)} 个任务。")
            else:
                QMessageBox.warning(self, "连接成功", "连接成功，但未找到任务。\n\n可能原因:\n1. 该账号没有被分配任务\n2. 所有任务状态已关闭\n\n详细日志: jira_debug.log")
            self.accept()
        except Exception as e:
            err_str = str(e)
            hint = ""
            if "403" in err_str:
                hint = "\n\n提示: 403 错误通常表示认证被拒绝。\n请确认:\n1. 用户名和密码/PAT 正确\n2. 该账号有权访问 Jira REST API\n3. 如使用 PAT，请确认它未过期"
            elif "401" in err_str:
                hint = "\n\n提示: 用户名或密码/PAT 不正确。"
            QMessageBox.critical(self, "连接失败", f"无法连接到 Jira 服务器:\n{e}{hint}")


class FloatingBallWithTask(FloatingBall):
    def __init__(self):
        super().__init__()
        self.task_window = None
        self.clicked_callback = self.show_task_window
        self._tasks = []
        self._config = None

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_tasks)
        self.refresh_timer.start(5 * 60 * 1000)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self._create_tray_icon())
        self.tray_icon.setToolTip("JiraTask")

        tray_menu = QMenu()
        show_action = tray_menu.addAction("显示任务列表")
        show_action.triggered.connect(self.show_task_window)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("退出")
        quit_action.triggered.connect(QApplication.quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def _create_tray_icon(self):
        size = 256
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        center = QPointF(size / 2, size / 2)
        radius = 112

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(108, 92, 231)))
        painter.drawEllipse(center, radius, radius)

        font = QFont("Segoe UI", 96, QFont.Weight.Bold)
        font.setPixelSize(int(radius * 2))
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(0, 0, size, size), Qt.AlignCenter, "J")
        painter.end()
        return QIcon(pixmap)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_task_window()

    def load_and_fetch(self):
        self._config = load_config()
        if self._config is None:
            dialog = ConfigDialog()
            if dialog.exec() != QDialog.Accepted:
                self._tasks = generate_mock_tasks()
                self._update_urgency()
                return
            self._config = load_config()

        self.refresh_tasks()

    def refresh_tasks(self):
        if self._config:
            try:
                self._tasks = fetch_jira_tasks(self._config)
            except Exception as e:
                self._tasks = generate_mock_tasks()
        else:
            self._tasks = generate_mock_tasks()

        self._update_urgency()

        if self.task_window and self.task_window.isVisible():
            self.task_window.update_tasks(self._tasks)

    def _update_urgency(self):
        overdue = sum(1 for t in self._tasks if t.get('is_overdue'))
        total = len(self._tasks)
        self.set_urgency(overdue, total)

    def show_task_window(self):
        if self.task_window is None or not self.task_window.isVisible():
            self.task_window = TaskWindow(tasks=self._tasks)
            self.task_window.finished.connect(self.on_task_window_closed)
            self.task_window.set_refresh_callback(self.refresh_tasks)
            self.task_window.show()
        else:
            self.task_window.raise_()
            self.task_window.activateWindow()

    def on_task_window_closed(self):
        self.task_window = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    ball = FloatingBallWithTask()
    ball.show()
    ball.load_and_fetch()
    
    sys.exit(app.exec())
