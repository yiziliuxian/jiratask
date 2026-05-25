import json
import os
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_http = urllib3.PoolManager(cert_reqs='CERT_NONE')

DEBUG_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jira_debug.log')
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')


def _debug(msg):
    with open(DEBUG_LOG, 'a', encoding='utf-8') as f:
        f.write(f'[{datetime.now().isoformat()}] {msg}\n')


def _clear_debug():
    with open(DEBUG_LOG, 'w', encoding='utf-8') as f:
        f.write('')


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def _api_get(url, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    resp = _http.request('GET', url, headers=headers)
    if resp.status >= 400:
        raise Exception(f'HTTP {resp.status}: {resp.data.decode("utf-8", errors="replace")[:500]}')
    return json.loads(resp.data.decode('utf-8'))


def _verify_connection(jira_url, token):
    _api_get(f'{jira_url}/rest/api/2/myself', token)


def _find_end_date_field(jira_url, token):
    fields = _api_get(f'{jira_url}/rest/api/2/field', token)
    for field in fields:
        if field['name'] == 'End date':
            _debug(f'Found "End date" field: {field["id"]}')
            return field['id']
    _debug('"End date" field not found, falling back to duedate')
    return None


def fetch_jira_tasks(config):
    _clear_debug()
    jira_url = config['jira_url'].rstrip('/')
    token = config['api_token']

    _verify_connection(jira_url, token)
    _debug('Connected via PAT')

    end_date_field = _find_end_date_field(jira_url, token)

    if end_date_field:
        field_number = end_date_field.split('_')[1]
        order_clause = f'cf[{field_number}] ASC'
    else:
        order_clause = 'duedate ASC'

    jql = f'assignee = currentUser() AND resolution = Unresolved ORDER BY {order_clause}'
    _debug(f'JQL: {jql}')

    fetch_fields = 'key,summary,status,duedate'
    if end_date_field:
        fetch_fields += f',{end_date_field}'

    import urllib.parse
    jql_encoded = urllib.parse.quote(jql)
    search_url = f'{jira_url}/rest/api/2/search?jql={jql_encoded}&maxResults=100&fields={fetch_fields}'
    data = _api_get(search_url, token)
    issues = data.get('issues', [])
    _debug(f'Found {len(issues)} issues')

    tasks = []
    today = datetime.now().date()
    for issue in issues:
        fields = issue.get('fields', {})
        key = issue.get('key', '')
        summary = fields.get('summary', '')
        status_obj = fields.get('status', {})
        status_name = status_obj.get('name', '') if status_obj else ''

        if end_date_field:
            duedate_raw = fields.get(end_date_field)
        else:
            duedate_raw = fields.get('duedate')

        if duedate_raw:
            duedate = datetime.strptime(str(duedate_raw)[:10], '%Y-%m-%d').date()
            duedate_str = duedate.isoformat()
        else:
            duedate = None
            duedate_str = ''

        task_url = f'{jira_url}/browse/{key}'
        is_overdue = duedate is not None and duedate < today
        is_today = duedate is not None and duedate == today

        tasks.append({
            'key': key,
            'summary': summary,
            'duedate': duedate_str,
            'status': status_name,
            'url': task_url,
            'is_overdue': is_overdue,
            'is_today': is_today,
        })

    _debug(f'Returned {len(tasks)} tasks')
    return tasks


if __name__ == '__main__':
    cfg = load_config()
    if not cfg:
        print('config.json not found')
    else:
        print(f'Connecting to {cfg["jira_url"]}...')
        try:
            tasks = fetch_jira_tasks(cfg)
            print(f'\nReturned {len(tasks)} tasks:')
            for t in tasks:
                overdue = ' [OVERDUE]' if t['is_overdue'] else ''
                today_mark = ' [TODAY]' if t['is_today'] else ''
                print(f"  {t['key']}: {t['summary'][:40]} | {t['status']} | {t['duedate']}{overdue}{today_mark}")
        except Exception as e:
            print(f'ERROR: {e}')
        print(f'\nDebug log: {DEBUG_LOG}')
