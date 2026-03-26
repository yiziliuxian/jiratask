from datetime import datetime, timedelta


def generate_mock_tasks():
    today = datetime.now().date()
    tasks = [
        {"key": "PROJ-101", "summary": "完成需求文档", "duedate": (today + timedelta(days=2)).isoformat(), "status": "进行中"},
        {"key": "PROJ-102", "summary": "修复登录Bug", "duedate": (today - timedelta(days=1)).isoformat(), "status": "待测试"},
        {"key": "PROJ-103", "summary": "更新用户手册，更新用户手册，更新用户手册，更新用户手册", "duedate": (today + timedelta(days=5)).isoformat(), "status": "未开始"},
        {"key": "PROJ-104", "summary": "性能优化", "duedate": (today + timedelta(days=0)).isoformat(), "status": "进行中"},
        {"key": "PROJ-105", "summary": "代码审查", "duedate": (today - timedelta(days=3)).isoformat(), "status": "已完成"},
        {"key": "PROJ-106", "summary": "部署测试环境", "duedate": (today + timedelta(days=1)).isoformat(), "status": "待部署"},
        {"key": "PROJ-107", "summary": "编写单元测试", "duedate": (today + timedelta(days=4)).isoformat(), "status": "未开始"},
    ]
    tasks.sort(key=lambda x: x["duedate"])
    return tasks
