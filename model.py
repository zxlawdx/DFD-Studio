"""Modelo e geometria independentes da interface. Python 3.10+."""
import copy
import json
import math
import textwrap
import uuid
from pathlib import Path

BLUE = '#2563eb'
GREEN = '#078453'
KINDS = {'process': 'Processo', 'entity': 'Entidade externa', 'store': 'Depósito de dados', 'note': 'Anotação'}
PORTS = ('auto', 'left', 'right', 'top', 'bottom')

def uid():
    return uuid.uuid4().hex[:12]

def blank():
    return {'format': 'dfd-studio', 'version': 1, 'title': 'Detalhamento do módulo 01', 'author': '', 'notes': '', 'nodes': [], 'edges': []}

def node(kind, code, text, x, y, color=BLUE, details='', w=190, h=100, id=None):
    return dict(id=id or uid(), kind=kind, code=code, text=text, x=x, y=y, w=w, h=h, color=color, details=details)

def edge(source, target, text='', color=BLUE, **kwargs):
    return dict(id=uid(), source=source, target=target, text=text, color=color,
                source_port=kwargs.get('source_port','auto'), target_port=kwargs.get('target_port','auto'),
                route=kwargs.get('route','horizontal'), bends=kwargs.get('bends',[]),
                label_dx=kwargs.get('label_dx',0), label_dy=kwargs.get('label_dy',-12), details=kwargs.get('details',''))

def validate(data):
    if not isinstance(data,dict) or data.get('format')!='dfd-studio' or data.get('version')!=1:
        raise ValueError('Este arquivo não é um projeto DFD Studio versão 1.')
    if not isinstance(data.get('nodes'),list) or not isinstance(data.get('edges'),list):
        raise ValueError('Listas de elementos ausentes.')
    if len(data['nodes'])>2000 or len(data['edges'])>5000:
        raise ValueError('Projeto excede o limite de elementos.')
    for key in ('title','author','notes'):
        if not isinstance(data.get(key),str):raise ValueError('Metadados inválidos.')
    ids=set()
    for n in data['nodes']:
        if n['id'] in ids or n['kind'] not in KINDS: raise ValueError('Elemento inválido ou duplicado.')
        ids.add(n['id'])
        for k in ('x','y','w','h'):
            if not isinstance(n[k],(float,int)) or not math.isfinite(n[k]) or abs(n[k])>100000: raise ValueError('Dimensão inválida.')
        if n['w']<80 or n['h']<50: raise ValueError('Dimensões mínimas: 80 × 50.')
        for k in ('text','code','color','details'):
            if not isinstance(n.get(k),str): raise ValueError('Texto de elemento inválido.')
    edge_ids=set()
    for e in data['edges']:
        if e['id'] in edge_ids or e['source'] not in ids or e['target'] not in ids: raise ValueError('Conexão inválida.')
        edge_ids.add(e['id'])
        if e['source_port'] not in PORTS or e['target_port'] not in PORTS: raise ValueError('Porta inválida.')
        if e['route'] not in ('horizontal','vertical','direct'): raise ValueError('Rota inválida.')
        for p in e['bends']:
            if len(p)!=2 or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in p): raise ValueError('Ponto inválido.')
        for k in ('label_dx','label_dy'):
            if not isinstance(e[k],(int,float)) or not math.isfinite(e[k]): raise ValueError('Rótulo inválido.')
        for k in ('text','color','details'):
            if not isinstance(e.get(k),str): raise ValueError('Texto de conexão inválido.')
    return data

def read(path):
    return validate(json.loads(Path(path).read_text(encoding='utf-8')))

def write(path, data):
    validate(data)
    p=Path(path)
    tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    tmp.replace(p)

def center(n): return (n['x']+n['w']/2,n['y']+n['h']/2)

def port(n, side, toward):
    x,y=center(n)
    if side=='auto':
        dx,dy=toward[0]-x,toward[1]-y
        side=('right' if dx>=0 else 'left') if abs(dx)/n['w']>=abs(dy)/n['h'] else ('bottom' if dy>=0 else 'top')
    return {'left':(n['x'],y),'right':(n['x']+n['w'],y),'top':(x,n['y']),'bottom':(x,n['y']+n['h'])}[side]

def simplify(points):
    out=[]
    for p in points:
        if out and p==out[-1]: continue
        out.append(p)
        while len(out)>=3:
            a,b,c=out[-3:]
            if (a[0]==b[0]==c[0] or a[1]==b[1]==c[1]): out.pop(-2)
            else: break
    if len(out)==1:
        x,y=out[0];return [out[0],(x+30,y-30),out[0]]
    return out

def path_points(data,e):
    ns={n['id']:n for n in data['nodes']}
    a,b=ns[e['source']],ns[e['target']]
    bends=e.get('bends',[])
    start=port(a,e['source_port'],bends[0] if bends else center(b))
    end=port(b,e['target_port'],bends[-1] if bends else center(a))
    if bends: return simplify([start,*bends,end])
    if e['route']=='direct': return [start,end]
    if e['route']=='vertical':
        m=(start[1]+end[1])/2
        return simplify([start,(start[0],m),(end[0],m),end])
    m=(start[0]+end[0])/2
    return simplify([start,(m,start[1]),(m,end[1]),end])

def label_pos(points,e):
    if not e.get('bends'):
        left=sum(math.dist(a,b) for a,b in zip(points,points[1:]))/2
        for a,b in zip(points,points[1:]):
            length=math.dist(a,b)
            if length and left<=length:
                ratio=left/length
                return (a[0]+(b[0]-a[0])*ratio+e['label_dx'],a[1]+(b[1]-a[1])*ratio+e['label_dy'])
            left-=length
    a,b=max(zip(points,points[1:]),key=lambda pair: math.dist(*pair))
    return ((a[0]+b[0])/2+e['label_dx'],(a[1]+b[1])/2+e['label_dy'])

def lines(text, width):
    out=[]
    for p in text.split('\n'):
        out.extend(textwrap.wrap(p,max(4,width),break_long_words=True) or [''])
    return out

def primitives(data):
    """Primitivas compartilhadas por canvas e SVG, com IDs para seleção."""
    out=[]
    def add(kind, coords, owner, **kw): out.append(dict(kind=kind,coords=coords,owner=owner,**kw))
    for e in data['edges']:
        pts=path_points(data,e); owner='e:'+e['id']
        add('line',pts,owner,color=e['color'],width=2,arrow=True)
        if e['text']:
            x,y=label_pos(pts,e); txt=lines(e['text'],23)
            w=max(map(len,txt))*6.7+12; h=len(txt)*17+6
            add('rect',(x-w/2,y-h/2,w,h),owner,fill='white',color='',width=0,radius=3)
            add('text',(x,y),owner,text='\n'.join(txt),color='#334155',size=12)
    for n in data['nodes']:
        owner='n:'+n['id']; x,y,w,h=(n[k] for k in ('x','y','w','h')); c=n['color']; typ=n['kind']
        if typ=='store':
            add('rect',(x,y,w,h),owner,fill='white',color='',width=0,radius=0)
            add('line',[(x+w,y),(x,y),(x,y+h),(x+w,y+h)],owner,color=c,width=2,arrow=False)
            add('line',[(x+58,y),(x+58,y+h)],owner,color=c,width=1.5,arrow=False)
            add('text',(x+29,y+h/2),owner,text=n['code'],color=c,size=12)
            add('text',(x+58+(w-58)/2,y+h/2),owner,text='\n'.join(lines(n['text'],int((w-72)/7))),color='#16243a',size=13)
        else:
            add('rect',(x,y,w,h),owner,fill='#fffbea' if typ=='note' else 'white',color=c,width=2.3,radius=14 if typ=='process' else 0)
            if n['code']:
                add('line',[(x,y+27),(x+w,y+27)],owner,color=c,width=1.3,arrow=False)
                add('text',(x+w/2,y+14),owner,text=n['code'],color=c,size=12)
            offset=27 if n['code'] else 0
            add('text',(x+w/2,y+offset+(h-offset)/2),owner,text='\n'.join(lines(n['text'],int((w-20)/7.4))),color='#16243a',size=14)
    return out

def bounds(data):
    boxes=[]
    for p in primitives(data):
        if p['kind']=='line':
            boxes.extend((x,y) for x,y in p['coords'])
        elif p['kind']=='rect':
            x,y,w,h=p['coords']; boxes.extend([(x,y),(x+w,y+h)])
        else:
            x,y=p['coords']; txt=p['text'].split('\n'); w=max(map(len,txt),default=0)*p['size']*.6; h=len(txt)*p['size']*1.35
            boxes.extend([(x-w/2,y-h/2),(x+w/2,y+h/2)])
    if not boxes: return (0,0,1000,650)
    xs,ys=zip(*boxes)
    return (min(xs)-35,min(ys)-35,max(xs)-min(xs)+70,max(ys)-min(ys)+70)
