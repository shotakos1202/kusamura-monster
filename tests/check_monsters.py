"""モンスターの データの むじゅんを しらべる（AGENTS.md の「モンスター」の ルール）。

python3 tools/build.py && python3 tests/check_monsters.py
- 野生・トレーナーの しんか前は しんかLv より したの レベルだけ
- しんか後は しんかLv いじょうの レベルだけ（野生・トレーナー）
- しんか後の あたらしい わざは しんかLv いじょう
- わざ・しんか先 が そんざい する／ずかん（DEX）・入手（WHERE）に もれが ない
- 野生で でる しんか前は、つかまえて から しんか までに わざを 1つ いじょう おぼえる
"""
import asyncio,pathlib,sys
from playwright.async_api import async_playwright
URL=pathlib.Path(__file__).resolve().parent.parent.joinpath('dist','test.html').as_uri()
JS=r"""()=>{const{MAPS,SP,MV,DEX,WHERE}=__t;const P=[],W=[];
 const pre={};for(const id in SP){const e=SP[id].evo;if(e)pre[e.to]=[id,e.lv]}
 for(const id in SP){const s=SP[id];
  if(!DEX.includes(id))P.push(`${id}: ずかん（DEX）に ない`);
  if(!WHERE[id])P.push(`${id}: 入手（WHERE）が ない`);
  for(const m of s.moves)if(!MV[m])P.push(`${id}: はじめの わざ ${m} が ない`);
  for(const lv in s.learn)if(!MV[s.learn[lv]])P.push(`${id}: Lv${lv}の わざ ${s.learn[lv]} が ない`);
  if(s.evo&&!SP[s.evo.to])P.push(`${id}: しんか先 ${s.evo.to} が ない`);
  if(pre[id]){const[b,elv]=pre[id],bl=SP[b].learn;for(const lv in s.learn)if(+lv<elv&&bl[lv]!==s.learn[lv])P.push(`${id}: しんか前に ない わざ ${MV[s.learn[lv]].n}を Lv${lv}（しんかLv${elv}より まえ）で おぼえる`)}}
 const chk=(where,id,lo,hi)=>{const s=SP[id];if(!s){P.push(`${where}: ${id} が いない`);return}
  if(s.evo&&hi>=s.evo.lv)P.push(`${where}: ${s.name} Lv${lo}-${hi} は しんかLv${s.evo.lv} いじょう（しんか後を だす）`);
  if(pre[id]&&lo<pre[id][1])P.push(`${where}: ${s.name} Lv${lo}-${hi} は しんかLv${pre[id][1]} より した`)};
 const wildMin={};
 for(const mid in MAPS){const m=MAPS[mid];
  for(const k of['wild','wildW']){const f=m[k];if(!f)continue;const seen={};
   for(let y=0;y<m.h;y++)for(let x=0;x<m.w;x++){let L;try{L=f(x,y)}catch(e){continue}if(!L)continue;
    for(const[id,lo,hi]of L){const key=id+lo+'-'+hi;if(seen[key])continue;seen[key]=1;chk(`${m.name||mid}（${k==='wild'?'やせい':'なみのり'}）`,id,lo,hi);wildMin[id]=Math.min(wildMin[id]??99,lo)}}}
  for(const e of m.npcs||[])if(e.team)for(const[id,lv]of e.team)chk(`${m.name||mid} ${e.tname||e.id}`,id,lv,lv)}
 for(const id in wildMin){const s=SP[id];if(!s.evo)continue;const lo=wildMin[id];
  if(!Object.keys(s.learn).some(lv=>+lv>lo&&+lv<s.evo.lv))W.push(`${s.name}: つかまえて（Lv${lo}〜）から しんか（Lv${s.evo.lv}）まで に おぼえる わざが ない`)}
 return{P,W}}"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page()
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(URL);await pg.wait_for_function('window.__t',timeout=20000)
        r=await pg.evaluate(JS);await b.close()
    for w in r['W']:print('ちゅうい:',w)
    for x in r['P']:print('NG:',x)
    if errs:print('pageerror:',errs)
    print('all OK' if not r['P'] and not errs else f"NG {len(r['P'])}けん")
    sys.exit(1 if r['P'] or errs else 0)
asyncio.run(main())
