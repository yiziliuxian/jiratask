from PySide6.QtCore import Qt, QPoint, QPointF, QRectF, QPropertyAnimation, QEasingCurve, QTimer, Property
from PySide6.QtWidgets import QWidget, QMenu, QApplication, QGraphicsDropShadowEffect
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QRadialGradient, QFont, QAction, QRegion, QLinearGradient


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
        self._hover = False
        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.OutQuad)

        self.settings_window = None

        self._overdue_count = 0
        self._total_count = 0
        self._accent = QColor(108, 92, 231)

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 120, screen.height() // 2 - 50)
        self.update_mask()

    def set_urgency(self, overdue_count, total_count):
        self._overdue_count = overdue_count
        self._total_count = total_count
        if overdue_count == 0:
            self._accent = QColor(0, 184, 148)
        elif overdue_count <= 2:
            self._accent = QColor(253, 203, 110)
        else:
            self._accent = QColor(225, 112, 85)
        self.update()

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
        step = 0.03
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
        base_radius = 26 * self._scale

        # outer glow - breathing pulse
        glow_alpha = 30 + int(25 * self._breath_factor)
        glow_radius = base_radius + 12 + (6 * self._breath_factor)
        glow = QRadialGradient(center, glow_radius)
        glow.setColorAt(0.0, QColor(self._accent.red(), self._accent.green(), self._accent.blue(), glow_alpha))
        glow.setColorAt(0.5, QColor(self._accent.red(), self._accent.green(), self._accent.blue(), glow_alpha // 2))
        glow.setColorAt(1.0, QColor(self._accent.red(), self._accent.green(), self._accent.blue(), 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, glow_radius, glow_radius)

        # ripples
        for r in self.ripples:
            ripple_alpha = int(60 * r.opacity)
            painter.setPen(QPen(QColor(self._accent.red(), self._accent.green(), self._accent.blue(), ripple_alpha), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(center, base_radius + r.radius, base_radius + r.radius)

        # glass sphere - semi-transparent
        sphere_grad = QRadialGradient(
            QPointF(center.x() - base_radius * 0.3, center.y() - base_radius * 0.3),
            base_radius * 1.6
        )
        sphere_grad.setColorAt(0.0, QColor(255, 255, 255, 100))
        sphere_grad.setColorAt(0.2, QColor(self._accent.red(), self._accent.green(), self._accent.blue(), 50))
        sphere_grad.setColorAt(0.6, QColor(self._accent.red(), self._accent.green(), self._accent.blue(), 30))
        sphere_grad.setColorAt(1.0, QColor(self._accent.red(), self._accent.green(), self._accent.blue(), 70))

        painter.setBrush(QBrush(sphere_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, base_radius, base_radius)

        # inner glass ring
        ring_grad = QRadialGradient(center, base_radius)
        ring_grad.setColorAt(0.85, QColor(255, 255, 255, 0))
        ring_grad.setColorAt(0.92, QColor(255, 255, 255, 40))
        ring_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(ring_grad))
        painter.drawEllipse(center, base_radius, base_radius)

        # rim
        rim_alpha = 80 if not self._hover else 160
        painter.setPen(QPen(QColor(255, 255, 255, rim_alpha), 1.2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, base_radius - 0.5, base_radius - 0.5)

        # top highlight
        hl_rect = QRectF(center.x() - base_radius * 0.45, center.y() - base_radius * 0.65,
                         base_radius * 0.55, base_radius * 0.35)
        hl_grad = QRadialGradient(hl_rect.center(), hl_rect.width())
        hl_grad.setColorAt(0.0, QColor(255, 255, 255, 140))
        hl_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(hl_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(hl_rect)

        # bottom reflection
        br_rect = QRectF(center.x() - base_radius * 0.3, center.y() + base_radius * 0.35,
                         base_radius * 0.4, base_radius * 0.2)
        br_grad = QRadialGradient(br_rect.center(), br_rect.width())
        br_grad.setColorAt(0.0, QColor(255, 255, 255, 60))
        br_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(br_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(br_rect)

        # task count in center
        if self._total_count > 0:
            count_font = QFont("Segoe UI", int(11 * self._scale), QFont.Weight.Bold)
            painter.setFont(count_font)
            painter.setPen(QColor(255, 255, 255, 220))
            text_rect = QRectF(center.x() - base_radius, center.y() - base_radius,
                               base_radius * 2, base_radius * 2)
            painter.drawText(text_rect, Qt.AlignCenter, str(self._total_count))

        # overdue badge
        if self._overdue_count > 0:
            badge_radius = 9 * self._scale
            badge_center = QPointF(
                center.x() + base_radius * 0.65,
                center.y() - base_radius * 0.65
            )
            # badge glow
            badge_glow = QRadialGradient(badge_center, badge_radius * 2)
            badge_glow.setColorAt(0.0, QColor(225, 112, 85, 80))
            badge_glow.setColorAt(1.0, QColor(225, 112, 85, 0))
            painter.setBrush(QBrush(badge_glow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(badge_center, badge_radius * 2, badge_radius * 2)

            painter.setBrush(QBrush(QColor(225, 112, 85)))
            painter.setPen(QPen(QColor(255, 255, 255, 200), 1.2))
            painter.drawEllipse(badge_center, badge_radius, badge_radius)

            font = QFont("Segoe UI", int(7 * self._scale), QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))
            badge_rect = QRectF(
                badge_center.x() - badge_radius,
                badge_center.y() - badge_radius,
                badge_radius * 2,
                badge_radius * 2
            )
            painter.drawText(badge_rect, Qt.AlignCenter, str(self._overdue_count))

        painter.end()

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
        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(self.mapToGlobal(event.pos()) - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.PointingHandCursor)

            self.scale_animation.setStartValue(self._scale)
            if self.rect().contains(event.pos()):
                self.scale_animation.setEndValue(1.1)
            else:
                self.scale_animation.setEndValue(1.0)
            self.scale_animation.start()

            end_pos = event.globalPosition().toPoint()
            distance = (end_pos - self.start_pos).manhattanLength()

            if distance < 5:
                self.ripples.append(Ripple(QPoint(self.width() // 2, self.height() // 2)))
                if not self.ripple_timer.isActive():
                    self.ripple_timer.start(16)

                if self.clicked_callback:
                    self.clicked_callback()
            else:
                self.snap_to_edge()

    def snap_to_edge(self):
        screen = QApplication.primaryScreen().availableGeometry()
        pos = self.pos()
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()

        dist_left = x - screen.left()
        dist_right = screen.right() - (x + w)

        target_x = screen.left() if dist_left < dist_right else screen.right() - w
        target_y = max(screen.top(), min(y, screen.bottom() - h))

        self.animation.setStartValue(QRectF(x, y, w, h))
        self.animation.setEndValue(QRectF(target_x, target_y, w, h))
        self.animation.start()

    def enterEvent(self, event):
        self._hover = True
        self.setCursor(Qt.PointingHandCursor)
        self.scale_animation.setStartValue(self._scale)
        self.scale_animation.setEndValue(1.15)
        self.scale_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self.setCursor(Qt.ArrowCursor)
        self.scale_animation.setStartValue(self._scale)
        self.scale_animation.setEndValue(1.0)
        self.scale_animation.start()
        super().leaveEvent(event)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setCursor(Qt.PointingHandCursor)
        menu.setWindowFlags(menu.windowFlags() | Qt.NoDropShadowWindowHint)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E8E4F8;
                border-radius: 12px;
                padding: 8px;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 8px 28px 8px 14px;
                border-radius: 8px;
                background-color: transparent;
                color: #2D3436;
            }
            QMenu::item:selected {
                background-color: #6C5CE7;
                color: #FFFFFF;
            }
            QMenu::separator {
                height: 1px;
                background: #F0F0F0;
                margin: 4px 8px;
            }
        """)

        show_action = QAction("📋  显示任务列表", self)
        show_action.triggered.connect(self.on_show_tasks_request)
        menu.addAction(show_action)

        menu.addSeparator()

        exit_action = QAction("✕  退出程序", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)

        menu.exec(pos)

    def on_show_tasks_request(self):
        if self.clicked_callback:
            self.clicked_callback()
