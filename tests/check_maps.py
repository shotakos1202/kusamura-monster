import asyncio,os,pathlib
from playwright.async_api import async_playwright
URL=pathlib.Path(__file__).resolve().parent.parent.joinpath('dist','test.html').as_uri()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(URL);await pg.wait_for_function('window.__t',timeout=20000)
        print(await pg.evaluate("""()=>{const{MAPS,WALK}=__t;const out=[];
 for(const id in MAPS){const m=MAPS[id];const at=(x,y)=>(x<0||y<0||x>=m.w||y>=m.h)?'#':m.rows[y][x];
  const block=new Set(m.npcs.filter(e=>!e.hideFlag).map(e=>e.x+','+e.y));
  const ok=(x,y)=>WALK.has(at(x,y))&&!block.has(x+','+y);
  const arr=[];for(const o in MAPS)for(const k in (MAPS[o].warps||{})){const w=MAPS[o].warps[k];if(w[0]===id)arr.push([w[1],w[2]])}
  if(!arr.length){out.push(id+' no arrivals');continue}
  const s0=arr[0];const seen=new Set([s0+'']);const st=[s0];
  while(st.length){const[x,y]=st.pop();{const w=(m.warps||{})[x+','+y];if(w&&w[0]===id&&!seen.has(w[1]+','+w[2])){seen.add(w[1]+','+w[2]);st.push([w[1],w[2]])}}for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]]){const nx=x+dx,ny=y+dy;if(ok(nx,ny)&&!seen.has(nx+','+ny)){seen.add(nx+','+ny);st.push([nx,ny])}}}
  const adj=(x,y)=>[[1,0],[-1,0],[0,1],[0,-1]].some(([dx,dy])=>seen.has((x+dx)+','+(y+dy)));
  const p=[];
  for(const a of arr)if(!seen.has(a+''))p.push('arrival '+a);
  for(const k in m.warps||{}){const[x,y]=k.split(',').map(Number);if(!seen.has(k)&&!adj(x,y))p.push('warp '+k)}
  for(const e of m.npcs)if(!e.hideFlag&&!adj(e.x,e.y)&&!adj(e.x,e.y+1))p.push('npc '+e.x+','+e.y);
  for(const k in m.signs||{}){const[x,y]=k.split(',').map(Number);if(m.rows[y][x]!=='S')p.push('signtile '+k);if(!adj(x,y))p.push('sign '+k)}
  for(const it of m.items||[])if(!seen.has(it.x+','+it.y)&&!adj(it.x,it.y))p.push('item '+it.id);
  for(const e of m.npcs)if(!WALK.has(at(e.x,e.y))&&at(e.x,e.y)!=='f'&&at(e.x,e.y)!=='c')p.push('npc-on-'+at(e.x,e.y)+' '+e.x+','+e.y);
  const strs=[];const walk=v=>{if(typeof v==='string')strs.push(v);else if(v&&typeof v==='object')for(const k in v)walk(v[k])};walk([m.npcs.map(e=>[e.text,e.say,e.lose,e.after,e.badgeTalk]),m.signs,m.locked]);if(strs.some(x=>x.includes(String.fromCharCode(92))||x.includes(String.fromCharCode(0xfffd))))p.push('BADTEXT');
  if(p.length)out.push(id+': '+p.join(' | '))}
 return out.join('\\n')||'all OK'}"""))
        print(errs);await b.close()
asyncio.run(main())
