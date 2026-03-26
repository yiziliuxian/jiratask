from PySide6.QtCore import Qt, QPoint, QPointF, QRectF, QPropertyAnimation, QEasingCurve, QTimer, Property
from PySide6.QtWidgets import QWidget, QMenu, QApplication, QGraphicsDropShadowEffect
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPainterPath, QRadialGradient, QAction, QRegion


class Ripple:
    def __init__(self, center, max_radius=60):
        self.center = center
        self.radius = 0
        self.max_radius = max_radius
        self.opacity = 1.0
        self.active = True

    def update(self):
        self.radius += 2
        self.opacity -= 0.04
        if self.opacity <= 0:
            self.active = False


class FloatingBall(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAutoFillBackground(False)
        self.resize(100, 100)
        
        self.dragging = False
        self.offset = QPoint()
        self.start_pos = QPoint()
        self.clicked_callback = None
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.OutBack)
        
        self._breath_factor = 0.0
        self.breath_timer = QTimer(self)
        self.breath_timer.timeout.connect(self.update_breath)
        self.breath_timer.start(50)
        self.breath_direction = 1
        
        self.ripples = []
        self.ripple_timer = QTimer(self)
        self.ripple_timer.timeout.connect(self.update_ripples)
        
        self._scale = 1.0
        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        self.settings_window = None
        
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 120, screen.height() // 2 - 50)
        self.update_mask()

    def update_mask(self):
        radius = int(50 * self._scale)
        mask = QRegion(self.width() // 2 - radius, self.height() // 2 - radius, 
                       radius * 2, radius * 2, QRegion.RegionType.Ellipse)
        self.setMask(mask)

    @Property(float)
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = scale
        self.update_mask()
        self.update()

    def update_breath(self):
        step = 0.05
        self._breath_factor += step * self.breath_direction
        if self._breath_factor >= 1.0:
            self._breath_factor = 1.0
            self.breath_direction = -1
        elif self._breath_factor <= 0.0:
            self._breath_factor = 0.0
            self.breath_direction = 1
        self.update()

    def update_ripples(self):
        active_ripples = []
        for r in self.ripples:
            r.update()
            if r.active:
                active_ripples.append(r)
        self.ripples = active_ripples
        if not self.ripples:
            self.ripple_timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPointF(self.width() / 2, self.height() / 2)
        base_radius = 28 * self._scale
        
        glow_radius = base_radius + 5 + (4 * self._breath_factor)
        glow = QRadialGradient(center, glow_radius)
        glow.setColorAt(0.0, QColor(108, 92, 231, 150))
        glow.setColorAt(0.6, QColor(0, 168, 255, 100))
        glow.setColorAt(1.0, QColor(0, 168, 255, 0))
        
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, glow_radius, glow_radius)
        
        for r in self.ripples:
            ripple_color = QColor(255, 255, 255, int(100 * r.opacity))
            painter.setPen(QPen(ripple_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(center, base_radius + r.radius, base_radius + r.radius)

        sphere_rect = QRectF(center.x() - base_radius, center.y() - base_radius, 
                             base_radius * 2, base_radius * 2)
        
        sphere_grad = QRadialGradient(sphere_rect.topLeft(), base_radius * 2)
        sphere_grad.setColorAt(0.0, QColor(255, 255, 255, 180))
        sphere_grad.setColorAt(0.3, QColor(100, 100, 255, 40))
        sphere_grad.setColorAt(1.0, QColor(20, 20, 50, 200))
        
        painter.setBrush(QBrush(sphere_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, base_radius, base_radius)
        
        rim_pen = QPen(QColor(255, 255, 255, 150), 1.5)
        painter.setPen(rim_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, base_radius - 1, base_radius - 1)
        
        highlight_rect = QRectF(center.x() - base_radius * 0.5, center.y() - base_radius * 0.6,
                                base_radius * 0.6, base_radius * 0.4)
        highlight_grad = QRadialGradient(highlight_rect.center(), highlight_rect.width())
        highlight_grad.setColorAt(0.0, QColor(255, 255, 255, 220))
        highlight_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(highlight_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(highlight_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.start_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
            
            self.scale_animation.setStartValue(self._scale)
            self.scale_animation.setEndValue(0.9)
            self.scale_animation.start()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(self.mapToGlobal(event.pos()) - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)
            
            self.scale_animation.setStartValue(self._scale)
            if self.rect().contains(event.pos()):
                self.scale_animation.setEndValue(1.1)
            else:
                self.scale_animation.setEndValue(1.0)
            self.scale_animation.start()
            
            end_pos = event.globalPosition().toPoint()
            distance = (end_pos - self.start_pos).manhattanLength()
            
            if distance < 5:
                self.ripples.append(Ripple(QPoint(self.width()//2, self.height()//2)))
                if not self.ripple_timer.isActive():
                    self.ripple_timer.start(16)
                
                if self.clicked_callback:
                    self.clicked_callback()
            else:
                self.snap_to_edge()

    def snap_to_edge(self):
        screen = QApplication.primaryScreen().availableGeometry()
        pos = self.pos()
        x = pos.x()
        y = pos.y()
        w = self.width()
        h = self.height()
        
        dist_left = x - screen.left()
        dist_right = screen.right() - (x + w)
        
        target_x = x
        if dist_left < dist_right:
            target_x = screen.left()
        else:
            target_x = screen.right() - w
            
        target_y = max(screen.top(), min(y, screen.bottom() - h))
        
        self.animation.setStartValue(QRectF(x, y, w, h))
        self.animation.setEndValue(QRectF(target_x, target_y, w, h))
        self.animation.start()

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        self.scale_animation.setStartValue(self._scale)
        self.scale_animation.setEndValue(1.1)
        self.scale_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        self.scale_animation.setStartValue(self._scale)
        self.scale_animation.setEndValue(1.0)
        self.scale_animation.start()
        super().leaveEvent(event)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setCursor(Qt.PointingHandCursor)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #DFE6E9;
                border-radius: 8px;
                padding: 6px;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                font-size: 13px;
                color: #2D3436;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 6px;
                background-color: transparent;
                color: #2D3436;
            }
            QMenu::item:selected {
                background-color: #6C5CE7;
                color: #FFFFFF;
            }
            QMenu::separator {
                height: 1px;
                background: #DFE6E9;
                margin: 4px 0px;
            }
        """)
        
        show_action = QAction("显示任务列表", self)
        show_action.triggered.connect(self.on_show_tasks_request)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        exit_action = QAction("退出程序", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        
        shadow = QGraphicsDropShadowEffect(menu)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        menu.setGraphicsEffect(shadow)
        
        menu.exec(pos)

    def on_show_tasks_request(self):
        if self.clicked_callback:
            self.clicked_callback()
