/* DFD Studio — núcleo gráfico em SVG puro, mantendo o schema .dfd.json v1.
 * Interface desacoplada: os únicos endpoints estão em apps/dfd/api.py.
 */
(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const svgNS = 'http://www.w3.org/2000/svg';
  const deep = value => JSON.parse(JSON.stringify(value));
  const uid = () => (globalThis.crypto && crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}${Math.random()}`).replace(/-/g, '').slice(0, 12);
  const safe = value => String(value ?? '').replace(/[&<>"']/g, v => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[v]));
  const blank = () => ({format:'dfd-studio',version:1,title:'Novo diagrama de fluxo de dados',author:'',notes:'',nodes:[],edges:[]});
  let diagram = blank(), selected = null, mode = 'select', connectionFrom = null, review = false;
  let transform = {x:0,y:0,k:1}, gesture = null, projectName = 'modulo_01', dirty = false;
  let undo = [], redo = [], autosaveTimer = null;
  const stage = $('#stage'), sheet = $('#sheet'), world = $('#world');
  const points = {left: n => [n.x,n.y+n.h/2],right:n=>[n.x+n.w,n.y+n.h/2],top:n=>[n.x+n.w/2,n.y],bottom:n=>[n.x+n.w/2,n.y+n.h]};

  function svg(type,attrs={},text) {
    const el = document.createElementNS(svgNS,type);
    Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k,v));
    if (text != null) el.textContent=text;
    return el;
  }
  function center(n){return [n.x+n.w/2,n.y+n.h/2]}
  function port(n,where,toward){
    if (!where || where==='auto') {
      const c=center(n),dx=toward[0]-c[0],dy=toward[1]-c[1];
      where = Math.abs(dx)/n.w >= Math.abs(dy)/n.h ? (dx>=0?'right':'left') : (dy>=0?'bottom':'top');
    }
    return points[where](n);
  }
  function edgePoints(e){
    const a=diagram.nodes.find(x=>x.id===e.source),b=diagram.nodes.find(x=>x.id===e.target);
    if(!a||!b)return [];
    const bends=e.bends||[];
    const start=port(a,e.source_port,bends.length?bends[0]:center(b));
    const end=port(b,e.target_port,bends.length?bends.at(-1):center(a));
    let path;
    if(bends.length)path=[start,...bends,end];
    else if(e.route==='direct')path=[start,end];
    else if(e.route==='vertical'){const my=(start[1]+end[1])/2;path=[start,[start[0],my],[end[0],my],end]}
    else {const mx=(start[0]+end[0])/2;path=[start,[mx,start[1]],[mx,end[1]],end]}
    return path.filter((p,i)=>!i||p[0]!==path[i-1][0]||p[1]!==path[i-1][1]);
  }
  function middle(path){
    let total=0;for(let i=1;i<path.length;i++)total+=Math.hypot(path[i][0]-path[i-1][0],path[i][1]-path[i-1][1]);
    let half=total/2;
    for(let i=1;i<path.length;i++){const [a,b]=[path[i-1],path[i]],d=Math.hypot(b[0]-a[0],b[1]-a[1]);if(half<=d&&d)return [a[0]+(b[0]-a[0])*half/d,a[1]+(b[1]-a[1])*half/d];half-=d}
    return path[Math.floor(path.length/2)]||[0,0];
  }
  function wrap(text,width=22){
    const words=String(text||'').split(/(\s+)/), lines=[''];
    words.forEach(w=>{if(w.includes('\n')){w.split('\n').forEach((v,i)=>{if(i)lines.push('');if(lines.at(-1).length+v.length>width&&lines.at(-1).trim())lines.push('');lines[lines.length-1]+=v});return}
      if((lines.at(-1)+w).trim().length>width&&lines.at(-1).trim())lines.push('');lines[lines.length-1]+=w;
    });return lines.flatMap(l=>l.length>width?l.match(new RegExp(`.{1,${width}}`,'g')):[l]).slice(0,10);
  }
  function textLines(parent,at,text,size=13,color='#d9e7f1',width=22){
    const lines=wrap(text,width),t=svg('text',{'text-anchor':'middle',fill:color,'font-size':size,'font-weight':500});
    const h=size*1.35;lines.forEach((row,i)=>t.append(svg('tspan',{x:at[0],y:at[1]+(i-(lines.length-1)/2)*h+size*.34},row)));
    parent.append(t);return t;
  }
  function drawEdge(e){
    const path=edgePoints(e);if(path.length<2)return;
    const isSelected=selected?.type==='edge'&&selected.id===e.id;
    const c=(review&&((diagram.nodes.find(n=>n.id===e.source)?.code==='1.8'&&diagram.nodes.find(n=>n.id===e.target)?.code==='1.11')||(diagram.nodes.find(n=>n.id===e.source)?.code==='1.13'&&diagram.nodes.find(n=>n.id===e.target)?.code==='1.04'))) ? '#4edea3' : (e.color||'#38bdf8');
    const g=svg('g',{'class':`connection ${isSelected?'selected':''}`,'data-edge':e.id});
    const pts=path.map(p=>p.join(',')).join(' ');
    g.append(svg('polyline',{points:pts,fill:'none',stroke:c,'stroke-width':2.2,'stroke-linecap':'round','stroke-linejoin':'round','class':'edge-line'}));
    g.append(svg('polyline',{points:pts,'class':'edge-hit'}));
    const end=path.at(-1),prev=path.at(-2),angle=Math.atan2(end[1]-prev[1],end[0]-prev[0]);
    const head=[end,[end[0]-11*Math.cos(angle)+5*Math.sin(angle),end[1]-11*Math.sin(angle)-5*Math.cos(angle)],[end[0]-11*Math.cos(angle)-5*Math.sin(angle),end[1]-11*Math.sin(angle)+5*Math.cos(angle)]];
    g.append(svg('polygon',{points:head.map(p=>p.join(',')).join(' '),fill:c}));
    if(e.text){const m=middle(path),x=m[0]+(e.label_dx||0),y=m[1]+(e.label_dy||-12),rows=wrap(e.text,23),w=Math.max(...rows.map(r=>r.length),4)*7+20,h=rows.length*16+13;
      g.append(svg('rect',{x:x-w/2,y:y-h/2,width:w,height:h,rx:4,fill:'#203344',stroke:isSelected?'#00e2eb':'#436074','stroke-width':1}));textLines(g,[x,y],e.text,11.5,'#d1ebf5',23);
    }
    $('#edges').append(g);
  }
  function drawNode(n){
    const active=selected?.type==='node'&&selected.id===n.id;
    const color=(review&&['1.15','1.16'].includes(n.code))?'#4edea3':n.color;
    const g=svg('g',{'data-node':n.id,'class':`node ${active?'selected':''}`});
    if(n.kind==='store'){
      g.append(svg('rect',{'class':'node-body',x:n.x,y:n.y,width:n.w,height:n.h,rx:0,fill:'#17312d',stroke:color,'stroke-width':2}));
      g.append(svg('line',{x1:n.x+56,y1:n.y,x2:n.x+56,y2:n.y+n.h,stroke:color,'stroke-width':1.6}));
      textLines(g,[n.x+27,n.y+n.h/2],n.code||'D',11,color,6);
      textLines(g,[n.x+56+(n.w-56)/2,n.y+n.h/2],n.text,12,'#e0efec',Math.max(6,Math.floor((n.w-68)/7)));
    } else {
      g.append(svg('rect',{'class':'node-body',x:n.x,y:n.y,width:n.w,height:n.h,rx:n.kind==='process'?12: n.kind==='note'?5:0,
         fill:n.kind==='entity'?'#1c2a3c':n.kind==='note'?'#383327':'#19323c',stroke:color,'stroke-width':2,'stroke-dasharray':n.kind==='note'?'6 4':'none'}));
      if(n.code){g.append(svg('line',{x1:n.x,y1:n.y+28,x2:n.x+n.w,y2:n.y+28,stroke:color,'stroke-width':1,opacity:.85}));
        textLines(g,[n.x+n.w/2,n.y+14],n.code,11.5,color,22)}
      const offset=n.code?28:0;
      textLines(g,[n.x+n.w/2,n.y+offset+(n.h-offset)/2],n.text,12.5,'#e4f1f5',Math.max(8,Math.floor((n.w-22)/7.5)));
    }
    $('#nodes').append(g);
    if(active){const c=center(n);$('#handles').append(svg('rect',{'class':'resize-handle',x:n.x+n.w-5,y:n.y+n.h-5,width:10,height:10,rx:2,'data-resize':n.id}));
      const sites={left:[n.x,c[1]],right:[n.x+n.w,c[1]],top:[c[0],n.y],bottom:[c[0],n.y+n.h]};
      Object.entries(sites).forEach(([side,p])=>$('#handles').append(svg('circle',{cx:p[0],cy:p[1],r:5,'class':'connector-handle','data-port':side,'data-owner':n.id})));
    }
  }
  function draw(){
    world.setAttribute('transform',`translate(${transform.x} ${transform.y}) scale(${transform.k})`);
    $('#edges').replaceChildren();$('#nodes').replaceChildren();$('#handles').replaceChildren();
    diagram.edges.forEach(drawEdge);diagram.nodes.forEach(drawNode);
    $('#count').textContent=`${diagram.nodes.length} elementos · ${diagram.edges.length} fluxos`;
    $('#zoomValue').textContent=Math.round(transform.k*100)+'%';
    $('#heading').textContent=diagram.title;
    $('#dirty').textContent=dirty?'● Rascunho alterado':'✓ Salvo';
    drawMini();
  }
  function worldPoint(clientX,clientY){
    const p=sheet.createSVGPoint();p.x=clientX;p.y=clientY;
    const matrix=world.getScreenCTM();if(!matrix)return [0,0];const z=p.matrixTransform(matrix.inverse());return [z.x,z.y];
  }
  function zoomAt(factor,clientX=stage.getBoundingClientRect().left+stage.clientWidth/2,clientY=stage.getBoundingClientRect().top+stage.clientHeight/2){
    const before=worldPoint(clientX,clientY),k=Math.max(.15,Math.min(3.5,transform.k*factor));
    const rect=stage.getBoundingClientRect();transform.k=k;transform.x=clientX-rect.left-before[0]*k;transform.y=clientY-rect.top-before[1]*k;draw();
  }
  function fit(){
    if(!diagram.nodes.length){transform={x:stage.clientWidth/2-150,y:stage.clientHeight/2-90,k:1};draw();return}
    const a=diagram.nodes,minX=Math.min(...a.map(n=>n.x))-95,minY=Math.min(...a.map(n=>n.y))-90,maxX=Math.max(...a.map(n=>n.x+n.w))+95,maxY=Math.max(...a.map(n=>n.y+n.h))+90;
    const k=Math.max(.15,Math.min(1.3,Math.min(stage.clientWidth/(maxX-minX),stage.clientHeight/(maxY-minY))));
    transform={k,x:(stage.clientWidth-(maxX-minX)*k)/2-minX*k,y:(stage.clientHeight-(maxY-minY)*k)/2-minY*k};draw();
  }
  function drawMini(){
    const mini=$('#mini');mini.replaceChildren();if(!diagram.nodes.length)return;
    const minX=Math.min(...diagram.nodes.map(n=>n.x))-45,minY=Math.min(...diagram.nodes.map(n=>n.y))-45,maxX=Math.max(...diagram.nodes.map(n=>n.x+n.w))+45,maxY=Math.max(...diagram.nodes.map(n=>n.y+n.h))+45;
    const width=maxX-minX,height=maxY-minY,s=Math.min(208/width,106/height),ox=(220-width*s)/2,oy=(124-height*s)/2;
    const xx=x=>ox+(x-minX)*s,yy=y=>oy+(y-minY)*s;
    diagram.edges.forEach(e=>{const p=edgePoints(e);if(p.length>1)mini.append(svg('polyline',{points:p.map(a=>`${xx(a[0])},${yy(a[1])}`).join(' '),fill:'none',stroke:'#4a8995','stroke-width':1}))});
    diagram.nodes.forEach(n=>mini.append(svg('rect',{x:xx(n.x),y:yy(n.y),width:Math.max(2,n.w*s),height:Math.max(2,n.h*s),rx:2,fill:n.kind==='store'?'#4edea3':'#40aabd',opacity:.85})));
    const visible={x:-transform.x/transform.k,y:-transform.y/transform.k,w:stage.clientWidth/transform.k,h:stage.clientHeight/transform.k};
    mini.append(svg('rect',{x:xx(visible.x),y:yy(visible.y),width:visible.w*s,height:visible.h*s,fill:'#00e2eb12',stroke:'#00e2eb','stroke-width':1.5}));
  }
  function note(message,error=false){const toast=$('#toast');toast.textContent=message;toast.style.display='block';toast.style.background=error?'#6a2933':'#254239';clearTimeout(toast.timer);toast.timer=setTimeout(()=>toast.style.display='none',4200)}
  function remember(){undo.push(JSON.stringify(diagram));if(undo.length>60)undo.shift();redo=[]}
  function mark(){dirty=true;clearTimeout(autosaveTimer);autosaveTimer=setTimeout(()=>{try{localStorage.setItem('dfd-studio-draft',JSON.stringify({diagram,projectName}))}catch(_){/* navegador restrito */}},300);draw();renderLayers()}
  function replaceData(value,name){
    validate(value);diagram=deep(value);projectName=name||'diagrama';selected=null;connectionFrom=null;undo=[];redo=[];dirty=false;
    draw();renderProperties();renderLayers();requestAnimationFrame(fit);
  }
  function validate(d){
    if(!d||d.format!=='dfd-studio'||d.version!==1||!Array.isArray(d.nodes)||!Array.isArray(d.edges))throw Error('Arquivo incompatível: esperado DFD Studio JSON v1.');
    if(d.nodes.length>2000||d.edges.length>5000)throw Error('Projeto excede o limite de elementos.');
    const ids=new Set();for(const n of d.nodes){if(!['process','entity','store','note'].includes(n.kind)||!n.id||ids.has(n.id))throw Error('Elemento inválido ou ID duplicado.');ids.add(n.id);for(const key of ['x','y','w','h'])if(!Number.isFinite(n[key]))throw Error('Posição inválida.');if(n.w<80||n.h<50)throw Error('Elemento menor que o mínimo permitido.')}
    const eid=new Set();for(const e of d.edges){if(!e.id||eid.has(e.id)||!ids.has(e.source)||!ids.has(e.target))throw Error('Conexão inválida.');eid.add(e.id)}
  }
  function select(type,id){selected=type?{type,id}:null;draw();renderProperties();renderLayers()}
  function addNode(kind,x,y){
    remember();const suffix=diagram.nodes.filter(n=>n.kind===kind).length+1;
    const labels={process:'Novo processo',entity:'Nova entidade',store:'Novo depósito',note:'Escreva uma observação'};
    const w=kind==='store'?200:kind==='note'?220:180,h=kind==='note'?76:96;
    const node={id:uid(),kind,code:kind==='process'?`1.${suffix}`:kind==='store'?`D-${String(suffix).padStart(2,'0')}`:'',text:labels[kind],x:Math.round(x),y:Math.round(y),w,h,color:kind==='store'?'#4edea3':kind==='note'?'#f1ca8b':'#00dbe9',details:''};
    diagram.nodes.push(node);selected={type:'node',id:node.id};mark();renderProperties();return node;
  }
  function addEdge(a,b,sourcePort='auto'){
    if(a===b){note('Para conectar um processo a ele mesmo, use outro elemento auxiliar.',true);return}
    remember();const e={id:uid(),source:a,target:b,text:'Novo fluxo de dados',color:'#38bdf8',source_port:sourcePort,target_port:'auto',route:'horizontal',bends:[],label_dx:0,label_dy:-12,details:''};
    diagram.edges.push(e);selected={type:'edge',id:e.id};connectionFrom=null;mark();renderProperties();note('Fluxo criado. Edite o nome na lateral direita.');
  }
  function removeSelected(){if(!selected)return;remember();if(selected.type==='node'){diagram.edges=diagram.edges.filter(e=>e.source!==selected.id&&e.target!==selected.id);diagram.nodes=diagram.nodes.filter(n=>n.id!==selected.id)}else diagram.edges=diagram.edges.filter(e=>e.id!==selected.id);selected=null;mark();renderProperties()}
  function setMode(value){mode=value;connectionFrom=null;stage.dataset.mode=value;$$('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===value));$('#hint').textContent={select:'Arraste para mover; alças para redimensionar; roda do mouse para ampliar.',connect:'Clique na origem e depois no destino para criar uma seta.',pan:'Arraste o fundo para navegar pelo diagrama.'}[value]}
  const $$=selector=>Array.from(document.querySelectorAll(selector));
  function onDown(e){
    if(e.button!==0)return;
    stage.focus({preventScroll:true});
    const portHandle=e.target.closest('[data-port]'),resize=e.target.closest('[data-resize]'),nodeEl=e.target.closest('[data-node]'),edgeEl=e.target.closest('[data-edge]');
    const [wx,wy]=worldPoint(e.clientX,e.clientY);
    if(portHandle){const id=portHandle.dataset.owner;connectionFrom={id,port:portHandle.dataset.port};setMode('connect');connectionFrom={id,port:portHandle.dataset.port};note('Agora clique no elemento de destino.');return}
    if(mode==='connect'){
      if(nodeEl){const id=nodeEl.dataset.node;if(!connectionFrom){connectionFrom={id,port:'auto'};select('node',id);note('Selecione o destino do fluxo.')}else addEdge(connectionFrom.id,id,connectionFrom.port)}
      else {connectionFrom=null;select(null,null)}return;
    }
    if(resize){const n=diagram.nodes.find(n=>n.id===resize.dataset.resize);if(!n)return;remember();gesture={type:'resize',node:n,wx,wy,w:n.w,h:n.h,moved:false};}
    else if(nodeEl&&mode==='select'){
      const n=diagram.nodes.find(n=>n.id===nodeEl.dataset.node);select('node',n.id);remember();gesture={type:'move',node:n,wx,wy,x:n.x,y:n.y,moved:false};
    }else if(edgeEl&&mode==='select'){select('edge',edgeEl.dataset.edge);return}
    else{if(mode!=='pan')select(null,null);gesture={type:'pan',cx:e.clientX,cy:e.clientY,x:transform.x,y:transform.y};stage.dataset.panning='true'}
    sheet.setPointerCapture(e.pointerId);e.preventDefault();
  }
  function onMove(e){
    if(!gesture)return;
    if(gesture.type==='pan'){transform.x=gesture.x+e.clientX-gesture.cx;transform.y=gesture.y+e.clientY-gesture.cy;draw();return}
    const [wx,wy]=worldPoint(e.clientX,e.clientY),deltaX=wx-gesture.wx,deltaY=wy-gesture.wy;
    const snap=(n)=>e.altKey?n:Math.round(n/11)*11;
    if(gesture.type==='move'){gesture.node.x=snap(gesture.x+deltaX);gesture.node.y=snap(gesture.y+deltaY)}
    else{gesture.node.w=Math.max(80,snap(gesture.w+deltaX));gesture.node.h=Math.max(50,snap(gesture.h+deltaY))}
    gesture.moved=true;draw();
  }
  function onUp(){
    if(!gesture)return;const g=gesture;gesture=null;stage.dataset.panning='false';
    if(g.moved)mark();else if(g.type==='resize'||g.type==='move'){undo.pop()}
  }
  sheet.addEventListener('pointerdown',onDown);sheet.addEventListener('pointermove',onMove);sheet.addEventListener('pointerup',onUp);sheet.addEventListener('pointercancel',onUp);
  sheet.addEventListener('wheel',e=>{e.preventDefault();zoomAt(e.deltaY<0?1.1:1/1.1,e.clientX,e.clientY)},{passive:false});
  stage.addEventListener('dragover',e=>{e.preventDefault();e.dataTransfer.dropEffect='copy'});
  stage.addEventListener('drop',e=>{e.preventDefault();const kind=e.dataTransfer.getData('application/x-dfd-kind');if(['process','entity','store','note'].includes(kind)){const p=worldPoint(e.clientX,e.clientY);addNode(kind,p[0]-90,p[1]-48)}});
  $$('.shape').forEach(button=>{button.addEventListener('dragstart',e=>{e.dataTransfer.setData('application/x-dfd-kind',button.dataset.kind);e.dataTransfer.effectAllowed='copy'});button.addEventListener('click',()=>{const r=stage.getBoundingClientRect(),p=worldPoint(r.left+r.width/2,r.top+r.height/2);addNode(button.dataset.kind,p[0]-80+Math.random()*24,p[1]-45+Math.random()*24)})});
  $$('[data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode)));
  $('#zoomIn').onclick=()=>zoomAt(1.16);$('#zoomOut').onclick=()=>zoomAt(1/1.16);$('#fit').onclick=fit;
  $('#btnReview').onclick=()=>{review=!review;$('#btnReview').textContent=review?'Mostrar todas as cores':'Destacar alterações';draw()};
  $('#toggleMini').onclick=()=>{$('#mini').classList.toggle('hidden');$('#toggleMini').textContent=$('#mini').classList.contains('hidden')?'+':'−'};
  $$('[data-tab]').forEach(tab=>tab.addEventListener('click',()=>{const id=tab.dataset.tab;$$('[data-tab]').forEach(t=>t.classList.toggle('active',t===tab));['nodes','layers','projects'].forEach(name=>$('#tab-'+name).classList.toggle('hidden',name!==id));if(id==='projects')refreshProjects();if(id==='layers')renderLayers()}));
  function field(name,value,type='text',options=[]) {
    const label=safe(name), val=safe(value);
    let input;
    if(type==='textarea')input=`<textarea data-field="${label}" rows="4">${val}</textarea>`;
    else if(type==='select')input=`<select data-field="${label}">${options.map(o=>`<option value="${safe(o[0])}" ${o[0]===value?'selected':''}>${safe(o[1])}</option>`).join('')}</select>`;
    else input=`<input data-field="${label}" type="${type}" ${type==='number'?'step="1"':''} value="${val}">`;
    return `<div class="field"><label>${label}</label>${input}</div>`;
  }
  function renderProperties(){
    const host=$('#properties');let obj=selected?.type==='node'?diagram.nodes.find(n=>n.id===selected.id):selected?.type==='edge'?diagram.edges.find(e=>e.id===selected.id):diagram;
    $('#propTitle').textContent=selected?.type==='node'?'Elemento selecionado':selected?.type==='edge'?'Fluxo selecionado':'Diagrama';
    if(!obj){selected=null;obj=diagram}
    if(!selected){host.innerHTML='<p class="inline-note">Metadados gerais e instruções que acompanham a entrega do trabalho.</p>'+field('Título',obj.title)+field('Autor',obj.author)+field('Observações',obj.notes,'textarea')+'<p class="inline-note">Selecione um elemento do canvas para alterar suas propriedades.</p>';}
    else if(selected.type==='node'){
      host.innerHTML='<div class="sectiontitle">IDENTIFICAÇÃO</div>'+field('Código',obj.code)+field('Descrição',obj.text,'textarea')+field('Tipo',obj.kind,'select',[['process','Processo'],['entity','Entidade externa'],['store','Depósito de dados'],['note','Anotação']])+
       '<div class="sectiontitle">GEOMETRIA</div><div class="fields2">'+field('X',obj.x,'number')+field('Y',obj.y,'number')+field('Largura',obj.w,'number')+field('Altura',obj.h,'number')+'</div>'+field('Cor',obj.color,'color')+'<div class="sectiontitle">DOCUMENTAÇÃO</div>'+field('Detalhamento',obj.details,'textarea')+'<button class="danger" id="remove">Excluir elemento</button>';
    }else{
      host.innerHTML='<div class="sectiontitle">FLUXO DE DADOS</div>'+field('Rótulo',obj.text,'textarea')+field('Cor',obj.color,'color')+field('Rota',obj.route,'select',[['horizontal','Ortogonal H'],['vertical','Ortogonal V'],['direct','Direta']])+field('Porta de origem',obj.source_port,'select',[['auto','Automática'],['left','Esquerda'],['right','Direita'],['top','Superior'],['bottom','Inferior']])+field('Porta de destino',obj.target_port,'select',[['auto','Automática'],['left','Esquerda'],['right','Direita'],['top','Superior'],['bottom','Inferior']])+
       '<div class="fields2">'+field('Rótulo X',obj.label_dx,'number')+field('Rótulo Y',obj.label_dy,'number')+'</div>'+field('Detalhamento',obj.details,'textarea')+'<button class="danger" id="remove">Excluir conexão</button>';
    }
    host.querySelectorAll('[data-field]').forEach(input=>{
      let editing=false;input.addEventListener('focus',()=>{editing=false});
      input.addEventListener('input',()=>{
        const key=({'Título':'title','Autor':'author','Observações':'notes','Código':'code','Descrição':'text','Tipo':'kind','X':'x','Y':'y','Largura':'w','Altura':'h','Cor':'color','Detalhamento':'details','Rótulo':'text','Rota':'route','Porta de origem':'source_port','Porta de destino':'target_port','Rótulo X':'label_dx','Rótulo Y':'label_dy'})[input.dataset.field];
        if(!editing){remember();editing=true}
        if(input.type==='number'){const num=Number(input.value);if(!Number.isFinite(num))return;obj[key]=['w','h'].includes(key)?Math.max(key==='w'?80:50,num):num}else obj[key]=input.value;
        mark();
      });
      input.addEventListener('change',()=>{editing=false;if(input.dataset.field==='Tipo')renderProperties()});
    });
    const remove=$('#remove');if(remove)remove.onclick=removeSelected;
  }
  function renderLayers(){
    const list=$('#layerList');list.replaceChildren();
    for(const n of diagram.nodes){const b=document.createElement('button');b.className='layer-item'+(selected?.id===n.id?' active':'');
      b.append(document.createTextNode((n.kind==='store'?'▤ ':n.kind==='entity'?'□ ':n.kind==='note'?'☰ ':'▣ ')+(n.code?n.code+' · ':'')+n.text));
      b.title='Selecionar no diagrama';b.onclick=()=>{select('node',n.id);const r=stage.getBoundingClientRect();transform.x=r.width/2-(n.x+n.w/2)*transform.k;transform.y=r.height/2-(n.y+n.h/2)*transform.k;draw()};list.append(b)}
  }
  function stepBack(){if(!undo.length)return;redo.push(JSON.stringify(diagram));diagram=JSON.parse(undo.pop());selected=null;mark();renderProperties()}
  function stepAhead(){if(!redo.length)return;undo.push(JSON.stringify(diagram));diagram=JSON.parse(redo.pop());selected=null;mark();renderProperties()}
  $('#btnUndo').onclick=stepBack;$('#btnRedo').onclick=stepAhead;
  document.addEventListener('keydown',e=>{
    const input=e.target.matches('input,textarea,select')||e.target.isContentEditable;
    if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='s'){e.preventDefault();openSave();return}
    if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){if(input)return;e.preventDefault();stepBack();return}
    if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='y'){if(input)return;e.preventDefault();stepAhead();return}
    if(input)return;
    if(e.key==='Escape'){connectionFrom=null;setMode('select');select(null,null)}
    if(e.key==='Delete'||e.key==='Backspace'){removeSelected()}
    if(e.key.toLowerCase()==='v')setMode('select');
    if(e.key.toLowerCase()==='c')setMode('connect');
    if(e.key.toLowerCase()==='h')setMode('pan');
  });
  async function api(path,data){
    const opts=data?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}:{};
    const r=await fetch('/api/dfd/'+path,opts);if(!r.ok)throw Error('A API local do Vela não respondeu.');
    const d=await r.json();if(!d.ok)throw Error(d.error||'Operação não concluída.');return d.result;
  }
  const dialog=$('#dialog');
  function modal(title,body){$('#modalTitle').textContent=title;$('#modalBody').innerHTML=body;dialog.showModal()}
  function close(){dialog.close()}
  function inputName(){return `<div class="modalfield"><label>Nome do arquivo / projeto</label><input id="projectInput" value="${safe(projectName)}" spellcheck="false" maxlength="70"></div>`}
  function name(){return ($('#projectInput')?.value||projectName).trim().replace(/[^\w-]/g,'_').slice(0,70)||'diagrama'}
  function download(content,filename,mime){const blob=new Blob([content],{type:mime});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=filename;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000)}
  function openSave(){modal('Salvar projeto',inputName()+'<p class="inline-note">O projeto fica salvo em Documentos/DFD Studio/projetos e pode ser exportado em JSON.</p><div class="modalactions"><button type="button" class="secondary" id="saveJson">Baixar JSON</button><button type="button" class="primary" id="saveLocal">Salvar no computador</button></div>');
    $('#saveJson').onclick=()=>{const value=name();download(JSON.stringify(diagram,null,2),value+'.dfd.json','application/json');projectName=value;dirty=false;draw();close();note('JSON gerado para abrir novamente no DFD Studio.')};
    $('#saveLocal').onclick=async()=>{const value=name();try{validate(diagram);const ans=await api('projects/save',{name:value,diagram});projectName=value;dirty=false;draw();close();note('Projeto salvo em:\n'+ans.path)}catch(err){note(err.message+' Você pode usar Baixar JSON.',true)}};
  }
  function openExport(){modal('Exportar para o professor',inputName()+'<p class="inline-note">HTML é a entrega mais simples: abre em qualquer navegador e permite imprimir em PDF. SVG mantém linhas vetoriais e JSON permite continuar editando.</p><div class="export-grid"><button type="button" data-export="html"><span>▣</span>HTML</button><button type="button" data-export="svg"><span>◈</span>SVG</button><button type="button" data-export="json"><span>{ }</span>JSON</button></div>');
    $$('[data-export]').forEach(b=>b.onclick=()=>doExport(b.dataset.export));}
  async function doExport(type){let value=name(),text,filename,mime;
    try{validate(diagram);const ret=await api('export',{diagram,type,name:value});text=ret.content;filename=ret.name;mime=type==='html'?'text/html':type==='svg'?'image/svg+xml':'application/json';download(text,filename,mime);projectName=value;close();note('Arquivo pronto. Uma cópia também foi gravada em:\n'+ret.path)}
    catch(err){if(type==='json'){download(JSON.stringify(diagram,null,2),value+'.dfd.json','application/json');close();note('JSON baixado. API local indisponível.')}else note(err.message+' Execute o aplicativo com python manage.py runapp.',true)}
  }
  $('#filePicker').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{const d=JSON.parse(await file.text());replaceData(d,file.name.replace(/\.dfd\.json$|\.json$/i,''));mark();note('Projeto importado. Confira os elementos e salve.') }catch(err){note(err.message,true)}e.target.value=''});
  async function refreshProjects(){const list=$('#projectList');list.textContent='Carregando…';try{const projects=await api('projects');list.replaceChildren();if(!projects.length)list.textContent='Nenhum projeto salvo neste computador.';
    projects.forEach(p=>{const b=document.createElement('button');b.className='layer-item';b.textContent='▣ '+p.name;b.onclick=async()=>{if(dirty&&!confirm('Descartar mudanças ainda não salvas?'))return;try{replaceData(await api('projects/load',{name:p.name}),p.name);note('Projeto aberto: '+p.name)}catch(err){note(err.message,true)}};list.append(b)})}
    catch(err){list.textContent='API local indisponível. Abra um arquivo JSON.'}
  }
  $('#refreshProjects').onclick=refreshProjects;
  $$('[data-action]').forEach(b=>b.onclick=()=>{const a=b.dataset.action;if(a==='save')openSave();if(a==='exports')openExport();if(a==='open')$('#filePicker').click();if(a==='new'){
    if(dirty&&!confirm('Criar novo diagrama e descartar as alterações do rascunho?'))return;replaceData(blank(),'novo_diagrama');dirty=true;mark();
  }});
  window.addEventListener('resize',draw);
  async function init(){
    let draft; try{draft=localStorage.getItem('dfd-studio-draft')}catch(_){draft=null}
    if(draft){try{const d=JSON.parse(draft);validate(d.diagram);replaceData(d.diagram,d.projectName);dirty=true;draw();note('Rascunho local recuperado.')}catch(_){try{localStorage.removeItem('dfd-studio-draft')}catch(e){};draft=null}}
    if(!draft){try{const obj=await api('example');replaceData(obj,'modulo_01')}catch(_){if(window.DFD_SAMPLE)replaceData(window.DFD_SAMPLE,'modulo_01');else {replaceData(blank(),'novo_diagrama');note('A API está indisponível. Abra o app com Vela.',true)}}}
    setMode('select');
  }
  init();
})();
