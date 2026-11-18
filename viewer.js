import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

function meshCorners(objects) {
  const points = [];
  for (const object of objects) {
    object.updateWorldMatrix(true, true);
    object.traverse(mesh => {
      if (!mesh.isMesh) return;
      if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
      const { min, max } = mesh.geometry.boundingBox;
      for (const x of [min.x, max.x]) {
        for (const y of [min.y, max.y]) {
          for (const z of [min.z, max.z]) {
            points.push(new THREE.Vector3(x, y, z).applyMatrix4(mesh.matrixWorld));
          }
        }
      }
    });
  }
  return points;
}

function fitCamera(objects, direction, camera) {
  const points = meshCorners(objects);
  const center = new THREE.Box3().setFromPoints(points).getCenter(new THREE.Vector3());
  const right = new THREE.Vector3().crossVectors(camera.up, direction).normalize();
  const up = new THREE.Vector3().crossVectors(direction, right).normalize();
  const tanY = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  let distance = 0;
  for (const point of points) {
    point.sub(center);
    const depth = point.dot(direction);
    const x = Math.abs(point.dot(right)) / (camera.aspect * tanY);
    const y = Math.abs(point.dot(up)) / tanY;
    distance = Math.max(distance, depth + Math.max(x, y));
  }
  return { center, distance: distance * 1.08 };
}

export async function createViewer(stage, id, work, signal, onPick) {
  const response = await fetch('assets/models/' + work.model, { signal });
  if (!response.ok) throw new Error('模型文件无法载入');
  const gltf = await new GLTFLoader().parseAsync(await response.arrayBuffer(), '');
  const root = gltf.scene;
  const originals = new Set(), materials = new Set(), geometries = new Set();
  root.traverse(o => {
    if (!o.isMesh) return;
    geometries.add(o.geometry);
    for (const material of [].concat(o.material)) originals.add(material);
  });
  let renderer, controls, resizeObserver, environment;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, .01, 2000);
  const initial = new THREE.Vector3(...work.direction).normalize();
  const protein = id === 'hemocyanin';
  let parts = [], selected = '', isolated = false, lastDistance = 0, closed = false;

  function release() {
    if (closed) return;
    closed = true;
    resizeObserver?.disconnect();
    controls?.dispose();
    for (const g of geometries) g.dispose();
    for (const m of materials) m.dispose();
    for (const m of originals) m.dispose();
    environment?.dispose();
    renderer?.dispose();
    renderer?.forceContextLoss();
    renderer?.domElement.remove();
  }
  try {
    if (signal.aborted) { release(); return null; }
    renderer = new THREE.WebGLRenderer({ antialias:true, alpha:false, powerPreference:'high-performance' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = .94;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    scene.background = new THREE.Color('#eaf0fa');
    const room = new RoomEnvironment();
    const generator = new THREE.PMREMGenerator(renderer);
    environment = generator.fromScene(room, .04);
    room.dispose(); generator.dispose();
    scene.environment = environment.texture;
    scene.environmentIntensity = protein ? .30 : .69;
    const hemi = new THREE.HemisphereLight(0xf7f8ff, 0x49596f, .29);
    scene.add(hemi);
    for (const [color, strength, x, y, z] of [
      [0xffeed7,2.8,-3,5,4],[0xcce8fa,.55,4,2,1],[0xd4f1f6,1.25,1,4,-3]
    ]) {
      const light = new THREE.DirectionalLight(color,strength);
      light.position.set(x,y,z).normalize().multiplyScalar(protein ? 88 : 10);
      light.target.position.set(0,protein ? 0 : 1.6,0);
      if (x === -3) {
        light.castShadow = true;
        const span = protein ? 45 : 4.7;
        Object.assign(light.shadow.camera,{left:-span,right:span,top:span,bottom:-span,near:.1,far:protein ? 180 : 24});
        light.shadow.mapSize.set(1536,1536);
        light.shadow.normalBias = protein ? .045 : .003;
        light.shadow.bias = -.00012;
      }
      scene.add(light,light.target);
    }
    scene.add(root);

    for (const object of root.children) {
      const info = object.userData;
      const vector = protein ? info.explodeDirection : info.explode;
      if (!Array.isArray(vector)) continue;
      const clones = new Map();
      const part = {
        object, name:object.name, label:protein ? '亚基 ' + info.label + ' (' + info.authorChain + ')' : info.display_name,
        base:object.position.clone(), shift:new THREE.Vector3(...vector).multiplyScalar(protein ? 25 : 1), colors:[]
      };
      object.traverse(mesh => {
        if (!mesh.isMesh) return;
        const local = [].concat(mesh.material).map(m => {
          if (!clones.has(m)) {
            const clone = m.clone();
            clones.set(m,clone); materials.add(clone);
            part.colors.push([clone,clone.color.clone()]);
          }
          return clones.get(m);
        });
        mesh.material = Array.isArray(mesh.material) ? local : local[0];
        mesh.castShadow = local.every(m=>!m.transparent && !m.transmission);
        mesh.receiveShadow = true;
        mesh.userData.pickGroup = part.name;
      });
      parts.push(part);
    }
    if (parts.length !== (protein ? 10 : 7)) throw new Error('模型的装配分组不完整');
    if (protein) parts.sort((a,b)=>a.name.localeCompare(b.name));
    else {
      const order=['Frame','Worktop','Sash','Hood','Prefilter','Blower','Filter'];
      parts.sort((a,b)=>order.indexOf(a.name)-order.indexOf(b.name));
    }
    const canvas = renderer.domElement;
    canvas.tabIndex=0;
    canvas.setAttribute('role','group');
    canvas.setAttribute('aria-label',work.title+'三维视图。方向键旋转，加减键缩放，Home 复位。');
    stage.prepend(canvas);
    controls = new OrbitControls(camera,canvas);
    controls.enablePan = false;
    controls.rotateSpeed = .75;
    controls.zoomSpeed = .9;
    controls.minPolarAngle = .03; controls.maxPolarAngle = Math.PI-.03;
    const render = () => { if (!closed) renderer.render(scene,camera); };
    controls.addEventListener('change',render);

    function reframe(resetAngle=false, preserveZoom=true) {
      const offset = camera.position.clone().sub(controls.target);
      const direction = resetAngle || !lastDistance ? initial : offset.clone().normalize();
      const relativeZoom = preserveZoom && lastDistance ? offset.length()/lastDistance : 1;
      const visible = parts.filter(p=>p.object.visible).map(p=>p.object);
      const fit = fitCamera(visible,direction,camera);
      controls.target.copy(fit.center);
      camera.position.copy(fit.center).addScaledVector(direction,fit.distance*relativeZoom);
      controls.minDistance = fit.distance*.22;
      controls.maxDistance = fit.distance*3.8;
      camera.near=fit.distance/1000;camera.far=fit.distance*12;
      camera.updateProjectionMatrix();
      lastDistance=fit.distance;
      controls.update();render();
    }
    function resize() {
      const w=stage.clientWidth, h=stage.clientHeight;
      if(!w||!h||closed)return;
      renderer.setSize(w,h,false);camera.aspect=w/h;
      reframe(!lastDistance);
    }
    const highlight = new THREE.Color('#405eff');
    function styleParts() {
      for (const part of parts) {
        part.object.visible = !isolated || part.name===selected;
        for (const [material,color] of part.colors) {
          material.color.copy(color);
          if (!isolated && part.name===selected) material.color.lerp(highlight,.55);
        }
      }
      render();
    }
    function select(name) {
      const wasIsolated=isolated;
      selected=name;isolated=false;styleParts();
      if(wasIsolated)reframe(false,false);
    }
    function isolate(active) {
      isolated=Boolean(active && selected);styleParts();reframe(false,false);
    }
    function setExplosion(value) {
      for (const p of parts) p.object.position.copy(p.base).addScaledVector(p.shift,value);
      reframe();
    }
    const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2();
    let down = null;
    canvas.addEventListener('pointerdown',e=>{
      if (e.isPrimary && e.button===0) down={id:e.pointerId,x:e.clientX,y:e.clientY};
      else down=null;
    });
    canvas.addEventListener('pointercancel',()=>{down=null;});
    canvas.addEventListener('pointerup',e=>{
      const start=down;down=null;
      if(!start || start.id!==e.pointerId || Math.hypot(e.clientX-start.x,e.clientY-start.y)>5 || isolated)return;
      const box=canvas.getBoundingClientRect();
      pointer.set((e.clientX-box.left)/box.width*2-1,1-(e.clientY-box.top)/box.height*2);
      raycaster.setFromCamera(pointer,camera);
      const hit=raycaster.intersectObjects(parts.map(p=>p.object),true)[0];
      const name=hit?.object.userData.pickGroup || '';
      select(name);onPick(name);
    });
    canvas.addEventListener('keydown',e=>{
      if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','Home'].includes(e.key))return;
      e.preventDefault();
      if(e.key==='Home'){reframe(true,false);return;}
      const spherical=new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));
      if(e.key==='ArrowLeft')spherical.theta-=.12;
      if(e.key==='ArrowRight')spherical.theta+=.12;
      if(e.key==='ArrowUp')spherical.phi-=.10;
      if(e.key==='ArrowDown')spherical.phi+=.10;
      if(e.key==='+'||e.key==='=')spherical.radius*=.86;
      if(e.key==='-')spherical.radius/=.86;
      spherical.phi=THREE.MathUtils.clamp(spherical.phi,.03,Math.PI-.03);
      spherical.radius=THREE.MathUtils.clamp(spherical.radius,controls.minDistance,controls.maxDistance);
      camera.position.setFromSpherical(spherical).add(controls.target);controls.update();
    });
    resize();
    resizeObserver = new ResizeObserver(resize);resizeObserver.observe(stage);
    return {parts:parts.map(({name,label})=>({name,label})), select,isolate,setExplosion,reset:()=>reframe(true,false),destroy:release};
  } catch (error) {
    release();
    throw error;
  }
}
