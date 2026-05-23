from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor, QFont


class JiraTaskModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._headers = ['Key', 'Summary', 'Due Date', 'Status']

    def rowCount(self, parent=QModelIndex()):
        return len(self._tasks)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        task = self._tasks[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return task['key']
            elif col == 1:
                return task['summary']
            elif col == 2:
                return task['duedate']
            elif col == 3:
                return task['status']
            return None

        if role == Qt.UserRole:
            return task.get('url', '')

        if role == Qt.ForegroundRole and col == 2:
            if task.get('is_overdue'):
                return QColor('#E17055')
            if task.get('is_today'):
                return QColor('#FDCB6E')
            return None

        if role == Qt.FontRole and col == 0:
            font = QFont()
            font.setUnderline(True)
            return font

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def setTasks(self, tasks):
        self.beginResetModel()
        self._tasks = tasks
        self.endResetModel()

    def get_overdue_count(self):
        return sum(1 for t in self._tasks if t.get('is_overdue'))

    def get_total_count(self):
        return len(self._tasks)
