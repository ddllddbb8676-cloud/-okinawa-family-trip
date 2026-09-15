/* Accessible map image viewer: pinch, pan, wheel, keyboard and large controls. */
window.tripMapCard=(file,title)=>`<figure class="trip-map-figure"><a class="trip-map-open" href="maps/${file}.svg" target="_blank" rel="noopener" data-map-link data-map-title="${title}" aria-label="${title} 크게 보기"><img src="maps/${file}.svg" alt="${title} · 전체 섬 위치와 확대 경로" width="1600" height="1500" loading="lazy" decoding="async"><span>지도 크게 보기 · 누르세요 ↗</span></a><figcaption>확대 화면에서 두 손가락으로 확대하고, 드래그해서 옮길 수 있어요.</figcaption></figure>`;
document.addEventListener('DOMContentLoaded',()=>{
  const dialog=document.createElement('dialog');dialog.className='map-lightbox';
  dialog.setAttribute('aria-labelledby','map-view-title');
  dialog.innerHTML=`<header class="map-lightbox-head"><h2 id="map-view-title">지도 크게 보기</h2><button type="button" data-action="close" aria-label="지도 닫기">닫기 ×</button></header><div class="map-controls"><button type="button" data-action="out" aria-label="지도 축소">−</button><output aria-live="polite" id="map-zoom-level">100%</output><button type="button" data-action="in" aria-label="지도 확대">＋</button><button type="button" data-action="fit">전체 보기</button><a class="map-original" target="_blank" rel="noopener">원본 ↗</a></div><p class="map-help">두 손가락으로 확대 · 한 손가락으로 이동</p><div class="map-pan-area" tabindex="0" role="region" aria-label="확대 지도. 더하기와 빼기로 확대 축소, 방향키로 이동"><img class="map-large-image" draggable="false" alt=""></div><p class="map-load-status" role="status"></p>`;
  document.body.append(dialog);
  const area=dialog.querySelector('.map-pan-area'),img=dialog.querySelector('img'),level=dialog.querySelector('output'),status=dialog.querySelector('.map-load-status');
  const points=new Map();let zoom=1,panX=0,panY=0,baseW=0,baseH=0,opener=null,bodyOverflow='',gesture=null;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  function render(){
    const mx=Math.max(0,(baseW*zoom-area.clientWidth)/2),my=Math.max(0,(baseH*zoom-area.clientHeight)/2);
    panX=clamp(panX,-mx,mx);panY=clamp(panY,-my,my);
    img.style.width=baseW+'px';img.style.height=baseH+'px';
    img.style.transform=`translate(calc(-50% + ${panX}px),calc(-50% + ${panY}px)) scale(${zoom})`;
    level.textContent=Math.round(zoom*100)+'%';area.classList.toggle('is-zoomed',zoom>1);
    dialog.querySelector('[data-action="out"]').disabled=zoom<=1;
    dialog.querySelector('[data-action="in"]').disabled=zoom>=6;
  }
  function fit(){const ratio=(img.naturalWidth||1600)/(img.naturalHeight||1500);baseW=Math.min(area.clientWidth-20,(area.clientHeight-20)*ratio);baseH=baseW/ratio;zoom=1;panX=panY=0;render();}
  function zoomAt(next,x=0,y=0){const before=zoom;zoom=clamp(next,1,6);panX=x-(x-panX)*zoom/before;panY=y-(y-panY)*zoom/before;render();}
  function local(e){const r=area.getBoundingClientRect();return {x:e.clientX-r.left-r.width/2,y:e.clientY-r.top-r.height/2};}
  function startGesture(){const p=[...points.values()];gesture=p.length>1?{distance:Math.hypot(p[1].x-p[0].x,p[1].y-p[0].y),cx:(p[0].x+p[1].x)/2,cy:(p[0].y+p[1].y)/2}:p.length?{x:p[0].x,y:p[0].y}:null;}
  img.addEventListener('load',()=>{status.textContent='';fit();});
  img.addEventListener('error',()=>{status.textContent='지도를 불러오지 못했어요. 원본 버튼으로 다시 열어 주세요.';});
  document.addEventListener('click',e=>{
    const link=e.target.closest('[data-map-link]');if(!link||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;
    e.preventDefault();opener=link;bodyOverflow=document.body.style.overflow;document.body.style.overflow='hidden';
    points.clear();gesture=null;status.textContent='지도를 불러오는 중…';img.alt=link.dataset.mapTitle;
    dialog.querySelector('h2').textContent=link.dataset.mapTitle;dialog.querySelector('.map-original').href=link.href;
    img.src=link.href;dialog.showModal();fit();if(img.complete&&img.naturalWidth)status.textContent='';
    dialog.querySelector('[data-action="close"]').focus();
  });
  dialog.addEventListener('click',e=>{const action=e.target.closest('[data-action]')?.dataset.action;if(action==='close')dialog.close();if(action==='fit')fit();if(action==='in')zoomAt(zoom*1.5);if(action==='out')zoomAt(zoom/1.5);});
  dialog.addEventListener('close',()=>{points.clear();gesture=null;document.body.style.overflow=bodyOverflow;opener?.focus({preventScroll:true});});
  area.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse'&&e.button!==0)return;area.setPointerCapture(e.pointerId);points.set(e.pointerId,local(e));startGesture();});
  area.addEventListener('pointermove',e=>{
    if(!points.has(e.pointerId)||!gesture)return;points.set(e.pointerId,local(e));const p=[...points.values()];
    if(p.length>1){const dist=Math.hypot(p[1].x-p[0].x,p[1].y-p[0].y),cx=(p[0].x+p[1].x)/2,cy=(p[0].y+p[1].y)/2;
      if(gesture.distance>0){zoomAt(zoom*dist/gesture.distance,gesture.cx,gesture.cy);panX+=cx-gesture.cx;panY+=cy-gesture.cy;render();}}
    else if(gesture.x!==undefined){panX+=p[0].x-gesture.x;panY+=p[0].y-gesture.y;render();}
    startGesture();
  });
  for(const type of ['pointerup','pointercancel','lostpointercapture'])area.addEventListener(type,e=>{points.delete(e.pointerId);startGesture();});
  area.addEventListener('wheel',e=>{e.preventDefault();const p=local(e);zoomAt(zoom*Math.exp(-e.deltaY*.002),p.x,p.y);},{passive:false});
  area.addEventListener('dblclick',e=>{const p=local(e);zoomAt(zoom>1?1:2.5,p.x,p.y);});
  dialog.addEventListener('keydown',e=>{if(['+','=','-','ArrowLeft','ArrowRight','ArrowUp','ArrowDown','0'].includes(e.key)){e.preventDefault();if(e.key==='+'||e.key==='=')zoomAt(zoom*1.5);if(e.key==='-')zoomAt(zoom/1.5);if(e.key==='0')fit();if(e.key==='ArrowLeft')panX+=70;if(e.key==='ArrowRight')panX-=70;if(e.key==='ArrowUp')panY+=70;if(e.key==='ArrowDown')panY-=70;render();}});
  new ResizeObserver(()=>{if(dialog.open)fit();}).observe(area);
});
