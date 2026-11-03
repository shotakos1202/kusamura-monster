"""ストーリーを さいごまで あそべるかを ボットで しらべる（エンディングまでの つうしテスト）。

python3 tools/build.py && python3 tests/playthrough.py
- かいはつしゃモードの シナリオ（SCN）から はじめ、ボットが じっさいに あるいて はなしかけ、
  でぐち・アイテムを ためし、バトルは つよい てもち（Lv100）で すすめる
- 章ごとに「たつ はずの フラグ」が たつかを しらべる（たたなければ NG）
- オオアミジム（スイッチの しかけ）は ボットが とけないので、けいかくした みちじゅんで あそぶ
- マウントフジは マップの「さざなみで とぶ」を つかう
- 1章 ずつ 数十びょう〜数ふん かかる。マップ・イベント・バトルを かえたときに じっこうする
"""
import asyncio,pathlib,json,sys,time
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parent.parent
BOT=(ROOT/'tests'/'bot.js').read_text(encoding='utf-8')
INJ="window.__x={S:()=>S,CUR:()=>CUR,P:()=>P,at,canHero,entityAt,hid,fade:()=>fade,boxui:()=>boxui,SCN,devBase,setDEV:v=>{DEV=v},MV,SP,mon};window.__t={"
# [シナリオ名, たつ はずの フラグ, フレーム上限, まえしょり(JS), むかう マップの じゅん（そこで まわりを しらべてから つぎへ）]
CHAPTERS=[
 ['さいしょから',['starter','iwao','tatsu1','uppy','shizuku'],200000,'',['nbr','village','route','town','gym','forest','route3','town2','gym2']],
 ['ミライジム',['satori'],80000,''],
 ['キヨシ イベントの まえ',['kiyoshi','ev5done'],100000,'',['route5','village']],
 ['ユノハマシティ',['ygruntGone','hibana','ev6done','tatsu2'],100000,''],
 ['イシモリの まえ',['ishimoriGone','it_cmap','caveOpen'],60000,''],
 ['タカネジム',['fuuka','r7done','kiyoTGone','towerDone','oamiWake'],150000,''],
 ['ぼうそうジム（マツナガ）',['matsunaga','matsunagaTold'],60000,''],
 ['ミライポート フェリー（タツヤ）',['tatsu3'],40000,''],
 ['カモガワジム（わかしお）',['wakashio','oosugiR','sazanamiGot','ruinsDone'],60000,''],
 ['マウントフジ（さざなみ あり）',['teruiF','kiyoF','fatherF','gameClear'],80000,
  "run(30);t.Q.length=0;run(5);t.menu={pg:'wmap',w:t.WMAP.findIndex(w=>w.id==='fuji'),i:0,j:0,k:0};t.pressed.a=true;run(1);"],
 # クリアご（FEAT.postgame・かいはつしゃモードで テスト）：うけつけ → 4にん → けっしょう タツヤ
 ['チャンピオンスタジアム（リーグ）',['champion'],150000,"X.S().party=['hisuijin','minezou','sazanami','uppy','mizuchi','ootsunoryuu'].map(id=>{const m=X.mon(id,100);m.moves=['hisuiounohoukou','kokuenha','tenryuuzan','ryuujinha'];return m});t.loadMap('stadiumIn',8,4,'up');"],
]
GYM6=r"""()=>{const t=__t,X=__x;X.SCN.find(s=>s[0]==='オオアミジム')[1]();t.mode='world';const S=X.S();S.party=[X.mon('glencon',100),X.mon('uzushion',100)];
 const run=n=>{for(let i=0;i<n;i++){t.update();for(const k in t.pressed)t.pressed[k]=false}};
 const drain=()=>{for(let i=0;i<8000;i++){if(t.mode==='world'&&!t.Q.length&&!X.fade()&&X.P().mv===0)return;if(t.Q.length&&t.Q[0].learn)t.pressed.b=true;else if(i%2)t.pressed.a=true;run(1)}};
 const C=X.CUR(),occ=()=>new Set(C.npcs.filter(e=>!X.hid(e)).map(e=>e.x+','+e.y)),walk=(x,y,sw)=>{const o=S.flags.g6sw;S.flags.g6sw=sw;const r=X.canHero(X.at(x,y));S.flags.g6sw=o;return r};
 const DIR=[[1,0,'right'],[-1,0,'left'],[0,1,'down'],[0,-1,'up']],L=C.npcs.find(e=>e.id==='shirasato');
 const plan=()=>{const P=X.P(),sw=S.flags.g6sw?1:0,O=occ(),s0=P.x+','+P.y+','+sw,prev=new Map([[s0,null]]),q=[[P.x,P.y,sw]];
  while(q.length){const[x,y,s]=q.shift(),k=x+','+y+','+s;for(const[dx,dy,d]of DIR){const nx=x+dx,ny=y+dy;
   if(nx===L.x&&ny===L.y){const a=[['face',d]];let c=k;while(prev.get(c)){const[pk,v]=prev.get(c);a.unshift(v);c=pk}return a}
   if(X.at(nx,ny)==='@'){const nk=x+','+y+','+(1-s);if(!prev.has(nk)){prev.set(nk,[k,['sw',d]]);q.push([x,y,1-s])}}
   if(!O.has(nx+','+ny)&&walk(nx,ny,s)){const nk=nx+','+ny+','+s;if(!prev.has(nk)){prev.set(nk,[k,['mv',d]]);q.push([nx,ny,s])}}}}return null};
 const acts=plan();if(!acts)return{ok:false,why:'シラサトまで いけない'};
 for(const[a,d]of acts){drain();if(a==='mv'){const P=X.P(),bx=P.x,by=P.y;for(let i=0;i<20&&X.P().x===bx&&X.P().y===by;i++){t.setKey(d,true);t.update();t.setKey(d,false);for(const k in t.pressed)t.pressed[k]=false;if(t.Q.length||t.mode!=='world')break}run(10)}else{X.P().dir=d;t.pressed.a=true;run(1);drain()}}
 t.pressed.a=true;run(1);drain();return{ok:!!S.flags.shirasato&&S.badges.length===6,why:'バッジ '+S.badges.length+'こ'}}"""
async def main():
    page=(ROOT/'dist'/'test.html').read_text(encoding='utf-8').replace('window.__t={',INJ,1)
    tmp=ROOT/'dist'/'playthrough.html';tmp.write_text(page,encoding='utf-8')
    only=sys.argv[1:]
    ng=0
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
        async def fresh():
            await pg.goto(tmp.as_uri());await pg.wait_for_function('window.__t',timeout=20000)
            await pg.add_script_tag(content=BOT)
            await pg.evaluate("()=>{window.requestAnimationFrame=()=>0;const t=__t;t.pressed.a=true;t.update();t.pressed.a=false}")
        for ch in CHAPTERS:
            name,want,budget,pre=ch[:4];goals=ch[4] if len(ch)>4 else []
            if only and not any(o in name for o in only):continue
            await fresh();errs.clear();t0=time.time()
            r=await pg.evaluate("""([name,want,budget,pre,goals])=>{BOT.setGoals(goals);const t=__t,X=__x;const run=n=>{for(let i=0;i<n;i++){t.update();for(const k in t.pressed)t.pressed[k]=false}};
              const sc=X.SCN.find(s=>s[0]===name);if(!sc)return{err:'シナリオが ない'};t.Q.length=0;t.menu=null;sc[1]();t.mode='world';X.setDEV({noenc:true});
              let inj=false;const strong=()=>{const S=X.S();if(inj||!S.flags.starter||!S.party.length)return;inj=true;S.party=[X.mon('hisuijin',100),X.mon('glencon',100),X.mon('uzushion',100),...S.party.filter(m=>m.id==='sazanami')]};
              strong();if(pre)(new Function('t','X','run',pre))(t,X,run);
              let i=0;for(;i<budget;i++){strong();BOT.tick();t.update();if(X.afterKey){X.afterKey();X.afterKey=null}for(const k in t.pressed)t.pressed[k]=false;
                if(want.every(f=>X.S().flags[f]))break}
              const S=X.S();return{frames:i,map:S.map,missing:want.filter(f=>!S.flags[f])}}""",[name,want,budget,pre,goals])
            ok=not r.get('err') and not r['missing'] and not errs
            ng+=0 if ok else 1
            print(('OK ' if ok else 'NG ')+name,f"{r.get('frames')}フレーム {time.time()-t0:.0f}びょう",'' if ok else f"たりない フラグ:{r.get('missing')} エラー:{errs} {r.get('err','')} いまの マップ:{r.get('map')}")
        if not only or any('オオアミジム' in o for o in only):
            await fresh();errs.clear()
            r=await pg.evaluate(GYM6);ok=r['ok'] and not errs;ng+=0 if ok else 1
            print(('OK ' if ok else 'NG ')+'オオアミジム（スイッチの しかけ）',r['why'],errs)
        await b.close()
    tmp.unlink(missing_ok=True)
    print('all OK' if not ng else f'NG {ng}けん');sys.exit(1 if ng else 0)
asyncio.run(main())
