"""Self-contained Korean SVG maps. Geography is projected; routes show visit order.
Run with NotoSansKR.ttf and coastal GeoJSON available; no browser fonts required.
"""
import json, math, html, re, urllib.request, tempfile
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT=Path(__file__).resolve().parents[1]
CACHE=Path(tempfile.gettempdir())/'okinawa-map-build';CACHE.mkdir(exist_ok=True)
def cached(name,url):
    p=CACHE/name
    if not p.exists():p.write_bytes(urllib.request.urlopen(url,timeout=90).read())
    return p
FONT=cached('NotoSansKR.ttf','https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf')
JAPAN=cached('japan.geojson','https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/JPN/ADM0/geoBoundaries-JPN-ADM0.geojson')
s=(ROOT/'itinerary-data.js').read_text(); DATA=json.loads(s[s.index('{'):].rstrip(';\n'))
COAST=[]
for feature in json.loads(JAPAN.read_text())['features']:
    geom=feature['geometry'];polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
    for polygon in polys:
        if any(127.5<x<128.4 and 26<y<26.95 for x,y,*_ in polygon[0]):COAST.append(polygon[0])
font=TTFont(FONT); glyphs=font.getGlyphSet(location={'wght':750}); cmap=font.getBestCmap(); U=font['head'].unitsPerEm
NAVY='#133e68'; BLUE='#086ab6'; CORAL='#df4761'
COLORS=['#6746bd','#ad7423','#de5264','#087baf','#b9337b','#23816b','#7445af','#466481']
used={}
def text(x,y,words,size=36,color=NAVY,anchor='start',opacity=1):
    total=sum(glyphs[cmap.get(ord(c),'space')].width for c in words)*size/U
    if anchor=='middle':x-=total/2
    if anchor=='end':x-=total
    out=[];pos=0
    for c in words:
        name=cmap.get(ord(c),'space');g=glyphs[name];gid='g'+str(ord(c))
        if gid not in used:
            pen=SVGPathPen(glyphs);g.draw(pen);used[gid]=pen.getCommands()
        out.append(f'<use href="#{gid}" transform="translate({pos:.2f} 0)"/>');pos+=g.width
    return f'<g aria-label="{html.escape(words)}" fill="{color}" opacity="{opacity}" transform="translate({x:.1f} {y:.1f}) scale({size/U:.5f} {-size/U:.5f})">'+''.join(out)+'</g>'
def rect(x,y,w,h,fill,rx=20,stroke='none',sw=1):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def circle(x,y,r,fill,stroke='none',sw=1):return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def path(points,stroke,width=3,fill='none',extra=''):
    return '<path d="M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'
def projection(bounds,viewport):
    lo,la,hi,ha=bounds;x,y,w,h=viewport;cos=math.cos(math.radians((la+ha)/2));k=min(w/((hi-lo)*cos),h/(ha-la));cx=(lo+hi)/2;cy=(la+ha)/2
    return lambda lng,lat:(x+w/2+(lng-cx)*cos*k,y+h/2-(lat-cy)*k)
def geography(P,clip):
    out=[]
    for ring in COAST:
        q=[P(a,b) for a,b,*_ in ring]
        d='M'+' L'.join(f'{a:.1f},{b:.1f}' for a,b in q)+' Z'
        out.append(f'<path d="{d}" fill="url(#land)" stroke="#68b69e" stroke-width="2.4"/>')
        out.append(f'<path d="{d}" fill="none" stroke="#e4f4b3" stroke-width="5" opacity=".7"/>')
    return f'<g clip-path="url(#{clip})">'+''.join(out)+'</g>'
def flower(x,y,scale=1):
    return f'<g transform="translate({x} {y}) scale({scale})">'+''.join(f'<ellipse cx="0" cy="-26" rx="24" ry="39" fill="{CORAL}" transform="rotate({i*72})"/>' for i in range(5))+circle(0,0,13,'#ffe09a')+'<path d="M0 0 Q20 -12 33 -48" stroke="#ffe09a" stroke-width="5" fill="none"/>'+circle(33,-48,7,'#ffe09a')+'</g>'
def compass(x,y):return f'<path d="M{x},{y} l-13,43 13,-8 13,8 Z" fill="{NAVY}"/>'+text(x,y-12,'북',25,anchor='middle')
def number(x,y,n,r=23,color=BLUE):return circle(x,y,r,color,'white',4)+text(x,y+size_offset(n,r),str(n),r*1.25,'white','middle')
def size_offset(n,r):return r*.43
def header(day,title,sub):
    return rect(0,0,1600,1500,'#e8f7fd',0)+rect(28,28,1544,1444,'#f9fdff',36,'#c3e4ef',2)+flower(104,105,.8)+text(185,111,title,62)+text(187,170,sub,31,'#52768e')+rect(1370,65,165,66,NAVY,33)+text(1452,110,day,30,'white','middle')
def finish(body,title,clips):
    body+=text(800,1465,'지도 바탕: 일본 국토교통성 · geoBoundaries / CC BY 4.0',19,'#607e90','middle')
    defs='<linearGradient id="sea" x2="0" y2="1"><stop stop-color="#b9eaff"/><stop offset="1" stop-color="#86ceed"/></linearGradient><linearGradient id="land" x2="1" y2="1"><stop stop-color="#e4f1b1"/><stop offset=".5" stop-color="#c4dfa0"/><stop offset="1" stop-color="#a8d092"/></linearGradient>'
    defs+=clips+''.join(f'<path id="{k}" d="{v}"/>' for k,v in used.items())
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1500" viewBox="0 0 1600 1500" role="img"><title>{html.escape(title)}</title><defs>{defs}</defs>{body}</svg>'
    return re.sub(r'-?\d+\.\d{3,}',lambda m:format(float(m.group()),'.2f').rstrip('0').rstrip('.'),svg)
def wrap(s,n=7):
    # Break on word boundaries whenever a Korean place name allows it.
    words=s.split();lines=[];line=''
    for w in words:
        if line and len(line)+len(w)+1>n:lines.append(line);line=w
        else:line=(line+' '+w).strip()
    if line:lines.append(line)
    return lines
THEMES=['도착 후, 시장과 골목을 가볍게','류큐의 역사와 동네 저녁','동굴과 공연, 작은 섬의 간식','도자기와 전망 카페를 따라 북쪽으로','푸른 고우리 바다와 나고의 맛','고래상어를 만나고 초록길을 걸어요','서해안 풍경을 따라 나하로','여유 있게 반납하고 공항으로']
for idx,day in enumerate(DATA['days']):
    used.clear();pts=day['map']; merged=[]
    for j,p in enumerate(pts):
        old=next((q for q in merged if q['name']==p['name'] and q['lat']==p['lat'] and q['lng']==p['lng']),None)
        if old:old['nums'].append(j+1)
        else:merged.append(dict(p,nums=[j+1]))
    xs=[p['lng'] for p in pts];ys=[p['lat'] for p in pts];cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
    bw=max(.037,max(xs)-min(xs));bh=max(.033,max(ys)-min(ys));bounds=(cx-bw*.66,cy-bh*.66,cx+bw*.66,cy+bh*.66)
    P=projection(bounds,(755,365,480,630));L=projection((127.58,26.02,128.34,26.92),(66,340,350,660))
    b=header(f'{idx+1}일차',f'{day["date"]} · {day["area"]}',THEMES[idx])
    b+=rect(58,234,358,858,'url(#sea)',24,'#97cbdf',2)+rect(449,234,1093,858,'url(#sea)',24,'#6aaacb',3)
    b+=geography(L,'locator')+geography(P,'detail')
    b+=rect(74,253,324,63,'white',17)+text(236,298,'전체에서 보기',36,anchor='middle')
    b+=rect(470,254,330,63,CORAL,16)+text(635,298,'오늘의 확대 경로',34,'white','middle')+compass(1490,340)
    # Locator context and the actual highlighted bounding region.
    q1=L(bounds[0],bounds[3]);q2=L(bounds[2],bounds[1]);ww=max(23,q2[0]-q1[0]);hh=max(23,q2[1]-q1[1])
    b+=f'<rect x="{q1[0]:.1f}" y="{q1[1]:.1f}" width="{ww:.1f}" height="{hh:.1f}" fill="#df4761" fill-opacity=".14" stroke="{CORAL}" stroke-width="4" stroke-dasharray="10 7"/>'
    for name,lng,lat,dx,dy in [('나하',127.679,26.214,-54,4),('나고',127.977,26.591,15,26),('고우리섬',128.02,26.71,-100,-27)]:
        xx,yy=L(lng,lat);b+=circle(xx,yy,6,BLUE,'white',2)+text(xx+dx,yy+dy,name,28)
    b+=text(237,1030,'빨간 구역을 확대 →',27,CORAL,'middle')
    q=[P(p['lng'],p['lat']) for p in pts]
    b+='<g clip-path="url(#detail)">'+path(q,'white',12)+path(q,CORAL,6,extra='stroke-dasharray="13 10"')+'</g>'
    # Place labels live in separate rows; close coordinates retain distinct leader lines.
    ranked=sorted(merged,key=lambda p:p['lng']);split=(len(ranked)+1)//2
    for side,group in enumerate([ranked[:split],ranked[split:]]):
        group.sort(key=lambda p:-p['lat'])
        for j,p in enumerate(group):
            yy=388+j*(245 if len(group)>2 else 360);xx=471 if side==0 else 1263
            px,py=P(p['lng'],p['lat']);edge=xx+244 if side==0 else xx;end=yy+52
            b+=path([(px,py),(edge+(16 if side==0 else -16),end),(edge,end)],'#446f8a',2.5)
            b+=circle(px,py,9,BLUE,'white',4)
            b+=rect(xx,yy,252,146,'#ffffff',18,'#d2e7ef',2)
            nums='·'.join(map(str,p['nums']));b+=rect(xx+13,yy+12,74,40,BLUE,20)+text(xx+50,yy+42,nums,28,'white','middle')
            name=p['name'];lines=wrap(name,7)
            for k,line in enumerate(lines):b+=text(xx+16,yy+86+k*38,line,33)
            if any(v in name for v in ['호텔','주유소','렌터카']):b+=text(xx+236,yy+39,'예정',24,'#647f90','end')
    b+=text(995,1060,'점선은 방문 순서 · 실제 도로 경로는 아래 구글 지도 확인',25,NAVY,'middle')
    b+=text(67,1166,'이 순서로 함께 둘러봐요',40)
    for j,p in enumerate(pts):
        col=j%3;row=j//3;x=65+col*507;y=1197+row*95
        b+=rect(x,y,478,77,'#ecf5f9',17)+number(x+39,y+38,j+1,22)
        name=p['name'];b+=text(x+77,y+48,name,29)
    b+=text(67,1430,'숙소·주유소·반납 장소는 대표 위치이며 확정 후 조정해요.',26,'#607e90')
    clips='<clipPath id="locator">'+rect(58,234,358,858,'white',24)+'</clipPath><clipPath id="detail">'+rect(449,234,1093,858,'white',24)+'</clipPath>'
    (ROOT/f'maps/day-{idx+1}.svg').write_text(finish(b,f'{idx+1}일차 {day["area"]} 관광지도',clips))

# The main page uses the same visual language with a full-island route overview.
used.clear();P=projection((127.57,26.04,128.35,26.91),(180,300,670,1030))
b=header('전체 경로','우리 가족 오키나와 여행','나하 3박 → 나고 3박 → 나하 1박 · 7박 8일')
b+=rect(60,235,925,1130,'url(#sea)',26,'#97cbdf',2)+geography(P,'overview')+compass(925,320)
for i,day in enumerate(DATA['days']):
    q=[P(p['lng'],p['lat']) for p in day['map']];b+=path(q,'white',8)+path(q,COLORS[i],4)
for name,lng,lat,dx,dy in [('나하',127.679,26.214,-108,-5),('나고',127.977,26.591,24,42),('고우리섬',128.02,26.71,16,-23),('모토부·비세',127.8779,26.6943,-213,-29),('온나·만좌모',127.851,26.5048,-217,-5),('차탄',127.758,26.316,22,18),('오키나와 남부',127.7484,26.1414,25,24)]:
    x,y=P(lng,lat);b+=circle(x,y,10,BLUE,'white',4)+text(x+dx,y+dy,name,36)
for i,day in enumerate(DATA['days']):
    y=238+i*138;b+=rect(1020,y,518,121,'#eef6fa',18)+rect(1020,y,9,121,COLORS[i],4)
    b+=text(1048,y+47,f'{i+1}일차 · {day["date"]}',32,COLORS[i])+text(1048,y+92,day['area'],32)
b+=text(74,1420,'색상별 선은 방문 순서예요. 실제 도로 경로는 날짜별 구글 지도에서 확인하세요.',27,'#607e90')
(ROOT/'maps/overview.svg').write_text(finish(b,'오키나와 7박 8일 전체 이동 경로','<clipPath id="overview">'+rect(60,235,925,1130,'white',26)+'</clipPath>'))
print('Created 8 daily maps and overview')
