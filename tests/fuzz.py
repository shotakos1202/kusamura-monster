import asyncio,os,pathlib
from playwright.async_api import async_playwright
URL=pathlib.Path(__file__).resolve().parent.parent.joinpath('dist','test.html').as_uri()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto(URL);await pg.wait_for_function('window.__t',timeout=20000)
        for seed,start in [(1,"'route',10,18"),(2,"'forest',12,30"),(3,"'route3',10,18"),(4,"'town2',10,16"),(5,"'coast',2,4"),(6,"'route4',10,23"),(7,"'hill',2,7"),(8,"'gym3',5,12")]:
          r=await pg.evaluate("""([seed,start])=>{window.requestAnimationFrame=()=>0;const t=__t;let s=seed;const r=()=>{s=(s*1103515245+12345)%2147483648;return s/2147483648};
           const step=()=>{t.update();t.draw();for(const x in t.pressed)t.pressed[x]=false};
           if(t.mode==='title'){t.pressed.a=true;step();t.pressed.a=true;step()}
           t.Q.length=0;t.menu=null;t.S.party=[t.mon('tsubomiru',20),t.mon('raidenga',19),t.mon('namitama',18)];t.S.badges=['ゴツゴツバッジ','アクアバッジ'];t.loadMap(...eval('['+start+']'),'up');
           let dir='up',stuck=0,last=null,maps=new Set(),battles=0,wasB=false;
           for(let f=0;f<15000;f++){if(f%16===0){t.setKey(dir,false);dir=['up','up','left','right','down'][r()*5|0];t.setKey(dir,true)}
             if(t.Q.length||t.mode!=='world'){if(f%3===0)t.pressed[r()<.85?'a':['b','up','down','left','right'][r()*5|0]]=true}else if(r()<.03)t.pressed.a=true;
             step();maps.add(t.S.map);if(t.mode==='battle'&&!wasB)battles++;wasB=t.mode==='battle';
             const q=t.Q[0];if(q&&q===last&&q.w)stuck++;else stuck=0;last=q;if(stuck>2500)return 'STUCK '+String(q.w);
             if(f%3000===0)t.S.party.forEach(m=>m.hp=m.mhp)}
           return 'ok '+[...maps]+' battles '+battles+' badges '+t.S.badges+' visited '+Object.keys(t.S.visited)}""",[seed,start])
          print(r)
        print(errs[:3]);await b.close()
asyncio.run(main())
