// プレイ ボット（tests/playthrough.py から つかう）：じっさいに あるいて はなしかけ、でぐち・アイテム・スイッチを ためし、バトルは A れんだで すすめる
window.BOT=(()=>{const X=__x,t=__t;
 const sig=()=>{const S=X.S();return JSON.stringify([Object.keys(S.flags).filter(k=>S.flags[k]&&!/^it_|f$|^t3step$|^g6sw$/.test(k)).sort(),S.badges.length])};
 let swc=new Map(),talked=new Set(),used=new Set(),lastSig='',path=[],target=null,stuck=0,log=[],steps=0,lastMap='',blocked=new Set(),noTarget=0,flagsSeen=new Set();
 const SKIP_ROLE=new Set(['shop','fishgame','tutor']);
 function neighbors(x,y){return[[1,0,'right'],[-1,0,'left'],[0,1,'down'],[0,-1,'up']].map(([dx,dy,d])=>[x+dx,y+dy,d])}
 function passable(x,y){const C=X.CUR();if(x<0||y<0||x>=C.w||y>=C.h)return false;if(blocked.has(X.S().map+':'+x+','+y))return false;return X.canHero(X.at(x,y))&&!X.entityAt(x,y)}
 function bfs(goal){const P=X.P(),start=P.x+','+P.y,prev=new Map([[start,null]]),q=[[P.x,P.y]];
  const W=X.CUR().warps||{},m=X.S().map;
  while(q.length){const[x,y]=q.shift();const k=x+','+y;const g=goal(x,y);if(g)return{path:back(prev,k),g};
   const w=W[k];if(w&&w[0]===m&&k!==start){const dk=w[1]+','+w[2];if(!prev.has(dk)){prev.set(dk,[k,'_tp']);q.push([w[1],w[2]])}continue}
   for(const[nx,ny,d]of neighbors(x,y)){const nk=nx+','+ny;if(prev.has(nk))continue;if(!passable(nx,ny)){const gg=goal(nx,ny,true);if(gg){prev.set(nk,[k,d]);return{path:back(prev,nk),g:gg,into:true}}continue}prev.set(nk,[k,d]);q.push([nx,ny])}}
  return null}
 function back(prev,k){const out=[];while(prev.get(k)){const[pk,d]=prev.get(k);if(d!=='_tp')out.unshift(d);else out.unshift('_tp');k=pk}return out}
 function chooseTarget(){const S=X.S(),C=X.CUR(),m=S.map;
  const npcs=C.npcs.filter(e=>!X.hid(e)&&(!e.obj||e.obj==='crack')&&!SKIP_ROLE.has(e.role)&&!talked.has(m+':'+(e.id||e.x+','+e.y)));
  const spots=new Map();
  for(const e of npcs){for(const[nx,ny,d]of neighbors(e.x,e.y)){spots.set(nx+','+ny,{kind:'npc',e,face:{right:'left',left:'right',down:'up',up:'down'}[d]})}
   for(const[dx,dy,f]of[[0,2,'up'],[0,-2,'down'],[2,0,'left'],[-2,0,'right']]){const cx=e.x+dx/2,cy=e.y+dy/2;if(X.at(cx,cy)==='c')spots.set((e.x+dx)+','+(e.y+dy),{kind:'npc',e,face:f})}}
  for(const k in(C.warps||{}))if(!used.has(m+':'+k))spots.set(k,{kind:'warp',k});
  if(C.gates)for(let y=0;y<C.h;y++)for(let x=0;x<C.w;x++)if(X.at(x,y)==='@'&&(swc.get(x+','+y)||0)<2){const e={id:'sw'+x+','+y,x,y,sw:true};for(const[nx,ny,d]of neighbors(x,y))spots.set(nx+','+ny,{kind:'npc',e,face:{right:'left',left:'right',down:'up',up:'down'}[d]})}
  for(const d of C.items||[])if(!S.flags['it_'+d.id]&&!(d.showIf&&!S.flags[d.showIf])&&!talked.has(m+':it'+d.id))spots.set(d.x+','+d.y,{kind:'item',d});
  let npcOnly=new Map([...spots].filter(([k,v])=>(v.kind==='npc'&&!v.e.sw)||v.kind==='item'));if(!npcOnly.size)npcOnly=new Map([...spots].filter(([k,v])=>v.kind==='npc'));
  let r=npcOnly.size?bfs((x,y,into)=>{if(into)return null;return npcOnly.get(x+','+y)||null}):null;
  if(!r)r=bfs((x,y,into)=>{const s=spots.get(x+','+y);if(!s)return null;if(into&&s.kind!=='warp')return null;return s});
  return r}

 const S0=()=>X.S();
 function pending(m){const M=t.MAPS[m];if(!M)return false;
  if(M.npcs.some(e=>!X.hid(e)&&!e.obj&&!SKIP_ROLE.has(e.role)&&!talked.has(m+':'+(e.id||e.x+','+e.y))))return true;
  if((M.items||[]).some(d=>!S0().flags['it_'+d.id]&&!(d.showIf&&!S0().flags[d.showIf])&&!talked.has(m+':it'+d.id)))return true;
  return Object.keys(M.warps||{}).some(k=>!used.has(m+':'+k))}
 function travelTarget(){const S=X.S(),cur=S.map;
  // map graph BFS to nearest map with pending things
  const prev=new Map([[cur,null]]),q=[cur];let goal=null;
  while(q.length){const m=q.shift();if(m!==cur&&pending(m)){goal=m;break}
   for(const k in(t.MAPS[m].warps||{})){const d=t.MAPS[m].warps[k][0];if(!prev.has(d)){prev.set(d,m);q.push(d)}}}
  if(!goal)return null;let nxt=goal;while(prev.get(nxt)!==cur)nxt=prev.get(nxt);
  const C=X.CUR(),cands=new Map();for(const k in C.warps)if(C.warps[k][0]===nxt)cands.set(k,{kind:'warp',k,travel:true});
  return bfs((x,y,into)=>cands.get(x+','+y)||null)}

 let goals=[];
 function travelTo(goal){const cur=X.S().map;const prev=new Map([[cur,null]]),q=[cur];let found=false;
  while(q.length){const m=q.shift();if(m===goal){found=true;break}for(const k in(t.MAPS[m].warps||{})){const d=t.MAPS[m].warps[k][0];if(!prev.has(d)){prev.set(d,m);q.push(d)}}}
  if(!found)return null;let nxt=goal;while(prev.get(nxt)!==cur)nxt=prev.get(nxt);
  const C=X.CUR(),c=new Map();for(const k in C.warps)if(C.warps[k][0]===nxt)c.set(k,{kind:'warp',k,travel:true});
  return bfs((x,y,into)=>c.get(x+','+y)||null)}
 function press(k){t.pressed[k]=true}
 function tick(){const S=X.S();if(!S)return;steps++;
  for(const k in S.flags)if(S.flags[k]&&!flagsSeen.has(k)&&!/^it_|f$|^t3step$/.test(k)){flagsSeen.add(k);log.push([steps,S.map,'flag',k])}
  if(S.map!==lastMap){log.push([steps,S.map,'map']);lastMap=S.map;path=[];target=null}
  const md=t.mode;
  if(md==='title'){press('a');return}
  if(md==='battle'||md==='trans'||md==='evolve'||md==='starter'||md==='mini'){if(t.Q.length&&t.Q[0].learn){press('b');return}if(steps%2)press('a');return}
  if(md!=='world')return;
  if(X.fade())return;
  if(t.Q.length){const q=t.Q[0];if(q.learn||q.tutor){press('b');return}if(steps%2)press('a');return}
  if(t.menu||t.shop||X.boxui()){press('b');return}
  const P=X.P();if(P.mv>0)return;
  const sg=sig();if(sg!==lastSig){lastSig=sg;swc.clear();talked.clear();used.clear();blocked.clear();path=[];target=null}
  if(!target){let r=null;
   if(goals.length&&S.map!==goals[0]){r=travelTo(goals[0]);if(!r){goals.shift();return}}
   else{r=chooseTarget();if(!r&&goals.length){goals.shift();return}if(!r)r=travelTarget()}
   if(!r){noTarget++;return}noTarget=0;target=r.g;path=r.path;log.push([steps,S.map,'target',target.kind,target.k||(target.e&&(target.e.tname||target.e.role||target.e.id)),path.length]);if(target.kind==='warp')used.add(S.map+':'+target.k)}
  if(path.length&&path[0]==='_tp'){path.shift();return}
  if(path.length){const d=path[0];const bx=P.x,by=P.y;
   if(P._w&&P._w.x===bx&&P._w.y===by&&P._w.d===d&&P._w.n>3){const[dx,dy]={right:[1,0],left:[-1,0],down:[0,1],up:[0,-1]}[d];blocked.add(S.map+':'+(bx+dx)+','+(by+dy));path=[];target=null;P._w=null;return}
   t.setKey(d,true);X.afterKey=()=>t.setKey(d,false);
   P._w=(P._w&&P._w.x===bx&&P._w.y===by&&P._w.d===d)?{...P._w,n:P._w.n+1}:{x:bx,y:by,d,n:1};
   path.shift();return}
  // arrived
  if(target.kind==='npc'){const e=target.e;if(e.sw){swc.set(e.x+','+e.y,(swc.get(e.x+','+e.y)||0)+1);talked.clear();used.clear()}else talked.add(S.map+':'+(e.id||e.x+','+e.y));P.dir=target.face;press('a');log.push([steps,S.map,'talk',e.tname||e.role||e.id||'npc']);target=null;return}
  if(target.kind==='warp'){used.add(S.map+':'+target.k);target=null;return}
  if(target.kind==='item'){talked.add(S.map+':it'+target.d.id);target=null;return}
 }
 return{tick,log,setGoals:g=>{goals=g.slice()},get noTarget(){return noTarget},get steps(){return steps}}})();
