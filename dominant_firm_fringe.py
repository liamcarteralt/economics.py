import streamlit as st
import streamlit.components.v1 as components

# 1. Page Setup (Hide standard Streamlit elements to let your design shine)
st.set_page_config(layout="wide", page_title="Dominant Firm Model")

# 2. The EXACT HTML/JS Code that you liked (Complete with the clean layout and smooth math)
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dominant Firm — Competitive Fringe</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

  :root {
    --bg: #ffffff;
    --card: #ffffff;
    --card-border: #e8e8e8;
    --card-shadow: 0 4px 12px rgba(0,0,0,0.08);
    --text: #2c2c2c;
    --text-dim: #888;
    --text-label: #555;
    --demand: #c62828;
    --mr: #e65100;
    --mc-dom: #2e7d32;
    --mc-fringe: #0277bd;
    --atc-dom: #6a1b9a;
    --atc-fringe: #4a148c;
    --fringe-supply: #2e7d32;
    --cs-color: #4285f4;
    --ps-color: #34a853;
    --dwl-color: #ea4335;
    --profit-color: #f9a825;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { height: 100%; overflow: hidden; background: var(--bg); color: var(--text); font-family: 'IBM Plex Sans', sans-serif; }

  .app { display: flex; flex-direction: column; height: 100vh; padding: 10px; }
  
  .main { display: flex; flex: 1; gap: 20px; overflow: hidden; }

  /* --- LEFT: GRAPHS --- */
  .graphs-card {
    flex: 3; min-width: 0;
    background: var(--card); border: 1px solid var(--card-border);
    border-radius: 12px; box-shadow: var(--card-shadow);
    display: flex; position: relative; overflow: hidden;
  }

  .graph-half {
    flex: 1; position: relative; display: flex; flex-direction: column;
  }
  .graph-half:first-child { border-right: 1px solid rgba(0,0,0,0.08); }

  .graph-half .graph-title {
    position: absolute; top: 12px; left: 18px;
    font-size: 14px; font-weight: 700; color: #333;
    z-index: 10; letter-spacing: 0.3px;
  }

  canvas.graph-canvas { display: block; width: 100%; flex: 1; }

  canvas.overlay-canvas {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 40;
  }

  /* --- TOOLTIP --- */
  .tooltip {
    position: absolute; pointer-events: none;
    background: rgba(255,255,255,0.98); border: 1px solid #ddd;
    border-radius: 6px; padding: 10px 14px;
    font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    opacity: 0; transition: opacity 0.1s ease;
    z-index: 100; white-space: nowrap; line-height: 1.6;
  }
  .tooltip.visible { opacity: 1; }
  .tooltip .label { color: var(--text-dim); font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-bottom: 4px; }

  /* --- RIGHT: SIDEBAR CONTROLS --- */
  .sidebar {
    flex: 1; min-width: 280px; max-width: 320px;
    display: flex; flex-direction: column; gap: 12px;
    overflow-y: auto; padding-right: 4px;
  }

  .panel {
    background: #fdfdfd; border: 1px solid var(--card-border);
    border-radius: 10px; padding: 14px;
  }
  .panel-title {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.8px; color: #888; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 6px;
  }

  .controls { display: flex; flex-direction: column; gap: 14px; }
  .control-row { display: flex; flex-direction: column; gap: 6px; }
  .control-header { display: flex; justify-content: space-between; align-items: center; }
  .control-header .name { font-size: 13px; font-weight: 500; color: #444; }
  .control-header .val { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; }

  /* Sliders */
  input[type="range"] {
    -webkit-appearance: none; appearance: none;
    width: 100%; height: 5px; border-radius: 3px; outline: none; cursor: pointer; background: #eee;
  }
  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 16px; height: 16px; border-radius: 50%;
    cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.3); border: 2px solid #fff;
  }
  input[type="range"]::-moz-range-thumb {
    width: 16px; height: 16px; border-radius: 50%;
    cursor: pointer; border: 2px solid #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  }

  /* Slider Colors */
  .slider-demand::-webkit-slider-thumb { background: #c62828; }
  .slider-fringe::-webkit-slider-thumb { background: #0277bd; }
  .slider-mc::-webkit-slider-thumb { background: #2e7d32; }
  .slider-atc::-webkit-slider-thumb { background: #6a1b9a; }

  /* Readouts */
  .readouts { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; text-align: center; }
  .readout-item .ro-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #999; }
  .readout-item .ro-value { font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; margin-top: 2px; }

  .divider { height: 1px; background: #eee; margin: 10px 0; }

  /* Footer Toggles */
  .footer {
    flex-shrink: 0; padding: 10px 0 0;
    display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
  }

  .toggle-btn {
    border: none; border-radius: 6px; padding: 6px 12px;
    font-family: 'IBM Plex Sans', sans-serif; font-size: 12px; font-weight: 600;
    cursor: pointer; transition: all 0.2s ease; user-select: none;
    background: #eee; color: #666;
  }
  .toggle-btn.active { color: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
  .toggle-btn.cs.active { background: var(--cs-color); }
  .toggle-btn.ps.active { background: var(--ps-color); }
  .toggle-btn.dwl.active { background: var(--dwl-color); }
  .toggle-btn.profit.active { background: var(--profit-color); color: #333; }
  .toggle-btn.atc-btn.active { background: var(--atc-dom); }
  .toggle-btn.comp.active { background: #555; }

  @media (max-width: 900px) {
    .main { flex-direction: column; overflow-y: auto; }
    .sidebar { width: 100%; max-width: none; flex-direction: row; flex-wrap: wrap; }
    .sidebar .panel { flex: 1; min-width: 200px; }
  }
</style>
</head>
<body>
<div class="app">
  <div class="main">
    <div class="graphs-card" id="graphs-card">
      <div class="graph-half" id="half-left">
        <div class="graph-title">Fringe Firm</div>
        <canvas class="graph-canvas" id="canvas-left"></canvas>
        <div class="tooltip" id="tooltip-left"></div>
      </div>
      <div class="graph-half" id="half-right">
        <div class="graph-title">Dominant Firm</div>
        <canvas class="graph-canvas" id="canvas-right"></canvas>
        <div class="tooltip" id="tooltip-right"></div>
      </div>
      <canvas class="overlay-canvas" id="overlay"></canvas>
    </div>

    <div class="sidebar">
      <div class="panel">
        <div class="panel-title">Market Demand</div>
        <div class="controls">
          <div class="control-row">
            <div class="control-header"><span class="name">Intercept (a)</span><span class="val" style="color:#c62828" id="val-a">100</span></div>
            <input type="range" class="slider-demand" id="slider-a" min="50" max="200" value="100" step="1">
          </div>
          <div class="control-row">
            <div class="control-header"><span class="name">Slope (b)</span><span class="val" style="color:#c62828" id="val-b">1.00</span></div>
            <input type="range" class="slider-demand" id="slider-b" min="0.2" max="3" value="1" step="0.05">
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title">Fringe Supply</div>
        <div class="controls">
          <div class="control-row">
            <div class="control-header"><span class="name">Min Price (c<sub>f</sub>)</span><span class="val" style="color:#0277bd" id="val-cf">20</span></div>
            <input type="range" class="slider-fringe" id="slider-cf" min="0" max="80" value="20" step="1">
          </div>
          <div class="control-row">
            <div class="control-header"><span class="name">Slope (d<sub>f</sub>)</span><span class="val" style="color:#0277bd" id="val-df">1.50</span></div>
            <input type="range" class="slider-fringe" id="slider-df" min="0.2" max="5" value="1.5" step="0.05">
          </div>
          <div class="control-row">
            <div class="control-header"><span class="name">Firms (n)</span><span class="val" style="color:#0277bd" id="val-n">5</span></div>
            <input type="range" class="slider-fringe" id="slider-n" min="1" max="20" value="5" step="1">
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title">Dominant Firm</div>
        <div class="controls">
          <div class="control-row">
            <div class="control-header"><span class="name">MC Base</span><span class="val" style="color:#2e7d32" id="val-mc">10</span></div>
            <input type="range" class="slider-mc" id="slider-mc" min="0" max="80" value="10" step="1">
          </div>
          <div class="control-row">
            <div class="control-header"><span class="name">MC Slope</span><span class="val" style="color:#2e7d32" id="val-mcs">0.30</span></div>
            <input type="range" class="slider-mc" id="slider-mcs" min="0" max="3" value="0.3" step="0.05">
          </div>
          <div class="control-row">
            <div class="control-header"><span class="name">Fixed Cost</span><span class="val" style="color:#6a1b9a" id="val-fc">50</span></div>
            <input type="range" class="slider-atc" id="slider-fc" min="0" max="1000" value="50" step="10">
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="readouts">
          <div class="readout-item"><div class="ro-label">P*</div><div class="ro-value" id="ro-p">—</div></div>
          <div class="readout-item"><div class="ro-label">Q<sub>d</sub></div><div class="ro-value" style="color:#2e7d32" id="ro-qd">—</div></div>
          <div class="readout-item"><div class="ro-label">Q<sub>f</sub></div><div class="ro-value" style="color:#0277bd" id="ro-qf">—</div></div>
        </div>
        <div class="divider"></div>
        <div class="readouts">
          <div class="readout-item"><div class="ro-label">π<sub>d</sub></div><div class="ro-value" style="color:#f9a825" id="ro-profit">—</div></div>
          <div class="readout-item"><div class="ro-label">CS</div><div class="ro-value" style="color:#4285f4" id="ro-cs">—</div></div>
          <div class="readout-item"><div class="ro-label">DWL</div><div class="ro-value" style="color:#ea4335" id="ro-dwl">—</div></div>
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    <button class="toggle-btn cs active" data-key="cs">Consumer Surplus</button>
    <button class="toggle-btn ps active" data-key="ps">Producer Surplus</button>
    <button class="toggle-btn dwl active" data-key="dwl">Deadweight Loss</button>
    <button class="toggle-btn profit" data-key="profit">Profit</button>
    <button class="toggle-btn atc-btn" data-key="atc">ATC</button>
    <button class="toggle-btn comp" data-key="comp">Competitive</button>
  </div>
</div>

<script>
// --- CORE MODEL LOGIC (Ported from Python to JS for Speed) ---
class DFModel {
  constructor(p){Object.assign(this,p);}
  marketDemandQ(P){return Math.max(0,(this.a-P)/this.b);}
  marketDemandP(Q){return this.a-this.b*Q;}
  fringeSupplyQ(P){return P>=this.cF?this.n*(P-this.cF)/this.dF:0;}
  fringeSupplyP(Qf){return this.cF+(this.dF*Qf)/this.n;}
  fringeFirmQ(P){return P>=this.cF?(P-this.cF)/this.dF:0;}
  mcAt(q){return this.mc0+this.mcS*q;}
  totalCost(q){return this.FC+this.mc0*q+(this.mcS*q*q)/2;}
  atcAt(q){return q>0.5?this.totalCost(q)/q:9999;}
  fringeFirmMC(q){return this.cF+this.dF*q;}
  fringeFirmATC(q){return q>0.5?this.cF+this.dF*q/2:9999;}
  kinkQ(){return Math.max(0,(this.a-this.cF)/this.b);}
  upperSeg(){const d=this.dF/this.n;return{A:(this.a*d+this.cF*this.b)/(this.b+d),B:(this.b*d)/(this.b+d)};}
  residualDemandP(Qd){const Qk=this.kinkQ();if(Qd>=Qk)return Math.max(0,this.a-this.b*Qd);const{A,B}=this.upperSeg();return Math.max(0,A-B*Qd);}
  competitivePrice(){return(this.dF*this.a+this.n*this.b*this.cF)/(this.n*this.b+this.dF);}
  solve(){
    const{a,b,cF,dF,mc0,mcS,n,FC}=this;
    const Qk=this.kinkQ();const{A,B}=this.upperSeg();
    const Q1=(2*B+mcS)>0?(A-mc0)/(2*B+mcS):Infinity;
    const Q2=(2*b+mcS)>0?(a-mc0)/(2*b+mcS):Infinity;
    let Qd,seg;
    if(Q1>=0&&Q1<Qk){Qd=Q1;seg='upper';}
    else if(Q2>=0&&Q2>Qk){Qd=Q2;seg='lower';}
    else{Qd=Qk;seg='kink';}
    Qd=Math.max(0,Qd);
    const Pd=this.residualDemandP(Qd);
    const Qf=this.fringeSupplyQ(Pd);const qf=this.fringeFirmQ(Pd);const Qt=Qd+Qf;
    const mcQd=this.mcAt(Qd);const profitD=Pd*Qd-this.totalCost(Qd);const atcQd=this.atcAt(Qd);
    const fringeATCqf=qf>0.5?cF+dF*qf/2:0;
    const fringeProfitPerFirm=qf>0?(Pd-fringeATCqf)*qf:0;
    const CS=Qt>0?0.5*(a-Pd)*Qt:0;
    let QdComp;const QdCU=(B+mcS)>0?(A-mc0)/(B+mcS):0;const QdCL=(b+mcS)>0?(a-mc0)/(b+mcS):0;
    if(QdCU>=0&&QdCU<=Qk)QdComp=QdCU;else QdComp=Math.max(0,QdCL);
    const PdComp=this.residualDemandP(QdComp);
    let DWL=0;if(Qd<QdComp){const steps=200;for(let i=0;i<steps;i++){const q=Qd+(i+0.5)/steps*(QdComp-Qd);const dq=(QdComp-Qd)/steps;const pR=this.residualDemandP(q);const mcQ=this.mcAt(q);if(pR>mcQ)DWL+=(pR-mcQ)*dq;}}
    const Pc=this.competitivePrice();
    const QcMarket=this.marketDemandQ(Pc);
    const QcFringe=this.fringeSupplyQ(Pc);
    return{Pd,Qd,Qf,qf,Qt,seg,mcQd,atcQd,profitD,fringeProfitPerFirm,CS,DWL,Qk,QdComp,PdComp,Pc,QcMarket,QcFringe};
  }
}

// --- SETUP CANVAS & UTILS ---
const cL=document.getElementById('canvas-left');
const cR=document.getElementById('canvas-right');
const cO=document.getElementById('overlay');
const xL=cL.getContext('2d');
const xR=cR.getContext('2d');
const xO=cO.getContext('2d');
const tipL=document.getElementById('tooltip-left');
const tipR=document.getElementById('tooltip-right');

const sl={a:document.getElementById('slider-a'),b:document.getElementById('slider-b'),cf:document.getElementById('slider-cf'),df:document.getElementById('slider-df'),n:document.getElementById('slider-n'),mc:document.getElementById('slider-mc'),mcs:document.getElementById('slider-mcs'),fc:document.getElementById('slider-fc')};
const vl={a:document.getElementById('val-a'),b:document.getElementById('val-b'),cf:document.getElementById('val-cf'),df:document.getElementById('val-df'),n:document.getElementById('val-n'),mc:document.getElementById('val-mc'),mcs:document.getElementById('val-mcs'),fc:document.getElementById('val-fc')};
const ro={p:document.getElementById('ro-p'),qd:document.getElementById('ro-qd'),qf:document.getElementById('ro-qf'),profit:document.getElementById('ro-profit'),cs:document.getElementById('ro-cs'),dwl:document.getElementById('ro-dwl')};

const toggles={cs:true,ps:true,dwl:true,profit:false,atc:false,comp:false};
document.querySelectorAll('.toggle-btn').forEach(btn=>{btn.addEventListener('click',()=>{toggles[btn.dataset.key]=!toggles[btn.dataset.key];btn.classList.toggle('active',toggles[btn.dataset.key]);});});

const MAX_Q=120,MAX_P=120;
const M={top:30,right:28,bottom:40,left:50};
let dpr=1,wL,hL,wR,hR,pWL,pHL,pWR,pHR;
let mxL=-1,myL=-1,mxR=-1,myR=-1;
let params={a:100,b:1,cF:20,dF:1.5,n:5,mc0:10,mcS:0.3,FC:50};
let target={...params};

function resize(){
  dpr=window.devicePixelRatio||1;
  const rL=cL.parentElement.getBoundingClientRect();const rR=cR.parentElement.getBoundingClientRect();
  cL.width=rL.width*dpr;cL.height=rL.height*dpr;cR.width=rR.width*dpr;cR.height=rR.height*dpr;
  wL=rL.width;hL=rL.height;wR=rR.width;hR=rR.height;
  pWL=wL-M.left-M.right;pHL=hL-M.top-M.bottom;pWR=wR-M.left-M.right;pHR=hR-M.top-M.bottom;
  const gc=document.getElementById('graphs-card').getBoundingClientRect();
  cO.width=gc.width*dpr;cO.height=gc.height*dpr;cO.style.width=gc.width+'px';cO.style.height=gc.height+'px';
}

function qXL(q){return M.left+(q/MAX_Q)*pWL;}
function qXR(q){return M.left+(q/MAX_Q)*pWR;}
function pYL(p){return M.top+(1-p/MAX_P)*pHL;}
function pYR(p){return M.top+(1-p/MAX_P)*pHR;}

function drawGrid(ctx,w,h,pW,pH,qX,pY,xLbl){
  ctx.save();
  for(let q=20;q<MAX_Q;q+=20){ctx.strokeStyle='rgba(0,0,0,0.05)';ctx.lineWidth=dpr;ctx.beginPath();ctx.moveTo(qX(q)*dpr,M.top*dpr);ctx.lineTo(qX(q)*dpr,(h-M.bottom)*dpr);ctx.stroke();}
  for(let p=20;p<MAX_P;p+=20){ctx.strokeStyle='rgba(0,0,0,0.05)';ctx.lineWidth=dpr;ctx.beginPath();ctx.moveTo(M.left*dpr,pY(p)*dpr);ctx.lineTo((w-M.right)*dpr,pY(p)*dpr);ctx.stroke();}
  ctx.strokeStyle='#333';ctx.lineWidth=1.5*dpr;
  ctx.beginPath();ctx.moveTo(M.left*dpr,M.top*dpr);ctx.lineTo(M.left*dpr,(h-M.bottom)*dpr);ctx.lineTo((w-M.right)*dpr,(h-M.bottom)*dpr);ctx.stroke();
  ctx.fillStyle='#999';ctx.font=`500 ${10*dpr}px 'JetBrains Mono',monospace`;
  ctx.textAlign='center';ctx.textBaseline='top';
  for(let q=20;q<=MAX_Q;q+=20)ctx.fillText(q,qX(q)*dpr,(h-M.bottom+6)*dpr);
  ctx.textAlign='right';ctx.textBaseline='middle';
  for(let p=20;p<=MAX_P;p+=20)ctx.fillText(p,(M.left-8)*dpr,pY(p)*dpr);
  ctx.save();ctx.translate(14*dpr,(M.top+pH/2)*dpr);ctx.rotate(-Math.PI/2);ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=`600 ${11*dpr}px 'IBM Plex Sans',sans-serif`;ctx.fillStyle='#555';ctx.fillText('Price',0,0);ctx.restore();
  ctx.restore();
}

function drawCurve(ctx,fn,qX,pY,color,w,dash,label,mq){
  const maxq=mq!=null?mq:MAX_Q;
  ctx.save();ctx.strokeStyle=color;ctx.lineWidth=w*dpr;
  if(dash)ctx.setLineDash(dash.map(d=>d*dpr));
  const pts=[];
  for(let i=0;i<=400;i++){const q=(i/400)*maxq;const p=fn(q);if(p<0)break;if(q>=0&&p<=MAX_P)pts.push({q,p});}
  if(pts.length>1){
    ctx.beginPath();ctx.moveTo(qX(pts[0].q)*dpr,pY(pts[0].p)*dpr);
    for(let i=1;i<pts.length;i++)ctx.lineTo(qX(pts[i].q)*dpr,pY(pts[i].p)*dpr);
    ctx.stroke();
    if(label){
      const last=pts[pts.length-1];ctx.setLineDash([]);ctx.font=`700 ${12*dpr}px 'IBM Plex Sans',sans-serif`;ctx.fillStyle=color;
      let lx=qX(last.q)*dpr+4*dpr, ly=pY(last.p)*dpr;
      ctx.textAlign='left';ctx.textBaseline='middle';
      if(last.p<=5)ly-=12*dpr;if(last.q>=maxq-2){lx-=8*dpr;ly-=12*dpr;ctx.textAlign='right';}
      ctx.fillText(label,lx,ly);
    }
  }
  ctx.restore();
}

function drawKinked(ctx,model,qX,pY,color,w){
  const Qk=model.kinkQ();const{A,B}=model.upperSeg();
  ctx.save();ctx.strokeStyle=color;ctx.lineWidth=w*dpr;
  let pts=[];for(let i=0;i<=150;i++){const q=(i/150)*Qk;const p=A-B*q;if(p<0)break;if(p<=MAX_P&&q<=MAX_Q)pts.push({q,p});}
  if(pts.length>1){ctx.beginPath();ctx.moveTo(qX(pts[0].q)*dpr,pY(pts[0].p)*dpr);for(let i=1;i<pts.length;i++)ctx.lineTo(qX(pts[i].q)*dpr,pY(pts[i].p)*dpr);ctx.stroke();}
  pts=[];for(let i=0;i<=150;i++){const q=Qk+(i/150)*(MAX_Q-Qk);const p=model.a-model.b*q;if(p<0)break;if(p<=MAX_P)pts.push({q,p});}
  if(pts.length>1){ctx.beginPath();ctx.moveTo(qX(pts[0].q)*dpr,pY(pts[0].p)*dpr);for(let i=1;i<pts.length;i++)ctx.lineTo(qX(pts[i].q)*dpr,pY(pts[i].p)*dpr);ctx.stroke();const last=pts[pts.length-1];ctx.font=`700 ${12*dpr}px 'IBM Plex Sans',sans-serif`;ctx.fillStyle=color;let lx=qX(last.q)*dpr+4*dpr,ly=pY(last.p)*dpr;ctx.textAlign='left';ctx.textBaseline='middle';if(last.p<=5)ly-=12*dpr;ctx.fillText('D(p)=Dr',lx,ly);}
  const kP=model.residualDemandP(Qk);
  if(Qk>0&&Qk<MAX_Q&&kP>0&&kP<MAX_P){ctx.beginPath();ctx.arc(qX(Qk)*dpr,pY(kP)*dpr,3*dpr,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();}
  const lq=Math.min(Qk*0.55,MAX_Q-10);const lp=A-B*lq;if(lp>5&&lp<MAX_P-5){ctx.font=`700 ${12*dpr}px 'IBM Plex Sans',sans-serif`;ctx.fillStyle=color;ctx.textAlign='left';ctx.textBaseline='bottom';ctx.fillText('Dr',qX(lq)*dpr+5*dpr,pY(lp)*dpr-3*dpr);}
  ctx.restore();
}

function fillReg(ctx,fT,fB,qs,qe,qX,pY,col){if(qe<=qs)return;ctx.save();ctx.fillStyle=col;ctx.beginPath();const S=100;let first=true;for(let i=0;i<=S;i++){const q=qs+(i/S)*(qe-qs);const p=Math.min(Math.max(fT(q),0),MAX_P);if(first){ctx.moveTo(qX(q)*dpr,pY(p)*dpr);first=false;}else ctx.lineTo(qX(q)*dpr,pY(p)*dpr);}for(let i=S;i>=0;i--){const q=qs+(i/S)*(qe-qs);const p=Math.min(Math.max(fB(q),0),MAX_P);ctx.lineTo(qX(q)*dpr,pY(p)*dpr);}ctx.closePath();ctx.fill();ctx.restore();}
function centroid(fT,fB,qs,qe){if(qe<=qs)return{cx:(qs+qe)/2,cy:50};let tA=0,sQ=0,sP=0;for(let i=0;i<40;i++){const q=qs+(i+0.5)/40*(qe-qs);const dq=(qe-qs)/40;const t=Math.min(fT(q),MAX_P),b=Math.max(fB(q),0),h=Math.max(t-b,0);tA+=h*dq;sQ+=q*h*dq;sP+=((t+b)/2)*h*dq;}if(tA<0.01)return{cx:(qs+qe)/2,cy:50};return{cx:sQ/tA,cy:sP/tA};}
function areaLbl(ctx,t,cx,cy,qX,pY,col){if(cx<0||cx>MAX_Q||cy<0||cy>MAX_P)return;ctx.save();ctx.font=`700 ${13*dpr}px 'IBM Plex Sans',sans-serif`;ctx.fillStyle=col;ctx.globalAlpha=0.8;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(t,qX(cx)*dpr,pY(cy)*dpr);ctx.restore();}
function ddash(ctx,x1,y1,x2,y2,col){ctx.save();ctx.strokeStyle=col||'#000';ctx.lineWidth=1.5*dpr;ctx.setLineDash([4*dpr,3*dpr]);ctx.beginPath();ctx.moveTo(x1*dpr,y1*dpr);ctx.lineTo(x2*dpr,y2*dpr);ctx.stroke();ctx.restore();}
function dot(ctx,qX,pY,q,p,r,col){ctx.save();ctx.beginPath();ctx.arc(qX(q)*dpr,pY(p)*dpr,r*dpr,0,Math.PI*2);ctx.fillStyle=col||'#333';ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=2*dpr;ctx.stroke();ctx.restore();}

function drawOverlay(model,eq){
  const gc=document.getElementById('graphs-card');const gcR=gc.getBoundingClientRect();const lR=cL.parentElement.getBoundingClientRect();const rR=cR.parentElement.getBoundingClientRect();
  xO.clearRect(0,0,cO.width,cO.height);
  const lAxisL=lR.left-gcR.left+M.left;const rAxisR=rR.left-gcR.left+wR-M.right;
  function pYov(p){return M.top+(1-p/MAX_P)*pHL;}
  const lines=[];if(eq.Qd>0&&eq.Pd>0&&eq.Pd<MAX_P)lines.push({p:eq.Pd,label:'P*',color:'#333'});if(params.cF>0&&params.cF<MAX_P)lines.push({p:params.cF,label:'p̄',color:'#333'});
  const pC=model.competitivePrice();if(pC>0&&pC<MAX_P)lines.push({p:pC,label:'Pc',color:'#777'});
  lines.sort((a,b)=>b.p-a.p);
  const seenL=[],seenR=[],gap=12;
  for(const l of lines){
    let yL=pYov(l.p),yR=yL;
    for(const s of seenL)if(Math.abs(yL-s)<gap)yL=s+gap;seenL.push(yL);
    for(const s of seenR)if(Math.abs(yR-s)<gap)yR=s+gap;seenR.push(yR);
    xO.save();xO.strokeStyle=l.color;xO.lineWidth=1.2*dpr;xO.setLineDash([4*dpr,4*dpr]);xO.globalAlpha=0.4;xO.beginPath();xO.moveTo(lAxisL*dpr,pYov(l.p)*dpr);xO.lineTo(rAxisR*dpr,pYov(l.p)*dpr);xO.stroke();xO.restore();
    xO.save();xO.font=`600 ${10*dpr}px 'IBM Plex Sans',sans-serif`;xO.fillStyle=l.color;
    xO.textAlign='right';xO.textBaseline='middle';xO.fillText(l.label,(lAxisL-6)*dpr,yL*dpr);
    xO.textAlign='left';xO.fillText(l.label,(rAxisR+6)*dpr,yR*dpr);xO.restore();
  }
}

function draw(){
  const t=0.25;for(const k in params)params[k]=params[k]+(target[k]-params[k])*t;
  const model=new DFModel(params);const eq=model.solve();
  const mcDom=q=>model.mcAt(q);const atcDom=q=>model.atcAt(q);const resDem=q=>model.residualDemandP(q);const demFn=q=>model.a-model.b*q;const Qk=model.kinkQ();

  xR.clearRect(0,0,cR.width,cR.height);drawGrid(xR,wR,hR,pWR,pHR,qXR,pYR,'Dominant firm output, Q');
  if(toggles.cs&&eq.Qd>0){fillReg(xR,resDem,()=>eq.Pd,0,eq.Qd,qXR,pYR,'rgba(66,133,244,0.18)');const c=centroid(resDem,()=>eq.Pd,0,eq.Qd);areaLbl(xR,'CS',c.cx,c.cy,qXR,pYR,'#4285f4');}
  if(toggles.ps&&eq.Qd>0){fillReg(xR,()=>eq.Pd,mcDom,0,eq.Qd,qXR,pYR,'rgba(52,168,83,0.18)');const c=centroid(()=>eq.Pd,mcDom,0,eq.Qd);areaLbl(xR,'PS_d',c.cx,c.cy,qXR,pYR,'#34a853');}
  if(toggles.dwl&&eq.Qd>0&&eq.QdComp>eq.Qd){let end=eq.QdComp;for(let q=eq.Qd;q<=eq.QdComp+1;q+=0.2){if(resDem(q)<=mcDom(q)){end=q;break;}}xR.save();xR.fillStyle='rgba(234,67,53,0.18)';xR.beginPath();const vp=[];for(let i=0;i<=60;i++){const q=eq.Qd+(i/60)*(end-eq.Qd);const pT=resDem(q),pB=mcDom(q);if(pT>pB)vp.push({q,pT:Math.min(pT,MAX_P),pB:Math.max(pB,0)});}if(vp.length>1){xR.moveTo(qXR(vp[0].q)*dpr,pYR(vp[0].pT)*dpr);for(let i=1;i<vp.length;i++)xR.lineTo(qXR(vp[i].q)*dpr,pYR(vp[i].pT)*dpr);for(let i=vp.length-1;i>=0;i--)xR.lineTo(qXR(vp[i].q)*dpr,pYR(vp[i].pB)*dpr);xR.closePath();xR.fill();const c=centroid(resDem,mcDom,vp[0].q,vp[vp.length-1].q);areaLbl(xR,'DWL',c.cx,c.cy,qXR,pYR,'#ea4335');}xR.restore();}
  if(toggles.profit&&eq.Qd>0){const atcV=atcDom(eq.Qd);if(eq.Pd>atcV){fillReg(xR,()=>eq.Pd,()=>atcV,0,eq.Qd,qXR,pYR,'rgba(251,188,4,0.22)');const c=centroid(()=>eq.Pd,()=>atcV,0,eq.Qd);areaLbl(xR,'πd',c.cx,c.cy,qXR,pYR,'#e8a000');}}
  if(Qk>0)drawCurve(xR,demFn,qXR,pYR,'#c62828',2,[5,4],null,Qk);
  drawKinked(xR,model,qXR,pYR,'#c62828',2.5);
  drawCurve(xR,q=>model.a-2*model.b*q,qXR,pYR,'#e65100',2,[5,4],null); /* Simple MR for now */
  drawCurve(xR,mcDom,qXR,pYR,'#2e7d32',2.5,null,'MCd');
  if(toggles.atc)drawCurve(xR,atcDom,qXR,pYR,'#6a1b9a',2,null,'ACd');
  if(toggles.comp&&eq.QdComp>0){ddash(xR,qXR(eq.QdComp),pYR(eq.PdComp),qXR(eq.QdComp),hR-M.bottom,'#555');dot(xR,qXR,pYR,eq.QdComp,eq.PdComp,4,'#555');}
  if(eq.Qd>0){ddash(xR,qXR(eq.Qd),pYR(eq.Pd),qXR(eq.Qd),hR-M.bottom,'#333');dot(xR,qXR,pYR,eq.Qd,eq.mcQd,4,'#333');dot(xR,qXR,pYR,eq.Qd,eq.Pd,5,'#333');}

  xL.clearRect(0,0,cL.width,cL.height);drawGrid(xL,wL,hL,pWL,pHL,qXL,pYL,'Fringe firm output, q');
  const fMC=q=>model.fringeFirmMC(q), fATC=q=>model.fringeFirmATC(q);
  if(toggles.profit&&eq.qf>0&&eq.Pd>0){const fA=fATC(eq.qf);if(eq.Pd>fA){fillReg(xL,()=>eq.Pd,()=>fA,0,eq.qf,qXL,pYL,'rgba(251,188,4,0.22)');const c=centroid(()=>eq.Pd,()=>fA,0,eq.qf);areaLbl(xL,'πf',c.cx,c.cy,qXL,pYL,'#e8a000');}}
  drawCurve(xL,demFn,qXL,pYL,'#c62828',2,null,'D(p)');
  drawCurve(xL,q=>model.fringeSupplyP(q),qXL,pYL,'#2e7d32',2.2,null,'S(p)');
  drawCurve(xL,fMC,qXL,pYL,'#0277bd',2.5,null,'MCf');
  if(toggles.atc)drawCurve(xL,fATC,qXL,pYL,'#4a148c',2,null,'ACf');
  const pC=model.competitivePrice(),qcTotal=model.marketDemandQ(pC);
  if(pC>0&&pC<MAX_P&&qcTotal>0)dot(xL,qXL,pYL,qcTotal,pC,4,'#555');
  if(eq.qf>0&&eq.Pd>0){ddash(xL,qXL(eq.qf),pYL(eq.Pd),qXL(eq.qf),hL-M.bottom,'#333');dot(xL,qXL,pYL,eq.qf,eq.Pd,5,'#333');}

  drawOverlay(model,eq);
  if(eq.Qd>0){ro.p.textContent=Math.round(eq.Pd);ro.qd.textContent=eq.Qd.toFixed(1);ro.qf.textContent=eq.Qf.toFixed(1);ro.profit.textContent=Math.round(eq.profitD);ro.cs.textContent=Math.round(eq.CS);ro.dwl.textContent=Math.round(eq.DWL);}
  else{ro.p.textContent='—';ro.qd.textContent='0';ro.qf.textContent='0';ro.profit.textContent='0';ro.cs.textContent='0';ro.dwl.textContent='0';}

  requestAnimationFrame(draw);
}

function onSlider(){
  target.a=+sl.a.value;vl.a.textContent=sl.a.value;target.b=+sl.b.value;vl.b.textContent=(+sl.b.value).toFixed(2);
  target.cF=+sl.cf.value;vl.cf.textContent=sl.cf.value;target.dF=+sl.df.value;vl.df.textContent=(+sl.df.value).toFixed(2);
  target.n=+sl.n.value;vl.n.textContent=sl.n.value;target.mc0=+sl.mc.value;vl.mc.textContent=sl.mc.value;
  target.mcS=+sl.mcs.value;vl.mcs.textContent=(+sl.mcs.value).toFixed(2);target.FC=+sl.fc.value;vl.fc.textContent=sl.fc.value;
}
Object.values(sl).forEach(s=>s.addEventListener('input',onSlider));
window.addEventListener('resize',resize);
resize();onSlider();draw();
</script>
</body>
</html>
"""

# 3. Embed the HTML into Streamlit
components.html(html_code, height=850, scrolling=False)
