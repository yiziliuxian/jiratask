import sys
from PySide6.QtWidgets import QApplication
from floating_ball import FloatingBall
from task_window import TaskWindow


class FloatingBallWithTask(FloatingBall):
    def __init__(self):
        super().__init__()
        self.task_window = None
        self.clicked_callback = self.show_task_window

    def show_task_window(self):
        if self.task_window is None or not self.task_window.isVisible():
            self.task_window = TaskWindow()
            self.task_window.finished.connect(self.on_task_window_closed)
            self.task_window.show()

    def on_task_window_closed(self):
        self.task_window = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    ball = FloatingBallWithTask()
    ball.show()
    
    sys.exit(app.exec())
