"""Exportação vetorial sem dependências externas."""
from html import escape
import math
from pathlib import Path
import model


def svg(data):
    x,y,w,h=model.bounds(data)
    esc=lambda t: escape(str(t),quote=True)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(data["title"])}">',
         '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="context-stroke"/></marker></defs>',
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white"/>']
    for p in model.primitives(data):
        color=esc(p['color']); co=p['coords']
        if p['kind']=='line':
            points=' '.join(f'{a},{b}' for a,b in co)
            out.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{p["width"]}" stroke-linejoin="round"/>')
            if p['arrow'] and len(co)>1:
                b=co[-1]; a=next((q for q in reversed(co[:-1]) if q!=b),co[0])
                angle=math.atan2(b[1]-a[1],b[0]-a[0]); dx=math.cos(angle);dy=math.sin(angle)
                triangle=[b,(b[0]-12*dx+5*dy,b[1]-12*dy-5*dx),(b[0]-12*dx-5*dy,b[1]-12*dy+5*dx)]
                ps=' '.join(f'{a},{b}' for a,b in triangle)
                out.append(f'<polygon points="{ps}" fill="{color}"/>')
        elif p['kind']=='rect':
            a,b,c,d=co
            out.append(f'<rect x="{a}" y="{b}" width="{c}" height="{d}" rx="{p["radius"]}" fill="{esc(p["fill"])}" stroke="{color or "none"}" stroke-width="{p["width"]}"/>')
        else:
            a,b=co; rows=p['text'].split('\n'); size=p['size']; step=size*1.35
            out.append(f'<text text-anchor="middle" font-family="Arial, sans-serif" font-size="{size}" fill="{color}">')
            for i,t in enumerate(rows):
                out.append(f'<tspan x="{a}" y="{b-(len(rows)-1)*step/2+i*step+size*.34}">{esc(t)}</tspan>')
            out.append('</text>')
    out.append('</svg>')
    return '\n'.join(out)


def html(data):
    esc=lambda t: escape(str(t),quote=True)
    ns={n['id']:n for n in data['nodes']}
    rows=[]
    for n in data['nodes']:
        if n['details']:
            rows.append(f'<tr><td>{esc(n["code"])} — {esc(n["text"])}</td><td>{esc(n["details"])}</td></tr>')
    for e in data['edges']:
        if e['details']:
            a,b=ns[e['source']],ns[e['target']]
            rows.append(f'<tr><td>{esc(a["code"] or a["text"])} → {esc(b["code"] or b["text"])}</td><td>{esc(e["details"])}</td></tr>')
    return '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>'''+esc(data['title'])+'''</title><style>
*{box-sizing:border-box}body{margin:0;background:#edf2f8;color:#17243b;font:15px Arial,sans-serif}header{padding:26px 32px;background:#14243d;color:white}h1{font-size:24px;margin:0 0 8px}header p{margin:0;opacity:.8}nav{padding:14px 32px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}button{padding:10px 16px;border:0;border-radius:7px;background:#2563eb;color:white;cursor:pointer}button.secondary{background:white;color:#14243d}main{padding:0 24px 24px}.sheet{background:white;border:1px solid #d9e2ef;border-radius:12px;padding:18px;overflow:auto}svg{display:block;width:100%;height:auto;min-width:700px}article{background:white;margin-top:22px;padding:24px;border-radius:12px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #dce3ec;padding:12px;text-align:left;vertical-align:top;white-space:pre-wrap}th{background:#f3f6fb}.note{white-space:pre-wrap;line-height:1.6}.legend{color:#078453;font-size:13px}footer{padding:18px 32px;font-size:12px;color:#53647a}@page{size:A3 landscape;margin:12mm}@media print{body{background:white}header{background:white;color:black;padding:0 0 8mm}nav,footer{display:none}main{padding:0}.sheet{border:0;padding:0;overflow:visible}svg{width:100%!important;min-width:0;max-height:240mm}article{break-before:page;padding:0}tr{break-inside:avoid}}
</style><header><h1>'''+esc(data['title'])+'''</h1><p>'''+esc(data.get('author',''))+'''</p></header>
<nav><button onclick="window.print()">Imprimir / salvar em PDF</button><button class="secondary" onclick="zoom(0.2)">Ampliar +</button><button class="secondary" onclick="zoom(-0.2)">Reduzir −</button><button class="secondary" onclick="scale=1;draw()">Ajustar</button><span>Arquivo independente • funciona sem internet</span></nav>
<main><section class="sheet">'''+svg(data)+'''</section><p class="legend">Verde: processos e conexões acrescentados na revisão.</p>
<article><h2>Detalhamento e observações</h2><p class="note">'''+esc(data.get('notes',''))+'''</p><table><thead><tr><th>Elemento</th><th>Detalhamento</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></article></main>
<footer>Exportado pelo DFD Studio • Diagrama de fluxo de dados</footer>
<script>let scale=1;function draw(){document.querySelector('svg').style.width=(scale*100)+'%'}function zoom(d){scale=Math.max(.4,Math.min(4,scale+d));draw()}</script></html>'''


def save_svg(path,data): Path(path).write_text(svg(data),encoding='utf-8')
def save_html(path,data): Path(path).write_text(html(data),encoding='utf-8')
