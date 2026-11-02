"""Generate a GitHub-safe SVG scene and a small public activity feed. Stdlib only."""

import argparse
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = 'helililili'
LOCAL = timezone(timedelta(hours=8))
START, END = '<!-- ACTIVITY:START -->', '<!-- ACTIVITY:END -->'
FONT = "'Segoe UI','Microsoft YaHei','PingFang SC',sans-serif"
MONO = "'Cascadia Code',Consolas,monospace"


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(content, encoding='utf-8', newline='\n')
    temp.replace(path)


def stamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(LOCAL)


def environment(now):
    now = now.astimezone(LOCAL)
    hour = now.hour
    phase = 'DAWN' if 5 <= hour < 8 else 'DAY' if 8 <= hour < 17 else 'DUSK' if 17 <= hour < 20 else 'NIGHT'
    season = ('WINTER', 'SPRING', 'SUMMER', 'AUTUMN')[(now.month % 12) // 3]
    accents = {'SPRING': '#258876', 'SUMMER': '#187b91', 'AUTUMN': '#af7348', 'WINTER': '#6c82aa'}
    return phase, season, accents[season]


def palette(dark):
    return ({'bg': '#101c2b', 'panel': '#152537', 'ink': '#e6edf5', 'muted': '#a1b3c5', 'line': '#304356', 'teal': '#70d4c1', 'soft': '#213e43', 'warm': '#e6ae7d'} if dark else
            {'bg': '#f1f5f7', 'panel': '#ffffff', 'ink': '#203449', 'muted': '#536b7f', 'line': '#d0dce4', 'teal': '#197f73', 'soft': '#deece9', 'warm': '#ad6f3c'})


def txt(x, y, content, size=14, fill='currentColor', weight=400, mono=False, extra=''):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="{escape(MONO if mono else FONT, quote=True)}" font-size="{size}" font-weight="{weight}" {extra}>{escape(str(content))}</text>'


def svg(title, desc, width, height, body):
    style = '''<style>
    .flow{stroke-dasharray:4 42;animation:flow 16s linear infinite}
    .pulse{animation:pulse 7s ease-in-out infinite}
    .cloud{animation:cloud 26s ease-in-out infinite}
    @keyframes flow{to{stroke-dashoffset:-184}}
    @keyframes pulse{0%,100%{opacity:.38}50%{opacity:.85}}
    @keyframes cloud{0%,100%{transform:translateX(0)}50%{transform:translateX(12px)}}
    @media(prefers-reduced-motion:reduce){.flow,.pulse,.cloud{animation:none}}
    </style>'''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>{style}{body}</svg>\n'


def sky(p, phase, season, accent, footer=False):
    """An abstract Chengdu skyline, not a geographic map or financial chart."""
    offset = -172 if footer else 0
    mountain = f'<g transform="translate(0 {offset})"><path d="M420 278L485 231L517 249L572 207L621 246L653 226L713 264L761 231L812 261L900 214V300H420Z" fill="{p["soft"]}" opacity=".55"/>'
    city = '<path d="M550 278v-20h14v20h12v-36h15v36h12v-21h9v21h18v-47h10v-14h6v14h10v47h13v-29h17v29h12v-16h20v16h17v-39h14v-11h7v11h14v39h13v-24h18v24h13v-41h18v41h17v-17h21v17h22v-29h17v29h25"'
    mountain += city + f' fill="none" stroke="{p["muted"]}" stroke-width="1" opacity=".3"/></g>'
    if footer:
        return mountain
    night = phase in ('NIGHT', 'DUSK')
    cy = {'DAWN': 77, 'DAY': 58, 'DUSK': 86, 'NIGHT': 60}[phase]
    color = p['warm'] if not night else '#9aaed5'
    sun = f'<circle cx="835" cy="{cy}" r="23" fill="{color}" opacity=".08"/><circle cx="835" cy="{cy}" r="11" fill="{color}" opacity=".8"/>'
    if night:
        sun += f'<circle cx="840" cy="{cy-4}" r="10" fill="{p["bg"]}"/>'
        for x, y in [(569, 63), (736, 80), (790, 44), (877, 118)]:
            sun += f'<circle class="pulse" cx="{x}" cy="{y}" r="1.3" fill="{p["muted"]}"/>'
    else:
        sun += f'<g class="cloud" stroke="{p["muted"]}" opacity=".2" fill="none" stroke-linecap="round"><path d="M675 66h36m-20 6h39M757 112h30"/></g>'
    return mountain + sun + f'<path d="M38 277h124" stroke="{accent}" opacity=".7" stroke-width="2"/>'


def header(now, dark=False):
    p = palette(dark)
    phase, season, accent = environment(now)
    s = f'<rect width="900" height="300" rx="14" fill="{p["bg"]}"/>'
    s += sky(p, phase, season, accent)
    s += txt(38, 42, 'HELILILILI / AI APPLICATION ENGINEERING', 11, p['muted'], mono=True, extra='letter-spacing="1"')
    s += txt(38, 111, '何丽', 46, p['ink'], 650)
    s += txt(38, 151, 'AI 应用开发 · 成都', 22, p['ink'], 500)
    s += txt(38, 180, '多智能体协作 / 数据生成与评估 / 后端工程', 14, p['muted'])
    s += f'<path d="M38 201H477" stroke="{p["line"]}"/>'
    for x, num, label in [(38, '600+', '标注样本'), (197, '113', 'API 端点'), (348, '49', '数据表')]:
        s += txt(x, 234, num, 25, p['ink'], 600, mono=True)
        s += txt(x, 255, label, 12, p['muted'])
    s += txt(570, 35, f'CHENGDU / {phase} / {season}', 10, p['muted'], mono=True)
    # Packets travel through a compact model → data → API topology.
    routes = ['M582 125H655Q675 125 675 145V180H768', 'M582 200H627Q645 200 645 180V125H768', 'M675 145H734Q750 145 750 125H768']
    for route in routes:
        s += f'<path d="{route}" stroke="{p["line"]}" stroke-width="1.5" fill="none"/><path class="flow" d="{route}" stroke="{p["teal"]}" stroke-width="2" fill="none"/>'
    for x, y, label in [(554, 108, 'LLM'), (554, 183, 'DATA'), (768, 108, 'AGENT'), (768, 163, 'API')]:
        s += f'<rect x="{x}" y="{y}" width="70" height="34" rx="6" fill="{p["panel"]}" stroke="{p["line"]}"/>'
        s += txt(x + 35, y + 22, label, 11, p['ink'], 500, True, 'text-anchor="middle"')
    s += f'<circle class="pulse" cx="675" cy="145" r="6" fill="{p["teal"]}"/>'
    s += txt(570, 296-7, 'MODEL → WORKFLOW → DELIVERY', 10, p['muted'], mono=True)
    return svg('何丽 · AI 应用开发', '原创城市与数据流场景，随北京时间和季节更新。指标来自个人项目经历。', 900, 300, s)


PROJECTS = {
    'quantagent': ('01 / MULTI-AGENT SYSTEM', 'QuantAgent', '多智能体量化研究平台', '研究看板 · 多角色分析 · Ollama 本地接入', '4', '分析角色', '技术 / 新闻 / 宏观 / 风控'),
    'pipeline': ('02 / DATA GENERATION', '三条 APP 数据管线', '从场景、对话到画像的三阶段生成', '结构化生成 · 模型对比 · 校验与人工二审', '600+', '标注样本', '场景 → 对话 → 画像'),
    'dietai': ('03 / BACKEND ENGINEERING', 'AIGC-Dietai', 'AI 饮食健康管理后端', '分层架构 · 认证限流 · Alembic 数据迁移', '113', 'API 端点', '49 张数据表 / 8 个定时任务'),
}


def card(name, dark=False):
    p = palette(dark)
    label, title, subtitle, detail, number, unit, foot = PROJECTS[name]
    s = f'<rect x=".5" y=".5" width="899" height="179" rx="12" fill="{p["panel"]}" stroke="{p["line"]}"/>'
    s += f'<rect x="1" y="27" width="3" height="124" rx="1" fill="{p["teal"]}"/>'
    s += txt(28, 32, label, 10, p['muted'], mono=True, extra='letter-spacing="1"')
    s += txt(28, 72, title, 27, p['ink'], 600)
    s += txt(28, 102, subtitle, 16, p['ink'], 500)
    s += txt(28, 143, detail, 13, p['muted'])
    s += f'<path d="M600 28V151" stroke="{p["line"]}"/>'
    s += txt(635, 81, number, 45, p['teal'], 600, True)
    s += txt(635, 109, unit, 14, p['ink'])
    s += txt(635, 144, foot, 12, p['muted'])
    s += txt(854, 33, '↗', 20, p['muted'])
    return svg(title, f'{subtitle}。{detail}。{number} {unit}；{foot}。', 900, 180, s)


def mobile_header(now, dark=False):
    p = palette(dark)
    phase, season, accent = environment(now)
    s = f'<rect width="480" height="300" rx="14" fill="{p["bg"]}"/>'
    s += f'<g transform="translate(-420 0)">{sky(p, phase, season, accent)}</g>'
    s += txt(26, 34, 'HELILILILI / AI ENGINEERING', 12, p['muted'], mono=True)
    s += txt(26, 101, '何丽', 46, p['ink'], 650)
    s += txt(26, 141, 'AI 应用开发 · 成都', 24, p['ink'], 500)
    s += txt(26, 174, '多智能体 / 数据管线 / 后端工程', 17, p['muted'])
    s += f'<path d="M26 196H454" stroke="{p["line"]}"/>'
    for x, number, unit in [(26, '600+', '标注样本'), (184, '113', 'API 端点'), (333, '49', '数据表')]:
        s += txt(x, 236, number, 29, p['ink'], 600, True)
        s += txt(x, 261, unit, 16, p['muted'])
    s += f'<path class="flow" d="M26 283H454" stroke="{p["teal"]}" stroke-width="2"/>'
    return svg('何丽 · AI 应用开发', f'手机布局。CHENGDU / {phase} / {season}', 480, 300, s)


def mobile_card(name, dark=False):
    p = palette(dark)
    label, title, subtitle, detail, number, unit, foot = PROJECTS[name]
    s = f'<rect x=".5" y=".5" width="479" height="239" rx="12" fill="{p["panel"]}" stroke="{p["line"]}"/>'
    s += f'<rect x="1" y="24" width="3" height="192" rx="1" fill="{p["teal"]}"/>'
    s += txt(24, 32, label, 11, p['muted'], mono=True)
    s += txt(24, 75, title, 30, p['ink'], 600)
    s += txt(24, 108, subtitle, 18, p['ink'])
    s += txt(24, 158, number, 37, p['teal'], 600, True)
    s += txt(139, 154, unit, 17, p['ink'])
    s += txt(24, 188, foot, 16, p['muted'])
    s += txt(24, 219, detail, 15, p['muted'])
    return svg(title, f'{subtitle}。{number} {unit}。{detail}', 480, 240, s)


def activity_counts(events, now):
    if events is None:
        return None
    dates = [(now.astimezone(LOCAL).date() - timedelta(days=i)) for i in range(13, -1, -1)]
    counts = dict.fromkeys(dates, 0)
    for e in events:
        try:
            day = stamp(e['created_at']).date()
            if day in counts:
                counts[day] += 1
        except (KeyError, TypeError, ValueError):
            continue
    return list(counts.values())


def footer(now, events, fetched_at, dark=False):
    p = palette(dark)
    phase, season, accent = environment(now)
    s = f'<rect width="900" height="128" rx="12" fill="{p["bg"]}"/>'
    s += sky(p, phase, season, accent, footer=True)
    s += txt(28, 30, 'SMALL STEPS. WORKING SYSTEMS.', 12, p['ink'], 500, True, 'letter-spacing=".5"')
    counts = activity_counts(events, now)
    s += txt(28, 54, 'PUBLIC ACTIVITY / 14-DAY SAMPLE' if counts is not None else 'PUBLIC ACTIVITY / UNAVAILABLE', 9, p['muted'], mono=True)
    for i in range(14):
        amount = counts[i] if counts is not None else 0
        color = p['teal'] if amount else p['line']
        opacity = min(.55 + amount * .12, 1) if amount else .7
        s += f'<rect x="{28 + 20*i}" y="67" width="12" height="12" rx="3" fill="{color}" opacity="{opacity}"/>'
    local = now.astimezone(LOCAL)
    s += txt(28, 105, f'SCENE {local:%Y-%m-%d %H:%M} UTC+8 / {phase} / {season}', 9, p['muted'], mono=True)
    if fetched_at:
        s += txt(500, 30, f'ACTIVITY SNAPSHOT {stamp(fetched_at):%m-%d %H:%M} UTC+8', 9, p['muted'], mono=True)
    return svg('公开活动与城市场景', '信号点是最近 14 天公开活动采样，不是完整贡献统计。场景为最近生成时刻快照。', 900, 128, s)


def safe_repo(name):
    return isinstance(name, str) and re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', name) is not None


def activity_lines(events):
    result, seen = [], set()
    allowed = {'PushEvent': '推送代码', 'PullRequestEvent': '更新 Pull Request', 'ReleaseEvent': '发布版本', 'CreateEvent': '创建开发资源'}
    for e in events:
        kind = e.get('type')
        repo = e.get('repo', {}).get('name', '')
        actor = e.get('actor', {}).get('login', '')
        if kind not in allowed or actor.lower() != USER or not safe_repo(repo):
            continue
        if repo.lower() in (f'{USER}/{USER}', f'{USER}/resume'):
            continue
        try:
            date = stamp(e['created_at']).strftime('%Y-%m-%d')
        except (KeyError, ValueError, TypeError):
            continue
        key = (date, repo, kind)
        if key in seen:
            continue
        seen.add(key)
        payload = e.get('payload', {})
        url = 'https://github.com/' + repo
        action = allowed[kind]
        if kind == 'PullRequestEvent':
            number = payload.get('pull_request', {}).get('number') or payload.get('number')
            if isinstance(number, int) and number > 0:
                url += '/pull/' + str(number)
        elif kind == 'ReleaseEvent':
            action = '发布版本'
            url += '/releases'
        result.append(f'- {date} · {action} · [{repo}]({url})')
        if len(result) == 3:
            break
    return '\n'.join(result) if result else f'[查看 GitHub 公开开发动态](https://github.com/{USER}?tab=overview#activity)'


def replace_activity(readme, content):
    if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(END) < readme.index(START):
        raise ValueError('README activity markers must occur exactly once, in order')
    before, rest = readme.split(START)
    _, after = rest.split(END)
    return before + START + '\n' + content + '\n' + END + after


def fetch_events():
    headers = {'User-Agent': USER + '-profile', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(f'https://api.github.com/users/{USER}/events/public?per_page=100', headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.load(response)
    if not isinstance(data, list) or not all(isinstance(e, dict) for e in data):
        raise ValueError('Invalid public events response')
    return data


def refresh(root=ROOT, now=None, offline=False, loader=fetch_events):
    now = (now or datetime.now(timezone.utc)).astimezone(LOCAL)
    state_path = root / '.github/profile-state.json'
    try:
        state = json.loads(state_path.read_text(encoding='utf-8'))
        if not isinstance(state, dict):
            state = {}
    except (OSError, ValueError):
        state = {}
    events, fetched_at = state.get('events'), state.get('fetched_at')
    success = False
    if not offline:
        try:
            events = loader()
            fetched_at = now.isoformat(timespec='seconds')
            success = True
        except (OSError, ValueError, urllib.error.URLError):
            print('Public activity unavailable; retaining existing snapshot.', file=sys.stderr)
    # Validate README before writing any outputs, so malformed markers cannot cause partial updates.
    readme_path = root / 'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    validated = replace_activity(readme, activity_lines(events or []))
    for dark in (False, True):
        suffix = '-dark' if dark else ''
        write(root / f'assets/header{suffix}.svg', header(now, dark))
        write(root / f'assets/header-mobile{suffix}.svg', mobile_header(now, dark))
        write(root / f'assets/footer{suffix}.svg', footer(now, events, fetched_at, dark))
        for name in PROJECTS:
            write(root / f'assets/{name}{suffix}.svg', card(name, dark))
            write(root / f'assets/{name}-mobile{suffix}.svg', mobile_card(name, dark))
    if success:
        write(state_path, json.dumps({'fetched_at': fetched_at, 'events': events}, ensure_ascii=False, indent=2) + '\n')
        write(readme_path, validated)
    return {'fresh': success, 'has_snapshot': events is not None, 'scene': now.isoformat(timespec='seconds')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='Only regenerate SVGs using the existing snapshot')
    args = parser.parse_args()
    print(json.dumps(refresh(offline=args.offline)))
