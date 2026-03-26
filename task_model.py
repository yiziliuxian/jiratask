from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


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
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        task = self._tasks[index.row()]
        col = index.column()
        if col == 0:
            return task['key']
        elif col == 1:
            return task['summary']
        elif col == 2:
            return task['duedate']
        elif col == 3:
            return task['status']
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def setTasks(self, tasks):
        self.beginResetModel()
        self._tasks = tasks
        self.endResetModel()
