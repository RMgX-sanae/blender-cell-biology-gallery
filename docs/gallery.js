const plate = name => 'assets/plates/' + name + '.webp';
const pdb = id => ['RCSB PDB ' + id, 'https://www.rcsb.org/structure/' + id];
const skillRepo = 'https://github.com/RMgX-sanae/blender-cell-biology';
const galleryRepo = 'https://github.com/RMgX-sanae/blender-cell-biology-gallery';
const types = {
  model: { name: '互动模型', icon: 'cube' },
  atlas: { name: '结构图集', icon: 'photo' },
  film: { name: '机制动画', icon: 'movie' }
};
const works = {
  hemocyanin: {
    title: '血蓝蛋白', latin: 'Hemocyanin', type: 'model', kind: '分子装配', ref: 'PDB 6R83',
    summary: '十个亚基围成中空的桶。\n太平洋褶柔鱼靠它在血液中运送氧。',
    cut: 'hemocyanin-cut', widths:[590,969], cover: 'hemo-whole-s', alt: '青色分子桶的开口内，金色和珊瑚色功能单元交错排列。',
    note: '金色的 FU-g 和珊瑚色的 FU-d* 位于内圈。每个亚基保留八个已建模的功能单元，径向展开可以看清各自的形状。',
    sources: [pdb('6R83'), ['查看建模脚本',skillRepo+'/tree/main/examples/structure-and-function/01_hemocyanin']], model: 'hemocyanin.glb',
    direction: [.37,.83,.65],
    stills: [['hemo-whole','完整十聚体'],['hemo-exploded','十个亚基']],
    partLabel: '选择亚基', soloLabel: '单独观察亚基'
  },
  bench: {
    title: '超净工作台', latin: 'Clean bench', type: 'model', kind: '实验器械', ref: '垂直流工作台',
    summary: '移开顶罩和前窗，看看工作腔上方的送风机组与两层过滤部件。',
    cut: 'bench-cut', widths:[509,974], cover: 'bench-cut-s', alt: '浅色工作台由墨绿色机架支撑，前方玻璃窗内是不锈钢工作面。',
    note: '顶部的预滤网、送风机组和主过滤盒位于工作腔上方。通用机身和七组部件的拆解行程按教学展示设计。',
    sources: [['设备结构参考','https://www.labconco.com/product/purifier-vertical-clean-benches'],['建模脚本与 Blender 工程',galleryRepo+'/tree/main/examples/clean-bench']],
    model: 'clean-bench.glb', direction: [3.35,1.99,6.45],
    stills: [['bench-cut','整机'],['bench-exploded','七组部件']],partLabel: '选择部件', soloLabel: '单独观察部件'
  },
  axoneme: {
    title: '鞭毛轴丝', latin: 'Axoneme', type: 'atlas', kind: '分子结构', ref: 'PDB 8GLV',
    summary: '沿衣藻的一根双联微管，观察一个 96 nm 重复单元里的辐条与动力臂。',
    cut: 'axoneme-cut', widths:[700,1242], cover: 'axon-whole-s', alt: '双联微管上伸出青绿辐条，两侧分布金色和珊瑚色动力臂。',
    note: '衣藻轴丝的一根双联微管上，青绿辐条、珊瑚色外动力臂和金色内动力臂沿管壁排列。',
    sources:[pdb('8GLV')], views:[['axon-whole','整体排列','双联微管与附着的辐条、动力臂。'],['axon-end','微管端面','从端面看见大小不同的两个管腔。'],['axon-spokes','辐条底座','两根长辐条与一根较短的辐条残段留在微管壁上。']]
  },
  antenna: {
    title: '红藻藻胆体', latin: 'Phycobilisome', type: 'atlas', cover:'antenna-s',alt:'红藻捕光天线的粉色外围、蓝紫色中间层和青绿色核心。',
    note:'紫球藻的捕光天线由 706 个蛋白亚基组装。依次观察完整装配、显露的青绿色核心和一对邻近亚基结合的色素。',
    sources:[pdb('6KGX'),['查看建模脚本',skillRepo+'/tree/main/examples/three-scale-studies/01_phycobilisome']],views:[['antenna-whole','完整装配','红藻藻胆体的完整半椭球形装配。'],['antenna','显露核心','移开遮挡亚基后显露的青绿色捕光核心。'],['antenna-pair','色素结合','一对藻红蛋白亚基以及它们结合的五个色素。']]
  },
  vatpase:{
    title:'V 型质子泵',latin:'V-ATPase',type:'film',cover:'vatpase-poster-s',alt:'同一台 V 型质子泵的侧面与 c 环俯视图。',duration:'00:32',
    note:'左右镜头同步显示同一台泵的整体与 c 环。两轮教学循环展示质子从胞质侧进入、随环转动，再释放到囊泡腔。',
    sources:[pdb('6VQ6'),['查看动画工作流',skillRepo+'/blob/main/references/vatpase-loop.md']],poster:'vatpase-poster',file:'vatpase.mp4'
  },
  arp23:{
    title:'肌动蛋白分支',latin:'Arp2/3',type:'film',cover:'arp23-poster-s',alt:'肌动蛋白母丝旁的 Arp2/3 分支接头和正在形成的子丝。',duration:'00:25',
    note:'节选自 Arp2/3 机制影片的分支成核章节。七亚基复合物与母丝侧面相接，随后出现子丝的首批亚基。',
    sources:[pdb('7TPT'),['查看成片工作流',skillRepo+'/blob/main/references/portable-actin-films.md']],poster:'arp23-poster',file:'arp23.mp4',captions:'arp23.vtt'
  }
};
const featureOrder = ['hemocyanin','bench','axoneme'];
const catalogOrder = ['antenna','bench','axoneme','vatpase','hemocyanin','arp23'];
const $ = (selector, root = document) => root.querySelector(selector);
const icon = name => '<svg class="icon" aria-hidden="true"><use href="assets/icons.svg#' + name + '"></use></svg>';
const workDialog = $('#work-dialog');
const aboutDialog = $('#about-dialog');
const content = $('#sheet-content');
let featureIndex = 0;
let viewer = null;
let loading = null;
let revision = 0;

const motionButton = $('#motion-toggle');
const html = document.documentElement;
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
let motionPreference = true;
try { motionPreference = localStorage.getItem('microforma-motion') !== 'off'; } catch {}
let heroVisible = true, idleTimer = 0, keyboardInput = false, lastPointerTime = 0;
const cueTimers = new WeakMap();
const motionOn = () => motionPreference && !reduceMotion.matches;
function scheduleIdle() {
  clearTimeout(idleTimer);
  html.classList.remove('art-idle');
  if (!motionOn() || !heroVisible || document.hidden || workDialog.open || aboutDialog.open) return;
  idleTimer = setTimeout(() => html.classList.add('art-idle'), 2100);
}
function updateMotion() {
  const enabled = motionOn();
  html.dataset.motion = enabled ? 'on' : 'off';
  motionButton.setAttribute('aria-pressed',String(enabled));
  motionButton.disabled = reduceMotion.matches;
  const label = reduceMotion.matches ? '已按系统偏好减少动效' : enabled ? '暂停几何动效' : '开启几何动效';
  motionButton.setAttribute('aria-label',label); motionButton.title=label;
  scheduleIdle();
}
function cue(element, name, duration) {
  if (!motionOn() || keyboardInput) return;
  clearTimeout(cueTimers.get(element));
  element.classList.remove(name);
  void element.offsetWidth;
  element.classList.add(name);
  cueTimers.set(element,setTimeout(()=>element.classList.remove(name),duration));
}
motionButton.addEventListener('click',()=>{
  motionPreference=!motionPreference;
  try {localStorage.setItem('microforma-motion',motionPreference?'on':'off');} catch {}
  updateMotion();
});
reduceMotion.addEventListener('change',updateMotion);
document.addEventListener('pointerdown',()=>{keyboardInput=false;scheduleIdle();},{passive:true});
document.addEventListener('pointermove',()=>{
  const now=performance.now();
  if(now-lastPointerTime>180){lastPointerTime=now;scheduleIdle();}
},{passive:true});
document.addEventListener('keydown',()=>{keyboardInput=true;scheduleIdle();});
document.addEventListener('visibilitychange',scheduleIdle);
for(const d of [workDialog,aboutDialog]) d.addEventListener('close',scheduleIdle);
new IntersectionObserver(entries=>{heroVisible=entries[0].isIntersecting;scheduleIdle();}).observe($('.hero'));
updateMotion();
cue(html,'page-enter',800);

function setFeature(step) {
  featureIndex = (featureIndex + step + featureOrder.length) % featureOrder.length;
  const id = featureOrder[featureIndex], work = works[id];
  $('.hero-layout').dataset.feature = id;
  $('#feature-kind').textContent = work.kind;
  $('#feature-title').textContent = work.title;
  $('#feature-latin').textContent = work.latin;
  $('#feature-summary').textContent = work.summary;
  $('#feature-ref').textContent = work.ref;
  $('#feature-current').textContent = String(featureIndex + 1).padStart(2, '0');
  const image = $('#feature-image');
  image.srcset = plate(work.cut+'-s') + ' ' + work.widths[0] + 'w, ' + plate(work.cut) + ' ' + work.widths[1] + 'w';
  image.src = plate(work.cut);
  $('#feature-open span').textContent = work.type === 'model' ? '拆解模型' : '查看图集';
  $('#feature-open use').setAttribute('href','assets/icons.svg#'+(work.type === 'model' ? 'stack-2' : 'photo'));
  $('#feature-status').textContent = '精选展品 ' + (featureIndex+1) + '，' + work.title;
  cue($('.hero-layout'),'feature-change',745);
}
$('#feature-prev').addEventListener('click', () => setFeature(-1));
$('#feature-next').addEventListener('click', () => setFeature(1));
$('#feature-open').addEventListener('click', () => openWork(featureOrder[featureIndex]));

function renderCatalog(filter = 'all') {
  const grid = $('#work-grid');
  const ids = catalogOrder.filter(id => filter === 'all' || works[id].type === filter);
  grid.replaceChildren(...ids.map(id => {
    const w = works[id], type = types[w.type];
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'work-card'; button.dataset.id = id;
    button.setAttribute('aria-label', '打开' + w.title + '，' + type.name);
    button.innerHTML = '<span class="card-image"><img loading="lazy" decoding="async" src="' + plate(w.cover) + '" alt="' + w.alt + '"></span><span class="card-row"><span class="card-title">' + w.title + '</span><span class="card-type">' + icon(type.icon) + (w.duration || type.name) + '</span></span>';
    button.addEventListener('click', () => openWork(id));
    return button;
  }));
  $('#filter-status').textContent = '显示 ' + ids.length + ' 件作品';
}
document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-filter]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
  renderCatalog(button.dataset.filter);
}));
renderCatalog();

function endWork() {
  revision++;
  loading?.abort(); loading = null;
  viewer?.destroy(); viewer = null;
  const video = $('video', content);
  if (video) { video.pause(); video.removeAttribute('src'); video.load(); }
  content.replaceChildren();
}
function workNotes(w) {
  const links = w.sources.map(([name, url]) => '<a class="source-link" rel="noopener noreferrer" target="_blank" href="' + url + '">' + name + ' ↗</a>');
  return '<p class="sheet-note">' + w.note + '</p><div class="source-row">' + links.join('') + '</div>';
}

function stillTabs(views, image, container) {
  const buttons = views.map(([file, name, alt], index) => {
    const b = document.createElement('button');
    b.type = 'button'; b.textContent = name; b.setAttribute('aria-pressed', String(index === 0));
    b.addEventListener('click', () => {
      image.src = plate(file);
      image.alt = alt || name;
      buttons.forEach(other => other.setAttribute('aria-pressed', String(other === b)));
    });
    return b;
  });
  container.replaceChildren(...buttons);
}
function showAtlas(w) {
  content.innerHTML = '<figure class="sheet-stage atlas-stage"><img src="' + plate(w.views[0][0]) + '" alt="' + w.views[0][2] + '"></figure><div class="still-tabs" role="group" aria-label="展品视图"></div>' + workNotes(w);
  stillTabs(w.views, $('img',content), $('.still-tabs',content));
}
function showFilm(id, w) {
  const track = w.captions ? '<track default kind="captions" srclang="zh" label="中文要点" src="assets/films/' + w.captions + '">' : '';
  content.innerHTML = '<div class="sheet-stage film-stage"><video controls playsinline preload="metadata" aria-label="' + w.title + '" poster="' + plate(w.poster) + '" src="assets/films/' + w.file + '">' + track + '</video></div><div class="still-tabs" role="group" aria-label="选择短片"></div>' + workNotes(w);
  for(const key of ['vatpase','arp23']){
    const film = works[key], b = document.createElement('button');
    b.type='button'; b.textContent=film.title + '  ' + film.duration; b.setAttribute('aria-pressed',String(key===id));
    b.addEventListener('click', () => { if(key!==id){ openWork(key); $('.still-tabs [aria-pressed="true"]',content).focus(); } });
    $('.still-tabs',content).append(b);
  }
}
async function showModel(id, w, current, signal) {
  content.innerHTML = '<div class="model-layout"><div class="sheet-stage model-stage" aria-busy="true"><img class="model-preview" src="' + plate(w.cut) + '" alt="' + w.alt + '"><span class="stage-status" role="status">正在载入三维模型…</span></div><div class="control-panel"><label class="control-heading" for="explode">拆解程度<output id="amount" for="explode">0%</output></label><input id="explode" type="range" min="0" max="100" step="1" value="0" disabled><div class="tool-row"><button class="outline-action" id="toggle-explode" type="button" disabled>展开全部</button><button class="tool-action" id="reset-view" type="button" disabled aria-label="复位视角" title="复位视角">' + icon('rotate-2') + '</button></div><div class="part-control"><label for="part">' + w.partLabel + '</label><select id="part" disabled><option value="">全部</option></select><button type="button" id="solo" class="outline-action" aria-pressed="false" disabled>' + w.soloLabel + '</button></div><p class="controls-tip">拖动旋转，双指或滚轮缩放。点选模型可定位部件。</p></div></div>' + workNotes(w);
  const stage = $('.model-stage',content), panel = $('.control-panel',content), preview = $('.model-preview',stage), status = $('.stage-status',stage);
  const slider=$('#explode'), toggle=$('#toggle-explode'), reset=$('#reset-view'), select=$('#part'), solo=$('#solo');
  function syncSelection(name) {
    select.value=name; solo.disabled=!name; slider.disabled=false; toggle.disabled=false;
    solo.setAttribute('aria-pressed','false'); solo.textContent=w.soloLabel;
  }
  try {
    const {createViewer} = await import('./viewer.bundle.js');
    if (signal.aborted) return;
    const api = await createViewer(stage, id, w, signal, syncSelection);
    if (signal.aborted || current!==revision) { api?.destroy(); return; }
    viewer=api;
    for(const p of api.parts) select.add(new Option(p.label,p.name));
    preview.hidden=true; status.hidden=true; stage.setAttribute('aria-busy','false');
    if(motionOn()&&!keyboardInput)stage.classList.add('is-ready');
    [slider,toggle,reset,select].forEach(e=>e.disabled=false);
    let animation=0, destination=null;
    function stopSpread() { cancelAnimationFrame(animation); animation=0;destination=null; }
    signal.addEventListener('abort',stopSpread,{once:true});
    function setSpread(value) {
      const percent=Math.round(value);
      slider.value=percent; $('#amount').value=percent+'%';
      toggle.textContent=percent===100 || destination===100?'重新合拢':'展开全部';
      api.setExplosion(value/100);
    }
    slider.addEventListener('input',()=>{stopSpread();setSpread(Number(slider.value));});
    toggle.addEventListener('click',()=>{
      const from=Number(slider.value), to=(destination===100 || (destination===null && from===100))?0:100;
      stopSpread();
      if(!motionOn()||keyboardInput){setSpread(to);return;}
      destination=to;
      const start=performance.now(), duration=220+Math.abs(to-from)*4;
      function tick(now) {
        const t=Math.min(1,(now-start)/duration);
        const eased=t*t*(3-2*t);
        if(t===1 || !motionOn()){stopSpread();setSpread(to);return;}
        setSpread(from+(to-from)*eased);
        animation=requestAnimationFrame(tick);
      }
      animation=requestAnimationFrame(tick);
    });
    reset.addEventListener('click',()=>api.reset());
    select.addEventListener('change',()=>{api.select(select.value);syncSelection(select.value);});
    solo.addEventListener('click',()=>{
      const active=solo.getAttribute('aria-pressed')!=='true';
      stopSpread();toggle.textContent=Number(slider.value)===100?'重新合拢':'展开全部';
      api.isolate(active);slider.disabled=active;toggle.disabled=active;solo.setAttribute('aria-pressed',String(active));
      solo.textContent=active?'显示全部':w.soloLabel;
    });
  } catch(error) {
    if(signal.aborted||current!==revision) return;
    stage.classList.add('is-still');stage.setAttribute('aria-busy','false');
    status.textContent='当前设备显示静帧'; preview.src=plate(w.stills[0][0]); preview.alt=w.stills[0][1];
    panel.innerHTML='<p class="control-heading">切换展品视图</p><div class="still-tabs fallback-panel" role="group" aria-label="结构状态"></div>';
    stillTabs(w.stills,preview,$('.still-tabs',panel));
    console.warn('三维视图暂不可用',error);
  }
}
function openWork(id) {
  const w=works[id];
  endWork();
  $('#sheet-kind').textContent=types[w.type].name + ' / ' + w.latin;
  $('#sheet-title').textContent=w.title;
  if(!workDialog.open) workDialog.showModal();
  scheduleIdle();cue(workDialog,'sheet-open',530);
  workDialog.scrollTop=0;
  if(w.type==='atlas') showAtlas(w);
  if(w.type==='film') showFilm(id,w);
  if(w.type==='model'){loading=new AbortController();showModel(id,w,revision,loading.signal);}
}
document.querySelectorAll('[data-about]').forEach(b=>b.addEventListener('click',()=>{aboutDialog.showModal();scheduleIdle();cue(aboutDialog,'sheet-open',320);}));
$('[data-film]').addEventListener('click',()=>openWork('vatpase'));
$('#about-catalog').addEventListener('click',()=>aboutDialog.close());
for(const dialog of [workDialog,aboutDialog]){
  $('.close-sheet',dialog).addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{
    if(e.target!==dialog)return;
    const r=dialog.getBoundingClientRect();
    if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();
  });
}
workDialog.addEventListener('close',()=>{if(!workDialog.open)endWork();});
