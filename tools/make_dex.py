"""モンスターずかん（かいはつよう）を ゲームの データから じどうで つくる。

python3 tools/make_dex.py   （tools/build.py の あとに じどうで よばれる）
- dev/dex.html     … ずかんページ（GitHub Pages: https://shotakos1202.github.io/kusamura-monster/dev/dex.html）
- dev/monsters.md  … モンスター いちらんと しょうさい（Markdown）
- dist/dex_artifact.html … claude.ai の アーティファクトよう（doctype なし）
dist/test.html を ブラウザ（Playwright）で ひらき、SP・DEX・MV・MAPS を よみだして つくる。
データが かわらなければ ファイルは かきかえない（むだな コミットを ださない）。
"""
import asyncio, collections, json, os, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INJ = "window.__x={MV,TN,TCOL,WHERE,LATE_LEARN,DEX,SP,ART,MAPS,LEGEND};window.__t={"
EXTRACT = r"""()=>{const{MV,TN,TCOL,WHERE,LATE_LEARN,DEX,SP,ART,MAPS,LEGEND}=__x;const out={DEX,TN,TCOL,WHERE,LEGEND,LATE:LATE_LEARN,MV:{},SP:{},maps:{}};
 for(const k in MV)out.MV[k]={n:MV[k].n,t:MV[k].t,p:MV[k].p||0,d:MV[k].d||''};
 for(const k in SP){const s=SP[k];out.SP[k]={name:s.name,type:s.type,type2:s.type2||null,b:s.b,exp:s.exp,cr:s.cr,grow:s.grow||1,moves:s.moves,learn:s.learn,evo:s.evo||null,desc:s.desc||''};
  try{out.SP[k].img=ART[k]?ART[k].img.toDataURL():null}catch(e){out.SP[k].img=null}}
 for(const id in MAPS){const m=MAPS[id];const samp=f=>{if(!f)return null;const acc={};for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){let L;try{L=f(x,y)}catch(e){continue}if(!L)continue;
   const tot=L.reduce((a,e)=>a+(e[3]||10),0);for(const[mid,lo,hi,w]of L){const r=Math.round((w||10)/tot*100);const a=acc[mid]||(acc[mid]={lo:99,hi:0,rmin:999,rmax:0});a.lo=Math.min(a.lo,lo);a.hi=Math.max(a.hi,hi);a.rmin=Math.min(a.rmin,r);a.rmax=Math.max(a.rmax,r)}}return acc};
  const tr=[];for(const e of m.npcs||[]){let team=null;try{team=e.team}catch(err){}if(team&&team.length)tr.push({n:e.tname||e.id||'',team})}
  out.maps[id]={name:m.name||'',wild:samp(m.wild),wildW:samp(m.wildW),npcs:tr}}
 return out}"""


async def extract():
    from playwright.async_api import async_playwright
    page = (ROOT / 'dist' / 'test.html').read_text(encoding='utf-8').replace('window.__t={', INJ, 1)
    tmp = ROOT / 'dist' / 'dex_extract.html'
    tmp.write_text(page, encoding='utf-8')
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await b.new_page()
            # ずかんの データだけ ほしいので そとの フォントは よまない
            await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
            await pg.goto(tmp.as_uri())
            await pg.wait_for_function('window.__t', timeout=30000)
            d = await pg.evaluate(EXTRACT)
            await b.close()
    finally:
        tmp.unlink(missing_ok=True)
    return d


def build_rows(d):
    SP, DEX, MV, TN, W = d['SP'], d['DEX'], d['MV'], d['TN'], d['WHERE']
    AN = {k: (m['name'] or k) for k, m in d['maps'].items()}
    pre = {}
    for k in SP:
        e = SP[k].get('evo')
        if e:
            pre[e['to']] = (k, e['lv'])
    wild = collections.defaultdict(list)
    tr = collections.defaultdict(list)
    for mid, m in d['maps'].items():
        for kind in ('wild', 'wildW'):
            for mon, a in (m[kind] or {}).items():
                r = f"{a['rmin']}%" if a['rmin'] == a['rmax'] else f"{a['rmin']}–{a['rmax']}%"
                wild[mon].append(dict(map=mid, area=AN[mid], water=kind == 'wildW', lo=a['lo'], hi=a['hi'], rate=r))
        for t in m['npcs']:
            for mon, lv in t['team']:
                tr[mon].append(dict(map=mid, area=AN[mid], t=t['n'], lv=lv))

    def chain(k):
        r = k
        while r in pre:
            r = pre[r][0]
        out = [r]
        while SP[out[-1]].get('evo'):
            out.append(SP[out[-1]]['evo']['to'])
        return out

    def learn(k):
        L = dict(SP[k]['learn'] or {})
        for lv, mv in (d['LATE'].get(k) or {}).items():
            L[lv] = mv
        return sorted((int(a), b) for a, b in L.items())

    tn = lambda t: TN.get(t, t)
    rows = []
    for i, k in enumerate(DEX, 1):
        s = SP[k]
        b = s['b']
        ch = chain(k)
        rows.append(dict(
            no=i, id=k, name=s['name'], type=s['type'], type2=s.get('type2'),
            tn=tn(s['type']) + ('・' + tn(s['type2']) if s.get('type2') else ''),
            b=b, bst=sum(b.values()), exp=s['exp'], cr=s['cr'], grow=s.get('grow', 1),
            evo=s.get('evo'), pre=pre.get(k), chain=ch, stage=ch.index(k) + 1, stages=len(ch),
            where=W.get(k, ''), desc=s['desc'], legend=k in (d.get('LEGEND') or []),
            moves=[MV[m]['n'] for m in s['moves'] if m in MV],
            learn=[(lv, MV[m]['n'], tn(MV[m]['t']), MV[m]['p']) for lv, m in learn(k) if m in MV],
            wild=sorted(wild[k], key=lambda w: w['lo']), tr=tr[k], img=s['img']))
    return rows


def notes(rows, TN):
    cnt = collections.Counter()
    for r in rows:
        cnt[r['type']] += 1
        if r['type2']:
            cnt[r['type2']] += 1
    out = ['タイプ べつ（ダブルタイプは りょうほうで かぞえる）：' + '・'.join(f"{TN[t]} {n}" for t, n in cnt.most_common())]
    dual = [r['name'] for r in rows if r['type2']]
    if dual:
        out.append('ダブルタイプ：' + '・'.join(dual))
    nowild = [r for r in rows if not r['wild'] and not r['legend'] and not r['pre']]
    tronly = [r['name'] for r in rows if not r['wild'] and r['tr'] and not r['legend']]
    if tronly:
        out.append('やせいに でない（トレーナーの てもち だけ）：' + '・'.join(tronly))
    unseen = [r['name'] for r in rows if not r['wild'] and not r['tr'] and not r['legend'] and r['pre']]
    if unseen:
        out.append('やせいにも トレーナーにも でない しんかけい：' + '・'.join(unseen))
    few = [r['name'] for r in rows if len(r['learn']) <= 3 and not r['legend']]
    if few:
        out.append('おぼえる わざが 3つ いか：' + '・'.join(few))
    single = [r['name'] for r in rows if r['stages'] == 1 and not r['legend']]
    if single:
        out.append('しんか しない（でんせつ・まぼろし いがい）：' + '・'.join(single))
    out.append('ルール（しんかLv・わざLv・でんせつの じゅんばん など）は AGENTS.md の「モンスター」を みてね')
    return out


def markdown(rows, TN, nl):
    N = {r['id']: r['name'] for r in rows}
    o = ['# くさむらモンスター モンスター一覧と詳細', '',
         '`tools/make_dex.py` が ゲームの データから じどうで つくる ファイル（てで かきかえない）。`python3 tools/build.py` の たびに さいしんに なる。', '',
         f"ぜんぶで **{len(rows)}ひき**（ずかん `DEX` の じゅん）。", '', '## きづいた こと', '']
    o += ['- ' + x for x in nl]
    o += ['', '## はやみひょう', '', '| No | なまえ | ID | タイプ | HP | こう | ぼう | すば | 合計 | しんか | 入手 |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        b = r['b']
        ev = f"Lv{r['evo']['lv']}→{N.get(r['evo']['to'], r['evo']['to'])}" if r['evo'] else '—'
        o.append(f"| {r['no']} | {r['name']} | {r['id']} | {r['tn']} | {b['hp']} | {b['atk']} | {b['def']} | {b['spd']} | {r['bst']} | {ev} | {r['where']} |")
    o += ['', '## しんかの ながれ', '']
    seen = set()
    for r in rows:
        c = tuple(r['chain'])
        if c in seen:
            continue
        seen.add(c)
        parts = [N[c[0]]]
        for x in c[1:]:
            pr = next(rr for rr in rows if rr['id'] == x)['pre']
            parts.append(f"（Lv{pr[1]}）→ {N[x]}")
        o.append('- ' + ' '.join(parts))
    o += ['', '## モンスター しょうさい', '']
    for r in rows:
        b = r['b']
        o.append(f"### {r['no']}. {r['name']}（{r['id']}）")
        o.append(f"- タイプ：{r['tn']}／HP {b['hp']}・こうげき {b['atk']}・ぼうぎょ {b['def']}・すばやさ {b['spd']}（合計 {r['bst']}）")
        o.append(f"- けいけんち {r['exp']}・つかまえやすさ {r['cr']}" + (f"・せいちょう ×{r['grow']}" if r['grow'] != 1 else ''))
        o.append(f"- せつめい：{r['desc']}")
        o.append(f"- 入手：{r['where'] or '—'}")
        if r['wild']:
            o.append('- 野生：' + '、'.join(f"{w['area']}{'（なみのり）' if w['water'] else ''} Lv{w['lo']}-{w['hi']}（{w['rate']}）" for w in r['wild']))
        if r['tr']:
            o.append('- トレーナー：' + '、'.join(f"{t['t']} {t['lv']}" for t in r['tr']))
        o.append('- はじめの わざ：' + '、'.join(r['moves']))
        if r['learn']:
            o.append('- おぼえる わざ：' + '、'.join(f"Lv{lv} {n}" for lv, n, _, _ in r['learn']))
        o.append('')
    return '\n'.join(o)


DOC_HEAD = ('<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="robots" content="noindex">\n</head>\n<body>\n')


def write_if_changed(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding='utf-8') == text:
        return False
    path.write_text(text, encoding='utf-8')
    return True


def main():
    if not (ROOT / 'dist' / 'test.html').exists():
        print('dist/test.html が ない。さきに python3 tools/build.py を じっこうしてね'); sys.exit(1)
    d = asyncio.run(extract())
    rows = build_rows(d)
    nl = notes(rows, d['TN'])
    data = json.dumps(dict(rows=rows, tcol=d['TCOL'], tn=d['TN']), ensure_ascii=False)
    tpl = (ROOT / 'tools' / 'dex_template.html').read_text(encoding='utf-8')
    body = tpl.replace('__DATA__', data).replace('__NOTES__', '\n'.join(f'   <li>{x}</li>' for x in nl))
    ch = []
    if write_if_changed(ROOT / 'dev' / 'dex.html', DOC_HEAD + body + '\n</body>\n</html>\n'):
        ch.append('dev/dex.html')
    if write_if_changed(ROOT / 'dev' / 'monsters.md', markdown(rows, d['TN'], nl) + '\n'):
        ch.append('dev/monsters.md')
    write_if_changed(ROOT / 'dist' / 'dex_artifact.html', body)
    print(f"ずかん：{len(rows)}ひき " + ('こうしん → ' + '・'.join(ch) if ch else 'へんこう なし'))


if __name__ == '__main__':
    main()
