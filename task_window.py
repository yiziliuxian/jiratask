from PySide6.QtCore import Qt, QSortFilterProxyModel, QPoint, QUrl, QSize, QRect, QRectF
from PySide6.QtWidgets import (QTableView, QVBoxLayout, QWidget, QPushButton,
                                QDialog, QHBoxLayout, QGraphicsDropShadowEffect,
                                QStyledItemDelegate, QStyleOptionViewItem, QApplication,
                                QLabel, QSizePolicy, QScrollArea)
from PySide6.QtGui import (QColor, QDesktopServices, QCursor, QPainter, QPen,
                            QFont, QFontMetrics, QIcon, QLinearGradient, QRadialGradient)


class TaskCard(QWidget):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self._hovered = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(72)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setToolTip(f"Click to open {task.get('key', '')} in browser")

    def set_hovered(self, hovered):
        if self._hovered != hovered:
            self._hovered = hovered
            self.update()

    def enterEvent(self, event):
        self.set_hovered(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.set_hovered(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            url = self.task.get('url', '')
            if url:
                QDesktopServices.openUrl(QUrl(url))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        is_overdue = self.task.get('is_overdue', False)
        is_today = self.task.get('is_today', False)
        is_approaching = self.task.get('is_approaching', False)
        w = self.width()
        h = self.height()
        margin = 8
        radius = 8

        card_rect = QRectF(margin, 2, w - margin * 2, h - 4)

        if self._hovered:
            if is_overdue:
                bg = QColor('#FFF0EE')
            elif is_approaching:
                bg = QColor('#FFF9F0')
            else:
                bg = QColor('#F0EDFF')
        else:
            if is_overdue:
                bg = QColor('#FFF5F3')
            elif is_approaching:
                bg = QColor('#FFFBF5')
            else:
                bg = QColor('#FAFBFC')
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg)
        painter.drawRoundedRect(card_rect, radius, radius)

        border_pen = QPen(QColor('#E8E8E8'), 1)
        if self._hovered:
            if is_overdue:
                border_pen = QPen(QColor('#E17055'), 1.5)
            elif is_approaching:
                border_pen = QPen(QColor('#E67E22'), 1.5)
            else:
                border_pen = QPen(QColor('#6C5CE7'), 1.5)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(card_rect, radius, radius)

        if is_overdue:
            stripe_color = QColor('#E17055')
        elif is_approaching:
            stripe_color = QColor('#E67E22')
        elif is_today:
            stripe_color = QColor('#FDCB6E')
        else:
            stripe_color = QColor('#6C5CE7')
        stripe_rect = QRectF(margin + 1, 2 + radius, 4, h - 4 - radius * 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(stripe_color)
        painter.drawRoundedRect(stripe_rect, 2, 2)

        content_x = margin + 16
        content_w = w - margin * 2 - 32

        key_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        summary_font = QFont("Segoe UI", 10)
        date_font = QFont("Segoe UI", 9)
        badge_font = QFont("Segoe UI", 8, QFont.Weight.Bold)

        painter.setFont(key_font)
        key = self.task.get('key', '')
        key_color = QColor('#6C5CE7')
        painter.setPen(key_color)
        painter.drawText(QRect(content_x, 10, 120, 20), Qt.AlignLeft | Qt.AlignVCenter, key)

        painter.setFont(summary_font)
        summary = self.task.get('summary', '')
        painter.setPen(QColor('#2D3436'))
        fm = QFontMetrics(summary_font)
        elided = fm.elidedText(summary, Qt.ElideRight, content_w - 160)
        painter.drawText(QRect(content_x, 32, content_w - 160, 20), Qt.AlignLeft | Qt.AlignVCenter, elided)

        status = self.task.get('status', '')
        painter.setFont(badge_font)
        status_fm = QFontMetrics(badge_font)
        status_w = max(status_fm.horizontalAdvance(status) + 16, 50)
        status_x = w - margin - status_w - 12
        status_y = 10
        status_rect = QRectF(status_x, status_y, status_w, 22)

        status_colors = {
            'overdue': (QColor('#FDE8E4'), QColor('#E17055')),
            'approaching': (QColor('#FFF3CD'), QColor('#E67E22')),
            'today': (QColor('#FFF3CD'), QColor('#E67E22')),
            'progress': (QColor('#E8F5E9'), QColor('#00B894')),
            'default': (QColor('#EBE8FF'), QColor('#6C5CE7')),
        }
        if is_overdue:
            bg_c, fg_c = status_colors['overdue']
        elif is_approaching:
            bg_c, fg_c = status_colors['approaching']
        elif is_today:
            bg_c, fg_c = status_colors['today']
        else:
            bg_c, fg_c = status_colors['default']

        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_c)
        painter.drawRoundedRect(status_rect, 11, 11)
        painter.setPen(fg_c)
        painter.drawText(status_rect, Qt.AlignCenter, status)

        duedate = self.task.get('duedate', '')
        if duedate:
            painter.setFont(date_font)
            date_x = w - margin - 12
            date_y = 42

            if is_overdue:
                painter.setPen(QColor('#E17055'))
                date_text = f"● {duedate}  OVERDUE"
            elif is_approaching:
                painter.setPen(QColor('#E67E22'))
                date_text = duedate
            elif is_today:
                painter.setPen(QColor('#E67E22'))
                date_text = f"● {duedate}  TODAY"
            else:
                painter.setPen(QColor('#636E72'))
                date_text = duedate

            date_fm = QFontMetrics(date_font)
            date_w = date_fm.horizontalAdvance(date_text)
            painter.drawText(QRect(date_x - date_w, date_y, date_w + 4, 18), Qt.AlignRight | Qt.AlignVCenter, date_text)

        painter.end()


class CustomTitleBar(QWidget):
    def __init__(self, overdue=0, total=0, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self.drag_pos = QPoint()

        layout = QHBoxLayout()
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(10)

        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 18px;
                font-weight: bold;
                color: #636E72;
                background: transparent;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #FFEAA7;
                color: #2D3436;
            }
        """)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.window().hide)

        self.title_label = QLabel("📋  Jira Tasks")
        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #2D3436;
            background: transparent;
            font-family: "Segoe UI", "Microsoft YaHei";
        """)

        self.count_label = QLabel(f"{total} tasks")
        self.count_label.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #FFFFFF;
            background-color: #6C5CE7;
            border-radius: 10px;
            padding: 2px 10px;
        """)
        self.count_label.setFixedHeight(22)
        self.count_label.setAlignment(Qt.AlignCenter)

        self.overdue_label = QLabel()
        if overdue > 0:
            self.overdue_label.setText(f"⚠ {overdue} overdue")
            self.overdue_label.setStyleSheet("""
                font-size: 11px;
                font-weight: 600;
                color: #E17055;
                background-color: #FFF0EE;
                border-radius: 10px;
                padding: 2px 10px;
            """)
            self.overdue_label.setFixedHeight(22)
        self.overdue_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.close_btn)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.overdue_label)
        layout.addWidget(self.count_label)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #FFFFFF;")

    def update_counts(self, overdue, total):
        self.count_label.setText(f"{total} tasks")
        if overdue > 0:
            self.overdue_label.setText(f"⚠ {overdue} overdue")
            self.overdue_label.setStyleSheet("""
                font-size: 11px;
                font-weight: 600;
                color: #E17055;
                background-color: #FFF0EE;
                border-radius: 10px;
                padding: 2px 10px;
            """)
        else:
            self.overdue_label.setText("")
            self.overdue_label.setStyleSheet("background: transparent;")


class TaskWindow(QDialog):
    def __init__(self, tasks=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(560, 560)

        self.drag_pos = QPoint()
        self._tasks = tasks or []
        self._refresh_callback = None

        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            QWidget#container {
                background-color: #FFFFFF;
                border-radius: 16px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(container)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        overdue = sum(1 for t in self._tasks if t.get('is_overdue'))
        total = len(self._tasks)
        self.title_bar = CustomTitleBar(overdue, total, self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #DFE6E9;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #B2BEC3;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        self.list_widget = QWidget()
        self.list_widget.setStyleSheet("background-color: transparent;")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(4, 4, 4, 4)
        self.list_layout.setSpacing(2)
        self.list_layout.addStretch()

        self.scroll_area.setWidget(self.list_widget)
        self._rebuild_cards()

        self.refresh_button = QPushButton("↻  Refresh")
        self.refresh_button.setFixedSize(110, 36)
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                font-family: "Segoe UI", "Microsoft YaHei";
            }
            QPushButton:hover {
                background-color: #5B4CD4;
            }
            QPushButton:pressed {
                background-color: #4A3DC3;
            }
        """)
        self.refresh_button.clicked.connect(self.on_refresh_request)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_button)
        btn_layout.addStretch()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.title_bar)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #F0F0F0;")
        content_layout.addWidget(sep)

        content_layout.addWidget(self.scroll_area, 1)

        sep2 = QWidget()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background-color: #F0F0F0;")
        content_layout.addWidget(sep2)

        footer = QWidget()
        footer.setFixedHeight(56)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(18, 8, 18, 8)
        footer_layout.addStretch()
        footer_layout.addWidget(self.refresh_button)
        footer_layout.addStretch()
        footer.setStyleSheet("background-color: #FAFBFC; border-radius: 0 0 16px 16px;")
        content_layout.addWidget(footer)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(content_layout)

        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(16, 16, 16, 16)
        window_layout.addWidget(container)
        self.setLayout(window_layout)

    def _rebuild_cards(self):
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        sorted_tasks = sorted(self._tasks, key=lambda t: (not t.get('is_overdue'), t.get('duedate', '9999')))
        for task in sorted_tasks:
            card = TaskCard(task, self.list_widget)
            self.list_layout.insertWidget(self.list_layout.count() - 1, card)

    def set_refresh_callback(self, callback):
        self._refresh_callback = callback

    def update_tasks(self, tasks):
        self._tasks = tasks
        overdue = sum(1 for t in tasks if t.get('is_overdue'))
        total = len(tasks)
        self.title_bar.update_counts(overdue, total)
        self._rebuild_cards()

    def on_refresh_request(self):
        if self._refresh_callback:
            self._refresh_callback()

    def on_row_clicked(self, index):
        pass

    def start_drag(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def on_drag(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def end_drag(self, event):
        pass

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def get_overdue_count(self):
        return sum(1 for t in self._tasks if t.get('is_overdue'))

    def get_total_count(self):
        return len(self._tasks)
