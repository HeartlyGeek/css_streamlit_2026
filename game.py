# game.py
GAME_HEIGHT = 860

def get_game_html() -> str:
    return r"""
<div class="gameWrap">
  <div class="gameShell">
    <div class="hudRow">
      <div class="hudLeft">
        <div class="hudTitle">🧬 Nanobot Defender</div>
        <div class="hudSub">Weapons 1–4 • Powerups • New virus variants • Boss waves</div>
      </div>
      <div class="hudRight">
        <button id="btnMute" class="hudBtn">Muted 🔇</button>
        <button id="btnPause" class="hudBtn">Pause</button>
        <button id="btnRestart" class="hudBtn">Restart</button>
      </div>
    </div>

    <div class="canvasWrap">
      <canvas id="cv"></canvas>

      <!-- START overlay (shown on first load) -->
      <div id="startOverlay" class="overlay">
        <div class="panel">
          <div class="big">READY?</div>
          <div class="small" style="margin-top:8px;">
            Click <b>Start</b> to begin.<br/>
            Move: ◀ ▶ • Fire: Space (or Shoot button) • Weapons: 1–4
          </div>
          <div class="row">
            <button id="btnStart" class="ovBtn">Start game</button>
          </div>
        </div>
      </div>

      <!-- GAME OVER overlay -->
      <div id="overlay" class="overlay hidden">
        <div class="panel">
          <div class="big">GAME OVER</div>
          <div id="final" class="small"></div>
          <div class="row">
            <button id="ovRestart" class="ovBtn">Play again</button>
          </div>
        </div>
      </div>
    </div>

    <div class="bottomRow">
      <div class="weaponBar" id="weaponBar">
        <button class="wbtn sel" data-w="1">1 Blaster</button>
        <button class="wbtn" data-w="2">2 Missile</button>
        <button class="wbtn" data-w="3">3 Laser</button>
        <button class="wbtn" data-w="4">4 Shotgun</button>
      </div>

      <div id="mobileControls" class="controls hidden">
        <button class="ctl" id="left">◀</button>
        <button class="ctl fire" id="fire">⦿</button>
        <button class="ctl" id="right">▶</button>
      </div>
    </div>
  </div>
</div>

<style>
  .gameWrap{ width:100%; display:flex; justify-content:center; }
  .gameShell{
    width:min(1000px, 100%);
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 12px;
    box-shadow: 0 10px 26px rgba(0,0,0,0.28);
  }
  .hudRow{
    display:flex; justify-content:space-between; align-items:center;
    gap: 10px; padding: 6px 8px 10px 8px;
  }
  .hudTitle{ color:#e5e7eb; font-weight:900; letter-spacing:-0.02em; }
  .hudSub{ color:#a7b0c3; font-size:13px; margin-top:2px; }
  .hudBtn{
    height: 38px; padding: 0 12px; border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.06);
    color:#e5e7eb; cursor:pointer;
  }
  .hudBtn:active{ transform: scale(0.99); }

  .canvasWrap{
    position: relative;
    width: 100%;
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.10);
    background:
      radial-gradient(1200px 420px at 20% 20%, rgba(180,18,44,0.18), rgba(0,0,0,0) 62%),
      radial-gradient(900px 360px at 80% 15%, rgba(120,8,20,0.20), rgba(0,0,0,0) 60%),
      linear-gradient(135deg, #130008, #07040b 55%, #13000a);
  }
  canvas{ width:100%; height:auto; display:block; aspect-ratio: 16/9; }

  .bottomRow{
    margin-top: 10px;
    display:flex;
    gap: 10px;
    align-items:center;
    justify-content: space-between;
    flex-wrap: wrap;
  }

  .weaponBar{ display:flex; gap:10px; flex-wrap: wrap; }
  .wbtn{
    height: 38px;
    padding: 0 12px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.06);
    color:#e5e7eb;
    cursor:pointer;
    font-weight: 750;
    letter-spacing:-0.01em;
  }
  .wbtn:hover{ background: rgba(255,255,255,0.10); border-color: rgba(236,72,153,0.30); }
  .wbtn.sel{
    border-color: rgba(236,72,153,0.55);
    background: linear-gradient(rgba(236,72,153,0.18), rgba(6,182,212,0.08));
    box-shadow: 0 0 0 2px rgba(236,72,153,0.16) inset;
  }

  .overlay{
    position:absolute; inset:0;
    display:flex; align-items:center; justify-content:center;
    background: rgba(0,0,0,0.55);
    backdrop-filter: blur(6px);
  }
  .hidden{ display:none; }
  .panel{
    width: min(460px, 92%);
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.18);
    background: rgba(17,24,39,0.78);
    box-shadow: 0 18px 60px rgba(0,0,0,0.55);
    padding: 18px;
    text-align:center;
  }
  .big{ color:#fff; font-weight:950; font-size: 34px; letter-spacing:-0.03em; }
  .small{ color:#cbd5e1; margin-top: 6px; font-size: 14px; line-height:1.35; }
  .row{ display:flex; justify-content:center; margin-top: 14px; }
  .ovBtn{
    height: 44px; padding: 0 16px; border-radius: 14px;
    border: 1px solid rgba(236,72,153,0.40);
    background: rgba(236,72,153,0.18);
    color:#fff; font-weight:800; cursor:pointer;
  }

  .controls{ display:flex; justify-content:center; gap: 10px; flex-wrap:wrap; }
  .ctl{
    width: 74px; height: 54px; border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.18);
    background: rgba(255,255,255,0.06);
    color:#fff; font-size: 20px;
    -webkit-tap-highlight-color: transparent;
    cursor:pointer;
  }
  .ctl.fire{
    width: 92px;
    border-color: rgba(236,72,153,0.35);
    background: rgba(236,72,153,0.12);
    font-weight: 900;
    letter-spacing: -0.02em;
  }
  .ctl:active{ transform: scale(0.98); background: rgba(255,255,255,0.10); }
</style>

<script>
(() => {
  const cv = document.getElementById("cv");
  const ctx = cv.getContext("2d");

  const overlay = document.getElementById("overlay");
  const finalTxt = document.getElementById("final");
  const btnMute = document.getElementById("btnMute");
  const btnPause = document.getElementById("btnPause");
  const btnRestart = document.getElementById("btnRestart");
  const ovRestart = document.getElementById("ovRestart");

  const startOverlay = document.getElementById("startOverlay");
  const btnStart = document.getElementById("btnStart");

  const weaponBar = document.getElementById("weaponBar");
  const weaponButtons = [...weaponBar.querySelectorAll(".wbtn")];

  const mobileControls = document.getElementById("mobileControls");
  const leftBtn = document.getElementById("left");
  const rightBtn = document.getElementById("right");
  const fireBtn = document.getElementById("fire");

  const isTouch = ("ontouchstart" in window) || (navigator.maxTouchPoints > 0);
  if (isTouch) mobileControls.classList.remove("hidden");

  // Logical resolution
  const W = 960, H = 540;

  function fitCanvas(){
    const rect = cv.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    cv.width = Math.round(rect.width * dpr);
    cv.height = Math.round(rect.height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.scale(rect.width / W, rect.height / H);
  }
  window.addEventListener("resize", fitCanvas);

  // Helpers
  const rand = (a,b)=>a+Math.random()*(b-a);
  const clamp = (v,a,b)=>Math.max(a,Math.min(b,v));
  const dist2 = (x1,y1,x2,y2)=>{ const dx=x1-x2, dy=y1-y2; return dx*dx+dy*dy; };

  function linePointDistance(px,py, x1,y1, x2,y2){
    const A = px - x1, B = py - y1, C = x2 - x1, D = y2 - y1;
    const dot = A*C + B*D;
    const lenSq = C*C + D*D;
    let t = lenSq ? (dot / lenSq) : 0;
    t = Math.max(0, Math.min(1, t));
    const xx = x1 + C*t, yy = y1 + D*t;
    const dx = px - xx, dy = py - yy;
    return Math.sqrt(dx*dx + dy*dy);
  }

  // ------------------------------------------------------------
  // Audio (starts muted) + auto-load SFX (no music)
  // ------------------------------------------------------------
  const AUDIO_BASE = "https://opengameart.org/sites/default/files/";
  // If these fail to fetch (CORS / missing), the game falls back to synthesized SFX.
  const AUDIO_URLS = {
    // Laser-ish shots
    shoot1: AUDIO_BASE + "80s_SciFi_Laser_Shot.ogg",
    shoot2: AUDIO_BASE + "Laser_Shoot_9.ogg",
    shoot3: AUDIO_BASE + "laser3.ogg",
    // Chunky shotgun / impact
    shoot4: AUDIO_BASE + "Shotgun_Blast.ogg",
    // Enemy death pop
    kill:   AUDIO_BASE + "Explosion3.ogg",
  };

  const AudioSys = {
    ctx: null,
    master: null,
    buffers: {},
    muted: true,
    loading: false,
    laserHum: null, // {osc, gain}
  };

  function audioInit(){
    if (AudioSys.ctx) return;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return; // no WebAudio support
    AudioSys.ctx = new Ctx();
    AudioSys.master = AudioSys.ctx.createGain();
    AudioSys.master.gain.value = 0.0; // start muted
    AudioSys.master.connect(AudioSys.ctx.destination);
  }

  function audioResume(){
    if (!AudioSys.ctx) return;
    if (AudioSys.ctx.state === "suspended") AudioSys.ctx.resume().catch(()=>{});
  }

  async function audioLoadBuffer(name, url){
    try{
      const res = await fetch(url, {cache:"force-cache"});
      if (!res.ok) throw new Error(res.status);
      const arr = await res.arrayBuffer();
      const buf = await AudioSys.ctx.decodeAudioData(arr);
      AudioSys.buffers[name] = buf;
    }catch(_e){
      // ignore; synthesized fallback will be used
    }
  }

  async function audioLoadAssets(){
    if (!AudioSys.ctx || AudioSys.loading) return;
    AudioSys.loading = true;
    try{
      await Promise.all(Object.entries(AUDIO_URLS).map(([k,u]) => audioLoadBuffer(k,u)));
    } finally {
      AudioSys.loading = false;
    }
  }

  function audioSetMuted(m){
    AudioSys.muted = !!m;
    if (AudioSys.master){
      const target = AudioSys.muted ? 0.0 : 0.9;
      AudioSys.master.gain.setTargetAtTime(target, AudioSys.ctx.currentTime, 0.03);
    }
    // Ensure any continuous hum obeys mute state
    if (AudioSys.laserHum && AudioSys.laserHum.gain){
      const t = AudioSys.ctx ? AudioSys.ctx.currentTime : 0;
      AudioSys.laserHum.gain.gain.setTargetAtTime(AudioSys.muted ? 0.0 : 0.07, t, 0.04);
    }
    btnMute.textContent = AudioSys.muted ? "Muted" : "Sound";
  }

  function audioPlayBuffer(buf, opts={}){
    if (!AudioSys.ctx || !buf || AudioSys.muted) return;
    const t = AudioSys.ctx.currentTime;
    const src = AudioSys.ctx.createBufferSource();
    src.buffer = buf;

    // Simple pitch variety
    src.playbackRate.value = opts.rate ?? 1.0;

    const g = AudioSys.ctx.createGain();
    g.gain.value = opts.gain ?? 0.65;

    // Soft limiter to avoid clipping
    const comp = AudioSys.ctx.createDynamicsCompressor();
    comp.threshold.value = -18;
    comp.knee.value = 30;
    comp.ratio.value = 10;
    comp.attack.value = 0.002;
    comp.release.value = 0.09;

    src.connect(g);
    g.connect(comp);
    comp.connect(AudioSys.master);
    src.start(t);
  }

  function audioSynthShoot(pitch=540, dur=0.08, gain=0.35){
    if (!AudioSys.ctx || AudioSys.muted) return;
    const t0 = AudioSys.ctx.currentTime;
    const osc = AudioSys.ctx.createOscillator();
    const g = AudioSys.ctx.createGain();
    osc.type = "square";
    osc.frequency.setValueAtTime(pitch, t0);
    osc.frequency.exponentialRampToValueAtTime(Math.max(70, pitch*0.28), t0 + dur);

    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(gain, t0 + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);

    osc.connect(g);
    g.connect(AudioSys.master);
    osc.start(t0);
    osc.stop(t0 + dur + 0.02);
  }

  function audioSynthNoise(dur=0.12, gain=0.28){
    if (!AudioSys.ctx || AudioSys.muted) return;
    const t0 = AudioSys.ctx.currentTime;
    const len = Math.floor(AudioSys.ctx.sampleRate * dur);
    const buf = AudioSys.ctx.createBuffer(1, len, AudioSys.ctx.sampleRate);
    const data = buf.getChannelData(0);
    for(let i=0;i<len;i++){
      const e = 1 - i/len;
      data[i] = (Math.random()*2-1) * e;
    }
    const src = AudioSys.ctx.createBufferSource();
    src.buffer = buf;
    const g = AudioSys.ctx.createGain();
    g.gain.value = gain;
    src.connect(g);
    g.connect(AudioSys.master);
    src.start(t0);
  }

  function audioPlaySfx(name, opts={}, legacyRate=null){
    if (!AudioSys.ctx) return;

    // Backwards compatibility: audioPlaySfx(name, gain, rate)
    if (typeof opts === "number"){
      const g = opts;
      const r = (typeof legacyRate === "number") ? legacyRate : 1.0;
      opts = {gain: g, rate: r};
    }

    const buf = AudioSys.buffers[name];
    if (buf){
      audioPlayBuffer(buf, opts);
    } else {
      // Fallback synth
      if (name.startsWith("shoot")) audioSynthShoot(opts.pitch ?? 520, opts.dur ?? 0.08, opts.gain ?? 0.35);
      else if (name === "kill") audioSynthNoise(opts.dur ?? 0.16, opts.gain ?? 0.30);
    }
  }

  function audioPlayShoot(weaponId){
    // 1 Blaster, 2 Missile, 3 Laser, 4 Shotgun
    if (weaponId === 2) audioPlaySfx("shoot2", {rate:0.95, gain:0.55, pitch:440, dur:0.10});
    else if (weaponId === 3) audioPlaySfx("shoot3", {rate:1.10, gain:0.45, pitch:620, dur:0.07});
    else if (weaponId === 4) audioPlaySfx("shoot4", {rate:0.92, gain:0.70, pitch:260, dur:0.12});
    else audioPlaySfx("shoot1", {rate:1.00, gain:0.55, pitch:540, dur:0.08});
  }

  function audioPlayKill(){
    audioPlaySfx("kill", {rate:1.0, gain:0.55, dur:0.16});
  }

  function audioLaserHum(on){
    if (!AudioSys.ctx) return;
    const t = AudioSys.ctx.currentTime;

    if (on){
      if (AudioSys.laserHum) return;
      const osc = AudioSys.ctx.createOscillator();
      const g = AudioSys.ctx.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(95, t);
      osc.frequency.linearRampToValueAtTime(125, t + 0.12);

      g.gain.setValueAtTime(0.0001, t);
      g.gain.setTargetAtTime(AudioSys.muted ? 0.0 : 0.07, t, 0.05);

      osc.connect(g);
      g.connect(AudioSys.master);
      osc.start(t);
      AudioSys.laserHum = {osc, gain:g};
    } else {
      if (!AudioSys.laserHum) return;
      const {osc, gain} = AudioSys.laserHum;
      gain.gain.setTargetAtTime(0.0001, t, 0.05);
      try{ osc.stop(t + 0.15); }catch(_e){}
      AudioSys.laserHum = null;
    }
  }

  // Particles
  const particles = [];
  function spark(x,y, n, hue, pow){
    for(let i=0;i<n;i++){
      const ang = rand(0, Math.PI*2);
      const sp = rand(60, pow);
      particles.push({
        x,y,
        vx: Math.cos(ang)*sp,
        vy: Math.sin(ang)*sp,
        r: rand(1.2, 3.6),
        life: rand(0.22, 0.75),
        hue
      });
    }
  }

  // Game state
  let keys = {L:false, R:false, F:false};
  let paused = true;
  let shake = 0;
  let started = false;
  let running = false;

  // ---- TUNING (easier + less shake) ----
  const SHAKE_SCALE = 0.45;       // reduce shake amplitude
  const SHAKE_DECAY = 70;         // higher = shake disappears faster
  const EXTRA_HP_CAP = 8;         // allow more healing

  // Weapons (slightly more forgiving)
  const WEAPONS = {
    1: {name:"Blaster", mode:"bullet",  fireRate:0.105, bulletSpeed:830, dmg:1},
    2: {name:"Missile", mode:"missile", fireRate:0.27,  bulletSpeed:430, dmg:1, splash:130},
    3: {name:"Laser",   mode:"laser",   fireRate:0.00,  beamDps:4.5, heatUp:0.49, coolDown:0.92},
    4: {name:"Shotgun", mode:"shotgun", fireRate:0.34,  bulletSpeed:710, pellets:8, spread:0.20, dmg:1},
  };

  // Easier defaults: more HP + slightly faster movement
  const player = {
    x: W/2, y: H-70,
    r: 18,
    speed: 430,
    cooldown: 0,
    hp: 6,
    weapon: 1,
    heat: 0,
    overheat: false,
    laserOn: false,
  };

  let score = 0;
  let time = 0;
  let bullets = [];
  let viruses = [];
  let powerups = [];
  let spores = [];
  let spawnT = 0;
  let gameOver = false;

  // Boss timing (later + lighter)
  let nextBossAt = 30;
  let bossAlive = false;

  // --- Blood-vein background (procedural) ---
  const veins = [];
  function initVeins(){
    veins.length = 0;
    const n = 16;
    for(let i=0;i<n;i++){
      veins.push({
        base: rand(-120, W+120),
        amp: rand(26, 120),
        freq: rand(0.006, 0.018),
        width: rand(3.0, 10.0),
        alpha: rand(0.08, 0.22),
        phase: rand(0, Math.PI*2),
        speed: rand(0.25, 0.85),
        drift: rand(-14, 14),
      });
    }
  }

  function drawBloodVeins(t){
    const g = ctx.createLinearGradient(0,0,W,H);
    g.addColorStop(0, "#130008");
    g.addColorStop(0.45, "#07040b");
    g.addColorStop(1, "#160009");
    ctx.fillStyle = g;
    ctx.fillRect(0,0,W,H);

    ctx.fillStyle = "rgba(220, 20, 60, 0.10)";
    ctx.beginPath(); ctx.arc(W*0.20, H*0.22, 220, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = "rgba(120, 10, 30, 0.18)";
    ctx.beginPath(); ctx.arc(W*0.82, H*0.28, 260, 0, Math.PI*2); ctx.fill();

    ctx.fillStyle = "rgba(255, 210, 220, 0.05)";
    const k = Math.floor(t*40);
    for(let i=0;i<110;i++){
      const sx = (i*173 + k*3) % W;
      const sy = (i*91 + k) % H;
      ctx.fillRect(sx, sy, 2, 2);
    }

    for(const v of veins){
      const flow = t * (0.9 + v.speed);
      const baseColA = v.alpha;
      const hiColA = v.alpha * 0.55;

      ctx.save();
      ctx.shadowBlur = 14;
      ctx.shadowColor = "rgba(255, 60, 90, 0.10)";

      ctx.lineWidth = v.width;
      ctx.strokeStyle = `rgba(150, 14, 38, ${baseColA})`;
      ctx.beginPath();
      for(let y=-60; y<=H+60; y+=26){
        const wobble =
          Math.sin((y* v.freq) + v.phase + flow*0.8) * v.amp +
          Math.sin((y* (v.freq*2.3)) + v.phase*0.7 + flow*1.2) * (v.amp*0.22);
        const x = v.base + wobble + Math.sin(flow*0.35 + y*0.01)*v.drift;
        if (y === -60) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      ctx.shadowBlur = 0;
      ctx.lineWidth = Math.max(1.2, v.width*0.40);
      ctx.strokeStyle = `rgba(255, 170, 185, ${hiColA})`;
      ctx.beginPath();
      for(let y=-60; y<=H+60; y+=28){
        const wobble =
          Math.sin((y* v.freq) + v.phase + flow*0.8) * v.amp +
          Math.sin((y* (v.freq*2.3)) + v.phase*0.7 + flow*1.2) * (v.amp*0.22);
        const x = v.base + wobble + 0.8;
        if (y === -60) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      ctx.restore();
    }

    const vg = ctx.createRadialGradient(W*0.5, H*0.5, 120, W*0.5, H*0.5, 620);
    vg.addColorStop(0, "rgba(0,0,0,0)");
    vg.addColorStop(1, "rgba(0,0,0,0.55)");
    ctx.fillStyle = vg;
    ctx.fillRect(0,0,W,H);
  }

  function reset(){
    score = 0;
    time = 0;
    bullets = [];
    viruses = [];
    powerups = [];
    spores = [];
    particles.length = 0;
    spawnT = 0;
    shake = 0;
    paused = false;
    gameOver = false;
    bossAlive = false;
    nextBossAt = 30;

    player.x = W/2;
    player.hp = 6;
    player.cooldown = 0;
    player.weapon = 1;
    player.heat = 0;
    player.overheat = false;
    player.laserOn = false;
    audioLaserHum(false);

    overlay.classList.add("hidden");
    btnPause.textContent = "Pause";
    setWeaponUI(1);
  }

  function endGame(){
    gameOver = true;
    finalTxt.textContent = `Score: ${score} • Survived: ${Math.floor(time)}s`;
    overlay.classList.remove("hidden");
  }

  function setWeaponUI(w){
    player.weapon = w;
    weaponButtons.forEach(b => b.classList.toggle("sel", Number(b.dataset.w) === w));
  }

  function nearestVirus(x,y){
    let best = null;
    let bestD = Infinity;
    for(const v of viruses){
      if (v.kind === "spore") continue;
      const d = dist2(x,y, v.x, v.y);
      if (d < bestD){ bestD = d; best = v; }
    }
    return best;
  }

  function addShake(amount, cap){
    shake = Math.min(cap, shake + amount * SHAKE_SCALE);
  }

  function explode(x,y, radius, baseDmg){
    spark(x,y, 70, 40, 680);
    spark(x,y, 46, 310, 640);
    addShake(6, 12);

    for(let i=viruses.length-1;i>=0;i--){
      const v = viruses[i];
      const d = Math.sqrt(dist2(x,y,v.x,v.y));
      if (d < radius + v.r){
        const falloff = 1 - (d / (radius + v.r));
        const dmg = Math.max(0.35, baseDmg * falloff * 1.6);
        damageVirus(v, dmg);
      }
    }
  }

  function shoot(){
    const w = WEAPONS[player.weapon];
    if (w.mode === "laser") return;

    if (player.cooldown > 0) return;
    player.cooldown = w.fireRate;

    // Weapon SFX (each gun has its own sound)
    audioPlayShoot(player.weapon);

    if (w.mode === "bullet"){
      spark(player.x, player.y-14, 16, 310, 260);
      addShake(0.9, 4);
      bullets.push({
        kind:"bullet",
        x: player.x, y: player.y-20,
        vx: 0, vy: -w.bulletSpeed,
        r: 3.2,
        life: 1.35,
        dmg: w.dmg,
      });
    }

    if (w.mode === "missile"){
      spark(player.x, player.y-14, 24, 40, 360);
      addShake(1.4, 5);
      bullets.push({
        kind:"missile",
        x: player.x, y: player.y-18,
        vx: 0, vy: -w.bulletSpeed,
        r: 5.0,
        life: 3.0,
        dmg: w.dmg,
        splash: w.splash,
        turn: 5.1,
        speed: w.bulletSpeed,
      });
    }

    if (w.mode === "shotgun"){
      spark(player.x, player.y-14, 28, 320, 360);
      addShake(1.2, 5);

      const pellets = w.pellets;
      for(let i=0;i<pellets;i++){
        const a = -Math.PI/2 + rand(-w.spread, w.spread);
        bullets.push({
          kind:"pellet",
          x: player.x, y: player.y-20,
          vx: Math.cos(a) * (w.bulletSpeed*0.45),
          vy: Math.sin(a) * w.bulletSpeed,
          r: 2.6,
          life: 0.78,
          dmg: w.dmg,
        });
      }
    }
  }

  // --- Enemies ---
  function spawnVirus(type=null, x=null, y=null, opts=null){
    const t = time;

    const pick = () => {
      const r = Math.random();
      const redChance = (t < 12) ? 0.06 : (t < 28 ? 0.12 : 0.16);
      if (Math.random() < redChance) return "crimson";

      if (t < 12) return (r < 0.76) ? "basic" : (r < 0.94 ? "spinner" : "swarm");
      if (t < 30) return (r < 0.38) ? "basic"
                        : (r < 0.52 ? "swooper"
                        : (r < 0.62 ? "shielded"
                        : (r < 0.78 ? "splitter"
                        : (r < 0.92 ? "swarm" : "bomber"))));
      return (r < 0.26) ? "basic"
            : (r < 0.40 ? "swooper"
            : (r < 0.52 ? "shielded"
            : (r < 0.68 ? "splitter"
            : (r < 0.80 ? "bomber"
            : (r < 0.90 ? "tank" : "swarm")))));
    };

    const kind = type || pick();

    const v = {
      kind,
      x: (x ?? rand(40, W-40)),
      y: (y ?? -30),
      r: rand(16, 24),
      vx: rand(-34, 34),
      vy: rand(72, 118),
      hp: 1,
      maxHp: 1,
      spin: rand(-3,3),
      ang: rand(0, Math.PI*2),
      hue: rand(110, 150),
      elite: false,
      shield: 0,
      phase: rand(0, Math.PI*2),
      dropT: 0,
      zigT: 0,
    };

    if (kind === "crimson"){
      v.r = rand(16, 24);
      v.vy = rand(76, 125);
      v.vx = rand(-85, 85);
      v.hp = 1; v.maxHp = 1;
      v.hue = rand(0, 18);
      v.spin = rand(-6, 6);
    } else if (kind === "swarm"){
      v.r = rand(10, 14);
      v.vy = rand(140, 205);
      v.vx = rand(-100, 100);
      v.hp = 1; v.maxHp = 1;
      v.hue = rand(125, 160);
    } else if (kind === "spinner"){
      v.r = rand(18, 26);
      v.vy = rand(82, 130);
      v.spin = rand(-8, 8);
      v.hp = 2; v.maxHp = 2;
      v.hue = rand(95, 125);
    } else if (kind === "swooper"){
      v.r = rand(18, 26);
      v.vy = rand(78, 118);
      v.vx = rand(52, 98) * (Math.random()<0.5 ? -1 : 1);
      v.hp = 2; v.maxHp = 2;
      v.hue = rand(140, 175);
    } else if (kind === "shielded"){
      v.r = rand(22, 30);
      v.vy = rand(62, 102);
      v.hp = 3; v.maxHp = 3;
      v.shield = 1.6;
      v.hue = 180;
    } else if (kind === "splitter"){
      v.r = rand(22, 30);
      v.vy = rand(72, 108);
      v.hp = 2; v.maxHp = 2;
      v.hue = 155;
    } else if (kind === "bomber"){
      v.r = rand(20, 28);
      v.vy = rand(60, 94);
      v.hp = 3; v.maxHp = 3;
      v.dropT = rand(0.80, 1.20);
      v.hue = 205;
    } else if (kind === "tank"){
      v.r = rand(28, 40);
      v.vy = rand(50, 72);
      v.vx = rand(-30, 30);
      v.hp = 5; v.maxHp = 5;
      v.hue = 95;
    } else {
      v.hp = 1; v.maxHp = 1;
      v.hue = rand(110, 150);
    }

    if (opts) Object.assign(v, opts);
    viruses.push(v);
  }

  function spawnBoss(){
    bossAlive = true;
    viruses.push({
      kind: "boss",
      x: W/2,
      y: -90,
      r: 64,
      vx: 130,
      vy: 70,
      hp: 68,
      maxHp: 68,
      spin: 1.25,
      ang: 0,
      hue: 300,
      elite: true,
      shield: 10,
      phase: rand(0, Math.PI*2),
      dropT: 0.38,
      zigT: 0,
    });
  }

  // --- Powerups ---
  function maybeDropPowerup(x,y){
    if (Math.random() < 0.18){
      const t = Math.random();
      let kind = "heal";
      if (t < 0.32) kind = "heal";
      else if (t < 0.56) kind = "rapid";
      else if (t < 0.80) kind = "spread";
      else kind = "power";
      powerups.push({x, y, r: 12, vy: 110, kind, life: 10});
    }
  }

  function applyPowerup(kind){
    if (kind === "heal"){
      player.hp = Math.min(EXTRA_HP_CAP, player.hp + 1);
    } else if (kind === "rapid"){
      for(const k of [1,2,4]){
        WEAPONS[k].fireRate = Math.max(0.07, WEAPONS[k].fireRate - 0.01);
      }
      WEAPONS[3].coolDown = Math.min(1.45, WEAPONS[3].coolDown + 0.06);
    } else if (kind === "spread"){
      WEAPONS[4].pellets = Math.min(14, WEAPONS[4].pellets + 2);
      WEAPONS[2].splash = Math.min(200, WEAPONS[2].splash + 14);
    } else if (kind === "power"){
      WEAPONS[1].dmg = Math.min(4, WEAPONS[1].dmg + 1);
      WEAPONS[2].dmg = Math.min(4, WEAPONS[2].dmg + 1);
      WEAPONS[4].dmg = Math.min(4, WEAPONS[4].dmg + 1);
      WEAPONS[3].beamDps = Math.min(10.5, WEAPONS[3].beamDps + 0.9);
    }
    spark(player.x, player.y, 32, 200, 520);
    addShake(3, 8);
  }

  // Damage + death
  function damageVirus(v, dmg){
    if (v.kind === "shielded" || v.kind === "boss"){
      if (v.shield > 0){
        v.shield -= dmg;
        spark(v.x, v.y, 10, 190, 220);
        if (v.shield < 0){
          v.hp += v.shield;
          v.shield = 0;
        }
      } else {
        v.hp -= dmg;
      }
    } else {
      v.hp -= dmg;
    }

    if (v.hp <= 0){
      onVirusDeath(v);
    }
  }

  function onVirusDeath(v){
    const idx = viruses.indexOf(v);
    if (idx >= 0) viruses.splice(idx, 1);

    spark(v.x, v.y, v.elite ? 110 : 60, v.hue, v.elite ? 860 : 620);

    // Enemy death SFX
    audioPlaySfx("kill", v.elite ? 0.28 : 0.20, (v.kind === "boss") ? 0.75 : (v.elite ? 0.92 : 1.0));

    maybeDropPowerup(v.x, v.y);

    const add = (v.kind === "boss") ? 65 :
                (v.kind === "tank") ? 5 :
                (v.kind === "bomber") ? 4 :
                (v.kind === "shielded") ? 4 :
                (v.kind === "swooper") ? 3 :
                (v.kind === "spinner") ? 3 :
                (v.kind === "swarm") ? 2 : 2;
    score += add;

    if (v.kind === "splitter"){
      for(let k=0;k<2;k++){
        spawnVirus("swarm", v.x + rand(-18,18), v.y + rand(-10,10), {
          vy: rand(160,220), vx: rand(-120,120), r: rand(10,13), hp:1, maxHp:1
        });
      }
    }

    if (v.kind === "boss"){
      bossAlive = false;
      nextBossAt = time + 34;
      spark(W/2, H/2, 150, 310, 1200);
      addShake(6, 12);
    }
  }

  // Input
  document.addEventListener("keydown", (e)=>{
    if (e.key === "ArrowLeft") keys.L = true;
    if (e.key === "ArrowRight") keys.R = true;
    if (e.key === " ") keys.F = true;

    if (e.key === "1") setWeaponUI(1);
    if (e.key === "2") setWeaponUI(2);
    if (e.key === "3") setWeaponUI(3);
    if (e.key === "4") setWeaponUI(4);

    if (e.key.toLowerCase() === "p") togglePause();
  });
  document.addEventListener("keyup", (e)=>{
    if (e.key === "ArrowLeft") keys.L = false;
    if (e.key === "ArrowRight") keys.R = false;
    if (e.key === " ") keys.F = false;
  });

  weaponButtons.forEach(btn => {
    btn.addEventListener("click", () => setWeaponUI(Number(btn.dataset.w)));
  });

  function bindHold(btn, onDown, onUp){
    btn.addEventListener("touchstart", (e)=>{ e.preventDefault(); onDown(); }, {passive:false});
    btn.addEventListener("touchend", (e)=>{ e.preventDefault(); onUp(); }, {passive:false});
    btn.addEventListener("mousedown", (e)=>{ e.preventDefault(); onDown(); });
    btn.addEventListener("mouseup", (e)=>{ e.preventDefault(); onUp(); });
    btn.addEventListener("mouseleave", ()=>onUp());
  }
  bindHold(leftBtn,  ()=>keys.L=true, ()=>keys.L=false);
  bindHold(rightBtn, ()=>keys.R=true, ()=>keys.R=false);
  bindHold(fireBtn,  ()=>keys.F=true, ()=>keys.F=false);

  function togglePause(){
    if (!started || gameOver) return;
    paused = !paused;
    btnPause.textContent = paused ? "Resume" : "Pause";
  }
  btnPause.onclick = togglePause;

  // Mute toggle (game starts muted)
  btnMute.onclick = () => {
    audioInit();
    audioResume();
    audioSetMuted(!AudioSys.muted);
  };

  btnRestart.onclick = () => {
    if (!started) startGame();
    else reset();
  };
  ovRestart.onclick = () => {
    if (!started) startGame();
    else reset();
  };

  function drawPlayer(){
    ctx.save();
    ctx.shadowBlur = 22;
    ctx.shadowColor = "rgba(6,182,212,0.55)";
    ctx.fillStyle = "#06b6d4";
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.r, 0, Math.PI*2);
    ctx.fill();
    ctx.restore();

    ctx.fillStyle = "rgba(255,255,255,0.90)";
    ctx.beginPath();
    ctx.arc(player.x+5, player.y-5, 5.4, 0, Math.PI*2);
    ctx.fill();

    const w = player.weapon;
    ctx.save();
    ctx.globalAlpha = 0.22;
    if (w===2) ctx.fillStyle = "#f59e0b";
    else if (w===3) ctx.fillStyle = "#22c55e";
    else if (w===4) ctx.fillStyle = "#ec4899";
    else ctx.fillStyle = "#06b6d4";
    ctx.beginPath(); ctx.arc(player.x, player.y, player.r+10, 0, Math.PI*2); ctx.fill();
    ctx.restore();
  }

  function drawVirus(v){
    ctx.save();
    ctx.translate(v.x, v.y);
    ctx.rotate(v.ang);

    ctx.shadowBlur = v.elite ? 26 : 14;
    ctx.shadowColor = `hsla(${v.hue}, 90%, 55%, 0.35)`;

    const spikes = (v.kind==="boss") ? 20 : (v.kind==="tank" ? 14 : 12);
    ctx.fillStyle = `hsla(${v.hue}, 82%, 52%, 0.95)`;
    for(let i=0;i<spikes;i++){
      const a = i*(Math.PI*2/spikes);
      const rr = v.r + 8 + Math.sin(time*2 + i)*2;
      ctx.beginPath();
      ctx.arc(Math.cos(a)*rr, Math.sin(a)*rr, 3.2, 0, Math.PI*2);
      ctx.fill();
    }

    if (v.kind==="boss"){
      ctx.fillStyle = "rgba(168,85,247,0.58)";
    } else {
      ctx.fillStyle = `hsla(${v.hue}, 72%, 40%, 0.92)`;
    }
    ctx.beginPath();
    ctx.arc(0,0, v.r, 0, Math.PI*2);
    ctx.fill();

    ctx.shadowBlur = 0;
    ctx.fillStyle = "rgba(0,0,0,0.25)";
    ctx.beginPath();
    ctx.arc(6,-6, v.r*0.45, 0, Math.PI*2);
    ctx.fill();

    if ((v.kind==="shielded" || v.kind==="boss") && v.shield > 0){
      ctx.strokeStyle = "rgba(6,182,212,0.55)";
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(0,0, v.r+8, 0, Math.PI*2);
      ctx.stroke();
    }

    if (v.kind==="boss" || v.kind==="tank"){
      const w = 80, h = 8;
      const pct = Math.max(0, v.hp / v.maxHp);
      ctx.globalAlpha = 0.9;
      ctx.fillStyle = "rgba(255,255,255,0.14)";
      ctx.fillRect(-w/2, v.r+18, w, h);
      ctx.fillStyle = (v.kind==="boss") ? "rgba(236,72,153,0.75)" : "rgba(34,197,94,0.75)";
      ctx.fillRect(-w/2, v.r+18, w*pct, h);
    }

    ctx.restore();
  }

  function drawSpore(s){
    ctx.save();
    ctx.shadowBlur = 14;
    ctx.shadowColor = "rgba(255, 120, 150, 0.22)";
    ctx.fillStyle = "rgba(255, 90, 120, 0.88)";
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
    ctx.fill();
    ctx.restore();
  }

  function drawBullet(b){
    if (b.kind==="missile"){
      ctx.save();
      ctx.shadowBlur = 18;
      ctx.shadowColor = "rgba(245,158,11,0.55)";
      ctx.fillStyle = "#f59e0b";
      ctx.beginPath();
      ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
      ctx.fill();
      ctx.restore();
      return;
    }
    ctx.save();
    ctx.shadowBlur = 16;
    ctx.shadowColor = "rgba(236,72,153,0.55)";
    ctx.fillStyle = "#ec4899";
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
    ctx.fill();
    ctx.restore();
  }

  function drawPowerup(p){
    ctx.save();
    ctx.shadowBlur = 18;
    ctx.shadowColor = "rgba(255,255,255,0.25)";
    ctx.fillStyle = "rgba(255,255,255,0.14)";
    ctx.beginPath(); ctx.arc(p.x,p.y,p.r+6,0,Math.PI*2); ctx.fill();
    ctx.shadowBlur = 0;

    let label = "H";
    let col = "#60a5fa";
    if (p.kind === "rapid"){ label="R"; col="#06b6d4"; }
    if (p.kind === "spread"){ label="S"; col="#ec4899"; }
    if (p.kind === "power"){ label="P"; col="#22c55e"; }

    ctx.fillStyle = col;
    ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fill();

    ctx.fillStyle = "rgba(0,0,0,0.35)";
    ctx.font = "bold 16px system-ui, -apple-system, Segoe UI, Arial";
    ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(label, p.x, p.y+1);
    ctx.restore();
  }

  function drawParticles(dt){
    for(let i=particles.length-1;i>=0;i--){
      const p = particles[i];
      p.life -= dt;
      if (p.life <= 0){ particles.splice(i,1); continue; }
      p.x += p.vx*dt;
      p.y += p.vy*dt;
      p.vx *= 0.92;
      p.vy *= 0.92;

      ctx.save();
      ctx.globalAlpha = Math.min(1, p.life*2);
      ctx.fillStyle = `hsla(${p.hue}, 90%, 60%, 0.95)`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      ctx.fill();
      ctx.restore();
    }
  }

  function drawLaser(dt){
    audioLaserHum(player.laserOn);
    if (!player.laserOn) return;

    const x1 = player.x, y1 = player.y - 20;
    const x2 = player.x, y2 = 0;

    ctx.save();
    ctx.globalAlpha = 0.90;
    ctx.shadowBlur = 24;
    ctx.shadowColor = "rgba(34,197,94,0.65)";

    ctx.strokeStyle = "rgba(34,197,94,0.95)";
    ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();

    ctx.globalAlpha = 0.33;
    ctx.strokeStyle = "rgba(34,197,94,0.75)";
    ctx.lineWidth = 16;
    ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
    ctx.restore();

    spark(player.x, player.y-28, 7, 120, 240);
  }

  function drawHUD(){
    ctx.save();
    ctx.fillStyle = "rgba(255,255,255,0.92)";
    ctx.font = "800 18px system-ui, -apple-system, Segoe UI, Arial";
    ctx.fillText(`Score: ${score}`, 18, 30);
    ctx.fillText(`HP: ${player.hp}`, 18, 54);

    const w = WEAPONS[player.weapon];
    ctx.fillStyle = "rgba(203,213,225,0.88)";
    ctx.font = "700 13px system-ui, -apple-system, Segoe UI, Arial";
    ctx.fillText(`Weapon: ${player.weapon} ${w.name}`, 18, 76);

    if (w.mode === "laser"){
      const barX = 18, barY = 92, barW = 180, barH = 10;
      ctx.fillStyle = "rgba(255,255,255,0.14)";
      ctx.fillRect(barX, barY, barW, barH);

      const pct = clamp(player.heat, 0, 1);
      ctx.fillStyle = player.overheat ? "rgba(236,72,153,0.85)" : "rgba(34,197,94,0.85)";
      ctx.fillRect(barX, barY, barW*pct, barH);

      ctx.fillStyle = "rgba(203,213,225,0.90)";
      ctx.fillText(player.overheat ? "OVERHEAT" : "Heat", barX + barW + 10, barY + 9);
    }

    if (!bossAlive){
      ctx.fillStyle = "rgba(203,213,225,0.72)";
      ctx.fillText(`Next boss in ~${Math.max(0, Math.floor(nextBossAt - time))}s`, 18, 118);
    } else {
      ctx.fillStyle = "rgba(236,72,153,0.70)";
      ctx.fillText(`BOSS WAVE`, 18, 118);
    }

    ctx.restore();
  }

  function updateLaser(dt){
    const w = WEAPONS[3];

    if (player.weapon !== 3){
      player.laserOn = false;
      audioLaserHum(false);
      player.overheat = false;
      player.heat = Math.max(0, player.heat - w.coolDown*dt);
      return;
    }

    if (keys.F && !player.overheat){
      player.laserOn = true;
      player.heat += w.heatUp * dt;
      if (player.heat >= 1){
        player.heat = 1;
        player.overheat = true;
        player.laserOn = false;
        spark(player.x, player.y-22, 34, 330, 620);
        addShake(6, 12);
      }
    } else {
      player.laserOn = false;
      player.heat -= w.coolDown * dt;
      if (player.heat <= 0){
        player.heat = 0;
        player.overheat = false;
      } else if (player.overheat && player.heat <= 0.30){
        player.overheat = false;
      }
    }

    audioLaserHum(player.laserOn);
    if (!player.laserOn) return;

    const x1 = player.x, y1 = player.y - 20;
    const x2 = player.x, y2 = 0;

    for(let i=viruses.length-1;i>=0;i--){
      const v = viruses[i];
      if (v.kind === "spore") continue;
      const d = linePointDistance(v.x, v.y, x1,y1, x2,y2);
      const hitR = v.r + 10;
      if (d < hitR && v.y < y1){
        damageVirus(v, w.beamDps * dt);
        spark(v.x, v.y, 3, 120, 160);
        addShake(0.4, 10);
      }
    }
  }

  function spawnSpore(x,y, vy=185){
    spores.push({
      x, y,
      r: rand(7, 11),
      vy,
      life: 5.6
    });
  }

  function update(dt){
    if (!started || paused || gameOver) return;

    time += dt;

    if (keys.L) player.x -= player.speed*dt;
    if (keys.R) player.x += player.speed*dt;
    player.x = clamp(player.x, 30, W-30);

    player.cooldown = Math.max(0, player.cooldown - dt);

    if (keys.F) shoot();
    updateLaser(dt);

    // Easier spawn curve
    spawnT += dt;
    const interval = Math.max(0.32, 1.02 - time*0.010);
    if (spawnT >= interval){
      spawnT = 0;
      spawnVirus();
      if (time > 34 && Math.random() < 0.16) spawnVirus();
      if (time > 60 && Math.random() < 0.10) spawnVirus();
    }

    if (!bossAlive && time >= nextBossAt){
      spawnBoss();
    }

    for(let i=bullets.length-1;i>=0;i--){
      const b = bullets[i];
      b.life -= dt;

      if (b.kind === "missile"){
        const t = nearestVirus(b.x, b.y);
        if (t){
          const dx = t.x - b.x;
          const dy = t.y - b.y;
          const desired = Math.atan2(dy, dx);
          const cur = Math.atan2(b.vy, b.vx);
          let diff = desired - cur;
          while(diff > Math.PI) diff -= Math.PI*2;
          while(diff < -Math.PI) diff += Math.PI*2;

          const newAng = cur + diff * Math.min(1, b.turn * dt);
          b.vx = Math.cos(newAng) * b.speed;
          b.vy = Math.sin(newAng) * b.speed;
        }
      }

      b.x += b.vx*dt;
      b.y += b.vy*dt;

      if (b.life <= 0 || b.y < -60 || b.y > H+60 || b.x < -60 || b.x > W+60){
        if (b.kind === "missile"){
          explode(b.x, b.y, b.splash, b.dmg);
        }
        bullets.splice(i,1);
      }
    }

    for(let i=spores.length-1;i>=0;i--){
      const s = spores[i];
      s.life -= dt;
      s.y += s.vy * dt;
      if (s.life <= 0 || s.y > H+60){
        spores.splice(i,1);
        continue;
      }

      if (dist2(s.x, s.y, player.x, player.y) < (s.r + player.r + 6)**2){
        spores.splice(i,1);
        player.hp -= 1;
        spark(player.x, player.y, 52, 10, 680);
        addShake(6, 12);
        if (player.hp <= 0) endGame();
      }
    }

    for(let i=viruses.length-1;i>=0;i--){
      const v = viruses[i];
      v.ang += v.spin * dt;

      if (v.kind === "swooper"){
        v.y += v.vy * dt;
        v.x += v.vx * dt + Math.sin(time*3 + v.phase) * 90 * dt;
      } else if (v.kind === "swarm"){
        v.y += v.vy * dt;
        v.x += v.vx * dt + Math.sin(time*5 + v.phase) * 52 * dt;
      } else if (v.kind === "boss"){
        v.y += Math.min(v.vy, 82) * dt;
        v.zigT += dt;
        v.x += Math.sin(v.zigT*0.9) * 180 * dt;
        v.x = clamp(v.x, 90, W-90);

        v.dropT -= dt;
        if (v.dropT <= 0){
          v.dropT = rand(0.34, 0.52);
          spawnSpore(v.x + rand(-40,40), v.y + v.r + 10, rand(170, 250));
          if (Math.random() < 0.12) spawnVirus("swarm", v.x + rand(-120,120), v.y + rand(20,40));
        }
      } else if (v.kind === "bomber"){
        v.y += v.vy * dt;
        v.x += v.vx * dt;
        v.dropT -= dt;
        if (v.dropT <= 0 && v.y > 50){
          v.dropT = rand(0.95, 1.40);
          spawnSpore(v.x + rand(-10,10), v.y + v.r + 6, rand(170, 250));
        }
      } else {
        v.x += v.vx * dt;
        v.y += v.vy * dt;
      }

      if (v.kind !== "boss"){
        if (v.x < 30 || v.x > W-30) v.vx *= -1;
      }

      if (v.y > H + 60){
        viruses.splice(i,1);
        player.hp -= 1;
        spark(W/2, H-10, 30, 10, 520);
        addShake(5, 10);
        if (player.hp <= 0) endGame();
      }
    }

    for(let i=powerups.length-1;i>=0;i--){
      const p = powerups[i];
      p.life -= dt;
      p.y += p.vy*dt;

      if (dist2(p.x,p.y, player.x, player.y) < (p.r + player.r + 8)**2){
        applyPowerup(p.kind);
        powerups.splice(i,1);
        continue;
      }

      if (p.life <= 0 || p.y > H+60) powerups.splice(i,1);
    }

    for(let bi=bullets.length-1; bi>=0; bi--){
      const b = bullets[bi];
      let hit = false;

      for(let vi=viruses.length-1; vi>=0; vi--){
        const v = viruses[vi];
        if (dist2(b.x,b.y, v.x,v.y) < (v.r + b.r + 6)**2){
          hit = true;

          if (b.kind === "missile"){
            explode(b.x, b.y, b.splash, b.dmg);
            bullets.splice(bi,1);
          } else {
            damageVirus(v, b.dmg);
            spark(b.x, b.y, 16, 310, 420);
            bullets.splice(bi,1);
          }

          addShake(0.7, 8);
          break;
        }
      }

      if (hit) continue;
    }

    for(let vi=viruses.length-1; vi>=0; vi--){
      const v = viruses[vi];
      if (dist2(v.x,v.y, player.x,player.y) < (v.r + player.r + 10)**2){
        const dmg = (v.kind==="boss") ? 2 : 1;
        viruses.splice(vi,1);
        player.hp -= dmg;
        spark(player.x, player.y, 70, 10, 820);
        addShake(8, 14);
        if (player.hp <= 0) endGame();
      }
    }
  }

  let last = performance.now();
  function loop(now){
    const dt = Math.min(0.033, (now - last)/1000);
    last = now;

    let ox=0, oy=0;
    if (shake > 0){
      shake = Math.max(0, shake - SHAKE_DECAY*dt);
      ox = rand(-shake, shake);
      oy = rand(-shake, shake);
    }

    ctx.save();
    ctx.translate(ox, oy);

    drawBloodVeins(time);
    update(dt);

    bullets.forEach(drawBullet);
    spores.forEach(drawSpore);
    viruses.forEach(drawVirus);
    drawLaser(dt);
    drawPlayer();
    for(const p of powerups) drawPowerup(p);
    drawParticles(dt);
    drawHUD();

    ctx.restore();
    requestAnimationFrame(loop);
  }

  // Desktop convenience: click/hold canvas to fire
  if (!isTouch){
    cv.addEventListener("pointerdown", () => { keys.F = true; });
    cv.addEventListener("pointerup", () => { keys.F = false; });
  }

  function startGame(){
    started = true;
    paused = false;
    gameOver = false;
    overlay.classList.add("hidden");
    startOverlay.classList.add("hidden");

    // Audio: initialize + start muted, auto-download assets
    audioInit();
    audioResume();
    audioSetMuted(true);

    reset();

    if (!running){
      running = true;
      last = performance.now();
      requestAnimationFrame(loop);
    }
  }

  btnStart.onclick = startGame;

  fitCanvas();
  initVeins();
  setWeaponUI(1);
  paused = true;
  started = false;
  btnPause.textContent = "Pause";

})();
</script>
"""
