from PySide6.QtCore import Qt, QSortFilterProxyModel, QPoint, QPropertyAnimation, QEasingCurve, QRectF
from PySide6.QtWidgets import QTableView, QVBoxLayout, QWidget, QPushButton, QDialog, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor, QPainter, QBrush, QPen
from task_model import JiraTaskModel
from mock_data import generate_mock_tasks


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.drag_pos = QPoint()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 0, 15, 0)
        
        self.back_btn = QPushButton("×")
        self.back_btn.setFixedSize(30, 30)
        self.back_btn.setStyleSheet("""
            border: none;
            font-size: 20px;
            font-weight: bold;
            color: #2D3436;
            background: transparent;
        """)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.window().hide)
        
        self.title_label = QPushButton("Jira 任务列表")
        self.title_label.setStyleSheet("""
            border: none;
            font-size: 16px;
            font-weight: 600;
            color: #2D3436;
            background: transparent;
        """)
        self.title_label.setCursor(Qt.PointingHandCursor)
        
        layout.addWidget(self.back_btn)
        layout.addWidget(self.title_label, 1)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #FFFFFF;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()


class TaskWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(600, 500)
        
        self.drag_pos = QPoint()
        
        self.model = JiraTaskModel()
        self.refresh_data()

        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            QWidget#container {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
        """)

        title_bar = CustomTitleBar(self)
        title_bar.mousePressEvent = lambda e: self.start_drag(e)
        title_bar.mouseMoveEvent = lambda e: self.on_drag(e)
        title_bar.mouseReleaseEvent = lambda e: self.end_drag(e)

        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setStretchLastSection(False)
        self.table_view.setWordWrap(False)
        self.table_view.setColumnWidth(0, 80)
        self.table_view.setColumnWidth(1, 325)
        self.table_view.setColumnWidth(2, 100)
        self.table_view.setColumnWidth(3, 50)
        self.table_view.setStyleSheet("""
            QTableView {
                border: none;
                background-color: #FFFFFF;
                alternate-background-color: #F8F9FA;
                gridline-color: #DFE6E9;
            }
            QTableView::item {
                padding: 8px;
                border-bottom: 1px solid #DFE6E9;
            }
            QHeaderView::section {
                background-color: #F8F9FA;
                color: #2D3436;
                font-weight: 600;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #6C5CE7;
            }
            QTableView::item:selected {
                background-color: rgba(108, 92, 231, 0.1);
                color: #2D3436;
            }
        """)

        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setFixedHeight(36)
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #5B4CD4;
            }
            QPushButton:pressed {
                background-color: #4A3DC3;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_data)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(title_bar)
        layout.addWidget(self.table_view)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_button)
        btn_layout.addStretch()
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addLayout(layout)
        main_layout.addLayout(btn_layout)
        
        container.setLayout(main_layout)
        
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(container)
        self.setLayout(window_layout)

        self.table_view.sortByColumn(2, Qt.AscendingOrder)

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

    def refresh_data(self):
        tasks = generate_mock_tasks()
        self.model.setTasks(tasks)
