#!/usr/bin/env python3
"""Report where Claude Code tokens went, from the transcripts under ~/.claude/projects.

A turn's units = input + 1.25*cache_write_5m + 2*cache_write_1h + 0.1*cache_read + 5*output,
times a per-model weight. Standard library only.
"""
import argparse, collections as C, csv, glob, json, os, re, statistics as S
from datetime import datetime, timedelta, timezone

ROOT = os.path.expanduser('~/.claude/projects')
HOME = re.sub(r'[^A-Za-z0-9]', '-', os.path.expanduser('~'))  # how Claude Code encodes a dir name
IMAGE_CHARS = 6000  # rough char-equivalent of one image block (~1.5k tokens)
IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
TS = re.compile(r'"timestamp":\s*"([^"]+)"')
COMPONENTS = ('input', 'cache write', 'cache read', 'output')

def utc(s):
    d = datetime.fromisoformat(s.strip().replace('Z', '+00:00'))
    return d.astimezone(timezone.utc) if d.tzinfo else d.replace(tzinfo=timezone.utc)

def key(d):
    return d.strftime('%Y-%m-%dT%H:%M:%S')

def args():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--since', help='start, YYYY-MM-DD or ISO (UTC); default 7 days ago')
    ap.add_argument('--until', help='end, ISO (UTC); default now')
    ap.add_argument('--project', action='append', default=[], help='substring of the project dir name; repeatable, OR')
    ap.add_argument('--cut', action='append', default=[], help='split the window into periods here; repeatable')
    ap.add_argument('--weights', default='', help='model weights, e.g. fable=7,sonnet=0.6,haiku=0.2')
    ap.add_argument('--ctx', type=int, default=200000, help='context threshold in tokens')
    ap.add_argument('--top', type=int, default=10, help='main sessions to list')
    ap.add_argument('--prs', help='file of merged-PR timestamps, one per line')
    ap.add_argument('--csv', help='directory to write agents.csv into')
    return ap.parse_args()

A = args()
NOW = datetime.now(timezone.utc)
SINCE = utc(A.since) if A.since else NOW - timedelta(days=7)
UNTIL = utc(A.until) if A.until else NOW
W = {'fable': 7.0, 'sonnet': 0.6, 'haiku': 0.2}
for kv in filter(None, A.weights.split(',')):
    k, v = kv.split('=')
    W[k.strip()] = float(v)
CUTS = sorted(c for c in map(utc, A.cut) if SINCE < c < UNTIL)
BOUNDS = [SINCE] + CUTS + [UNTIL]
PERIODS = [(key(s), key(e), (e - s).total_seconds() / 86400) for s, e in zip(BOUNDS, BOUNDS[1:])]
S_KEY, U_KEY = key(SINCE), key(UNTIL)

def family(model):
    return next((k for k in W if k in model), 'opus' if 'opus' in model else model)

def weigh(u, model):
    def g(k):
        return u.get(k) or 0
    cc = u.get('cache_creation') or {}
    if cc:
        c5, c1 = cc.get('ephemeral_5m_input_tokens') or 0, cc.get('ephemeral_1h_input_tokens') or 0
    else:
        c5, c1 = g('cache_creation_input_tokens'), 0
    m = W.get(family(model), 1.0)
    ctx = g('input_tokens') + g('cache_read_input_tokens') + g('cache_creation_input_tokens')
    comps = (m * g('input_tokens'), m * (1.25 * c5 + 2 * c1), m * 0.1 * g('cache_read_input_tokens'), m * 5 * g('output_tokens'))
    return ctx, comps

def tool_name(b):
    name, inp = b.get('name') or '?', b.get('input') or {}
    if name == 'Bash':
        words = str(inp.get('command', '')).split()
        while words and (re.match(r'[A-Za-z_]\w*=', words[0]) or (words[0] == 'cd' and len(words) > 2)):
            if words[0] != 'cd':
                words = words[1:]
            elif words[1].endswith(';'):
                words = words[2:]
            elif words[2] in ('&&', ';'):
                words = words[3:]
            else:
                break
        return 'Bash:' + (words[0] if words else '')
    if name == 'Read' and str(inp.get('file_path', '')).lower().endswith(IMAGE_EXT):
        return 'image'
    return name

def result_size(name, content):
    if isinstance(content, str):
        return name, len(content), 1
    size = imgs = 0
    for x in content if isinstance(content, list) else []:
        if isinstance(x, dict) and x.get('type') == 'text':
            size += len(x.get('text') or '')
        elif isinstance(x, dict) and x.get('type') == 'image':
            imgs += 1
    if imgs or name == 'image':
        return 'image', size + IMAGE_CHARS * imgs, max(imgs, 1)
    return name, size, 1

def discover():
    files = []
    for p in sorted(os.listdir(ROOT)):
        d = os.path.join(ROOT, p)
        if not os.path.isdir(d) or (A.project and not any(s in p for s in A.project)):
            continue
        # Subagent files first, so a response logged in both places is credited to the subagent.
        files += [(p, f, True) for f in glob.glob(os.path.join(d, '*', 'subagents', '**', 'agent-*.jsonl'), recursive=True)]
        files += [(p, f, False) for f in glob.glob(os.path.join(d, '*.jsonl'))]
    return [x for x in files if os.path.getmtime(x[1]) >= SINCE.timestamp()]

def scan(proj, path, is_sub, seen):
    if is_sub:
        try:
            with open(path[:-6] + '.meta.json') as fh:
                at = json.load(fh).get('agentType') or '?'
        except (OSError, ValueError):
            at = '?'
        sid = os.path.basename(path.split(os.sep + 'subagents' + os.sep)[0])
    else:
        at, sid = 'main', os.path.basename(path)[:-6]
    turns, uses, chars, count = [], {}, C.Counter(), C.Counter()
    with open(path, errors='ignore') as fh:
        for line in fh:
            if '"usage"' not in line and '"tool_result"' not in line:
                continue
            m = TS.search(line)
            ts = m.group(1)[:19] if m else ''
            if not (S_KEY <= ts < U_KEY):
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            msg = d.get('message') or {}
            if d.get('type') == 'assistant':
                for b in msg.get('content') or []:
                    if isinstance(b, dict) and b.get('type') == 'tool_use':
                        uses[b.get('id')] = tool_name(b)
                u, model, k = msg.get('usage'), msg.get('model'), (msg.get('id'), d.get('requestId'))
                if not u or model in (None, '<synthetic>') or k in seen:
                    continue
                if k != (None, None):
                    seen.add(k)
                turns.append((ts, model) + weigh(u, model))
            elif d.get('type') == 'user' and isinstance(msg.get('content'), list):
                for b in msg['content']:
                    if isinstance(b, dict) and b.get('type') == 'tool_result':
                        name, size, n = result_size(uses.get(b.get('tool_use_id'), '?'), b.get('content'))
                        chars[name] += size
                        count[name] += n
    if not turns and not chars:
        return None
    units = [sum(t[3]) for t in turns]
    ctxs = [t[2] for t in turns]
    return dict(proj=proj, sid=sid, at=at, turns=turns, chars=chars, count=count,
                n=len(turns), units=sum(units), peak=max(ctxs, default=0), start=ctxs[0] if ctxs else 0,
                past=sum(u for u, c in zip(units, ctxs) if c > A.ctx),
                first=turns[0][0] if turns else '',
                model=C.Counter(t[1] for t in turns).most_common(1)[0][0] if turns else '')

def period_of(ts):
    return next((i for i, (s, e, _) in enumerate(PERIODS) if s <= ts < e), None)

def fmt(x):
    return f'{x / 1e6:.1f}M' if abs(x) >= 1e6 else f'{x / 1e3:.0f}k'

def pct(a, b):
    return f'{a / b:.0%}' if b else '-'

def short(p, width=28):
    s = p[len(HOME):].lstrip('-') if p.startswith(HOME) else p.lstrip('-')
    return (s[-width:] if width else s) or '-'

def report(files, agents):
    days = (UNTIL - SINCE).total_seconds() / 86400
    nturns = sum(a['n'] for a in agents)
    print(f'Window {S_KEY} -> {U_KEY} UTC ({days:.1f} days)')
    print('Weights: units = input + 1.25*cache5m + 2*cache1h + 0.1*cache_read + 5*output; model x '
          + ', '.join(f'{k}={v:g}' for k, v in W.items()) + ', other=1')
    print(f'{len(files)} files scanned, {len(agents)} agents with activity, {nturns} turns, ctx threshold {fmt(A.ctx)}')
    prs = []
    if A.prs:
        with open(A.prs) as fh:
            prs = [key(utc(line.split()[0])) for line in fh if line.strip()]

    for i, (s, e, d) in enumerate(PERIODS):
        tot, by, comp = 0.0, C.Counter(), [0.0] * 4
        for a in agents:
            role = 'main' if a['at'] == 'main' else 'sub:' + a['at']
            for ts, model, _, cs in a['turns']:
                if s <= ts < e:
                    u = sum(cs)
                    tot += u
                    by[f'{family(model)} {role}'] += u
                    comp = [x + y for x, y in zip(comp, cs)]
        npr = sum(s <= t < e for t in prs)
        print(f'\n== Period {i + 1}: {s} -> {e} ({d:.1f} days)')
        line = f'units {fmt(tot)}  per day {fmt(tot / d if d else 0)}'
        if A.prs:
            line += f'  PRs {npr}  per PR {fmt(tot / npr) if npr else "-"}'
        print(line)
        print(f'  {"model x role":36s}{"share":>7}{"per day":>10}')
        for k, v in by.most_common(10):
            print(f'  {k[:36]:36s}{pct(v, tot):>7}{fmt(v / d if d else 0):>10}')
        print('  components: ' + '  '.join(f'{n} {pct(c, tot)}' for n, c in zip(COMPONENTS, comp)))
        subagent_table([a for a in agents if a['at'] != 'main' and a['turns'] and period_of(a['first']) == i])

    mains = sorted((a for a in agents if a['at'] == 'main' and a['turns']), key=lambda a: -a['units'])
    subs = C.Counter()
    for a in agents:
        if a['at'] != 'main':
            subs[(a['proj'], a['sid'])] += a['units']
    print(f'\n== Top {A.top} main sessions (whole window)')
    print(f'{"project":28s} {"session":8s}{"turns":>7}{"peak":>7}{"units":>8}{"past":>6}{"subagents":>10}')
    for a in mains[:A.top]:
        print(f'{short(a["proj"]):28s} {a["sid"][:8]:8s}{a["n"]:7d}{fmt(a["peak"]):>7}{fmt(a["units"]):>8}'
              f'{pct(a["past"], a["units"]):>6}{fmt(subs[(a["proj"], a["sid"])]):>10}')

    for label, group in (('main', [a for a in agents if a['at'] == 'main']), ('subagents', [a for a in agents if a['at'] != 'main'])):
        chars, count = C.Counter(), C.Counter()
        for a in group:
            chars.update(a['chars'])
            count.update(a['count'])
        total = sum(chars.values())
        print(f'\n== Tool results, {label} (whole window): {fmt(total)} chars')
        print(f'  {"tool":28s}{"chars":>8}{"share":>7}{"count":>8}{"mean":>8}')
        for k, v in chars.most_common(12):
            print(f'  {k[:28]:28s}{fmt(v):>8}{pct(v, total):>7}{count[k]:8d}{fmt(v / count[k]):>8}')

def subagent_table(rows):
    if not rows:
        print('  no subagents started in this period')
        return
    print(f'  {"subagents":20s}{"n":>5}{"medT":>6}{"p90T":>6}{"crossed":>8}{"past":>6}{"medPeak":>8}{"mean":>7}{"medStart":>9}{"grow/T":>8}')
    types = C.Counter(a['at'] for a in rows)
    for t in ['ALL'] + [t for t, n in types.most_common() if n >= 3]:
        r = [a for a in rows if t == 'ALL' or a['at'] == t]
        tl = sorted(a['n'] for a in r)
        units = sum(a['units'] for a in r)
        grow = [(a['peak'] - a['start']) / (a['n'] - 1) for a in r if a['n'] > 1]
        print(f'  {t[:20]:20s}{len(r):5d}{S.median(tl):6.0f}{tl[int(0.9 * len(tl))]:6d}'
              f'{pct(sum(a["peak"] > A.ctx for a in r), len(r)):>8}{pct(sum(a["past"] for a in r), units):>6}'
              f'{fmt(S.median(a["peak"] for a in r)):>8}{fmt(units / len(r)):>7}'
              f'{fmt(S.median(a["start"] for a in r)):>9}{fmt(S.median(grow)) if grow else "-":>8}')

def write_csv(agents):
    os.makedirs(A.csv, exist_ok=True)
    path = os.path.join(A.csv, 'agents.csv')
    with open(path, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['project', 'session', 'agent_type', 'model', 'first_ts', 'turns', 'start_ctx', 'peak_ctx', 'units', 'units_past_ctx'])
        for a in agents:
            if a['turns']:
                w.writerow([short(a['proj'], None), a['sid'], a['at'], a['model'], a['first'], a['n'], a['start'], a['peak'],
                            round(a['units']), round(a['past'])])
    print(f'\nwrote {path}')

def main():
    files, seen = discover(), set()
    agents = [a for a in (scan(p, f, sub, seen) for p, f, sub in files) if a]
    report(files, agents)
    if A.csv:
        write_csv(agents)

main()
