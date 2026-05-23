from datetime import datetime, timedelta


def generate_mock_tasks():
    today = datetime.now().date()
    tasks = [
        {"key": "PROJ-101", "summary": "完成需求文档", "duedate": (today + timedelta(days=2)).isoformat(), "status": "进行中", "url": "https://jira.calterah.com/browse/PROJ-101", "is_overdue": False, "is_today": False},
        {"key": "PROJ-102", "summary": "修复登录Bug", "duedate": (today - timedelta(days=1)).isoformat(), "status": "待测试", "url": "https://jira.calterah.com/browse/PROJ-102", "is_overdue": True, "is_today": False},
        {"key": "PROJ-103", "summary": "更新用户手册，更新用户手册，更新用户手册，更新用户手册", "duedate": (today + timedelta(days=5)).isoformat(), "status": "未开始", "url": "https://jira.calterah.com/browse/PROJ-103", "is_overdue": False, "is_today": False},
        {"key": "PROJ-104", "summary": "性能优化", "duedate": (today + timedelta(days=0)).isoformat(), "status": "进行中", "url": "https://jira.calterah.com/browse/PROJ-104", "is_overdue": False, "is_today": True},
        {"key": "PROJ-105", "summary": "代码审查", "duedate": (today - timedelta(days=3)).isoformat(), "status": "已完成", "url": "https://jira.calterah.com/browse/PROJ-105", "is_overdue": True, "is_today": False},
        {"key": "PROJ-106", "summary": "部署测试环境", "duedate": (today + timedelta(days=1)).isoformat(), "status": "待部署", "url": "https://jira.calterah.com/browse/PROJ-106", "is_overdue": False, "is_today": False},
        {"key": "PROJ-107", "summary": "编写单元测试", "duedate": (today + timedelta(days=4)).isoformat(), "status": "未开始", "url": "https://jira.calterah.com/browse/PROJ-107", "is_overdue": False, "is_today": False},
    ]
    tasks.sort(key=lambda x: x["duedate"])
    return tasks
