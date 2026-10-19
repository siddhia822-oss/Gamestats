const $ = (id) => document.getElementById(id);
const REQUIRED_NUMERIC = ["Kills","Deaths","Assists","Wins","Matches","Playtime_Hours","FPS_Avg","FPS_Min","CPU_Usage","GPU_Usage","RAM_Usage_GB","GPU_Temp","Score"];
let allRows = [];
let filteredRows = [];
let headers = [];

function parseCSV(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i], next = text[i + 1];
    if (ch === '"' && quoted && next === '"') { field += '"'; i++; }
    else if (ch === '"') quoted = !quoted;
    else if (ch === ',' && !quoted) { row.push(field); field = ""; }
    else if ((ch === '\n' || ch === '\r') && !quoted) {
      if (ch === '\r' && next === '\n') i++;
      row.push(field);
      if (row.some(v => v.trim() !== "")) rows.push(row);
      row = []; field = "";
    } else field += ch;
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  if (!rows.length) return {headers: [], data: []};
  const hs = rows.shift().map(h => h.trim().replace(/^\uFEFF/, ""));
  const data = rows.map(r => {
    const obj = {};
    hs.forEach((h, i) => {
      const raw = (r[i] ?? "").trim();
      if (raw === "" || raw.toLowerCase() === "nan" || raw.toLowerCase() === "null") obj[h] = null;
      else if (raw !== "" && Number.isFinite(Number(raw))) obj[h] = Number(raw);
      else obj[h] = raw;
    });
    return obj;
  });
  return {headers: hs, data};
}
function num(row, key) {
  const v = row[key];
  return v === null || v === undefined || v === "" || !Number.isFinite(Number(v)) ? null : Number(v);
}
function mean(rows, key) {
  const vals = rows.map(r => num(r,key)).filter(v => v !== null);
  return vals.length ? vals.reduce((a,b)=>a+b,0)/vals.length : null;
}
function fmt(value, suffix="") { return value === null || !Number.isFinite(value) ? "N/A" : `${value.toFixed(1)}${suffix}`; }
function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}
function loadRows(rows, hs, label="CSV loaded") {
  allRows = rows; headers = hs;
  $("dataStatus").textContent = `${label} · ${rows.length} rows`;
  const modes = [...new Set(rows.map(r => r.Game_Mode).filter(v => v !== null && v !== undefined && v !== ""))].sort((a,b)=>String(a).localeCompare(String(b)));
  $("modeFilter").innerHTML = '<option value="all">All modes</option>' + modes.map(m=>`<option value="${escapeHTML(m)}">${escapeHTML(m)}</option>`).join("");
  updateDashboard();
}
function applyFilters() {
  const mode = $("modeFilter").value;
  const search = $("playerSearch").value.trim().toLowerCase();
  filteredRows = allRows.filter(r => {
    const modeOK = mode === "all" || String(r.Game_Mode ?? "") === mode;
    const playerOK = !search || String(r.Player ?? "").toLowerCase().includes(search);
    return modeOK && playerOK;
  });
}
function updateDashboard() {
  applyFilters();
  $("totalSessions").textContent = filteredRows.length.toLocaleString();
  $("avgFps").textContent = fmt(mean(filteredRows,"FPS_Avg"));
  $("avgCpu").textContent = fmt(mean(filteredRows,"CPU_Usage"), "%");
  $("avgGpu").textContent = fmt(mean(filteredRows,"GPU_Usage"), "%");
  drawBarChart("fpsChart", filteredRows.slice(0,20).map(r=>num(r,"FPS_Avg")), "FPS", "#a78bfa");
  drawBarChart("usageChart", [mean(filteredRows,"CPU_Usage"),mean(filteredRows,"GPU_Usage")], "Usage %", "#65a7ff", ["CPU","GPU"]);
  drawLineChart("tempChart", filteredRows.slice(0,40).map(r=>num(r,"GPU_Temp")), "#ffb36b");
  drawLineChart("ramChart", filteredRows.slice(0,40).map(r=>num(r,"RAM_Usage_GB")), "#4bd4a0");
  renderLeaderboard();
  renderDataTable();
}
function canvasFor(id) {
  const host = $(id); host.innerHTML = "";
  const canvas = document.createElement("canvas");
  const rect = host.getBoundingClientRect();
  const width = Math.max(250, rect.width || 500), height = Math.max(150, rect.height || 190);
  const dpr = window.devicePixelRatio || 1;
  canvas.width = width*dpr; canvas.height = height*dpr;
  canvas.style.width = "100%"; canvas.style.height = "100%";
  host.appendChild(canvas);
  const ctx = canvas.getContext("2d"); ctx.scale(dpr,dpr);
  return {ctx,width,height};
}
function drawBarChart(id, values, label, color, labels=null) {
  const valid = values.filter(v=>v!==null && Number.isFinite(v));
  if (!valid.length) { $(id).innerHTML = '<div class="empty">No reported data available</div>'; return; }
  const {ctx,width:w,height:h} = canvasFor(id);
  const pad={l:30,r:8,t:10,b:27}, chartH=h-pad.t-pad.b, chartW=w-pad.l-pad.r;
  const max=Math.max(1,...valid)*1.15;
  ctx.strokeStyle="#283244"; ctx.fillStyle="#7f8ba0"; ctx.font="10px DM Sans, sans-serif";
  for(let i=0;i<4;i++){const y=pad.t+chartH*i/3;ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(w-pad.r,y);ctx.stroke();ctx.fillText(Math.round(max*(1-i/3)).toString(),2,y+3);}
  const gap=values.length>2?4:22, barW=Math.max(5,(chartW-gap*Math.max(0,values.length-1))/values.length);
  values.forEach((v,i)=>{
    if(v===null||!Number.isFinite(v))return;
    const bh=Math.max(2,(v/max)*chartH), x=pad.l+i*(barW+gap), y=pad.t+chartH-bh;
    ctx.fillStyle=color; roundRect(ctx,x,y,barW,bh,4); 
    ctx.fillStyle="#8995a8";ctx.textAlign="center";
    const text=labels?labels[i]:(i+1);
    if(values.length<=2 || i%2===0)ctx.fillText(String(text),x+barW/2,h-8);
  });
  ctx.textAlign="left";
}
function drawLineChart(id, values, color) {
  const valid=values.map((v,i)=>({v,i})).filter(o=>o.v!==null&&Number.isFinite(o.v));
  if(!valid.length){$(id).innerHTML='<div class="empty">No reported data available</div>';return;}
  const {ctx,width:w,height:h}=canvasFor(id), pad={l:30,r:8,t:12,b:18};
  const vals=valid.map(o=>o.v), min=Math.min(...vals), max=Math.max(...vals), span=(max-min)||1;
  const x=i=>pad.l+(i/Math.max(1,values.length-1))*(w-pad.l-pad.r);
  const y=v=>pad.t+(1-(v-min)/span)*(h-pad.t-pad.b);
  ctx.strokeStyle="#283244";ctx.fillStyle="#7f8ba0";ctx.font="10px DM Sans, sans-serif";
  for(let i=0;i<3;i++){let yy=pad.t+(h-pad.t-pad.b)*i/2;ctx.beginPath();ctx.moveTo(pad.l,yy);ctx.lineTo(w-pad.r,yy);ctx.stroke();}
  ctx.beginPath();valid.forEach((o,j)=>{if(j===0)ctx.moveTo(x(o.i),y(o.v));else ctx.lineTo(x(o.i),y(o.v));});
  ctx.strokeStyle=color;ctx.lineWidth=2;ctx.stroke();
  valid.forEach(o=>{ctx.beginPath();ctx.arc(x(o.i),y(o.v),2.5,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();});
  ctx.fillStyle="#8c98aa";ctx.fillText(max.toFixed(0),2,14);ctx.fillText(min.toFixed(0),2,h-6);
}
function roundRect(ctx,x,y,w,h,r){const rr=Math.min(r,w/2,h/2);ctx.beginPath();ctx.moveTo(x+rr,y);ctx.arcTo(x+w,y,x+w,y+h,rr);ctx.arcTo(x+w,y+h,x,y+h,rr);ctx.arcTo(x,y+h,x,y,rr);ctx.arcTo(x,y,x+w,y,rr);ctx.closePath();ctx.fill();}
function renderLeaderboard() {
  const body=$("leaderboardBody");
  if(!headers.includes("Player") || !headers.includes("Score")) {
    body.innerHTML='<tr><td colspan="6" class="empty-cell">CSV needs Player and Score columns for the leaderboard.</td></tr>';return;
  }
  const groups=new Map();
  filteredRows.forEach(r=>{
    if(r.Player===null||r.Player===undefined||r.Score===null)return;
    const name=String(r.Player);
    if(!groups.has(name))groups.set(name,{scores:[],kills:0,deaths:0,assists:0,wins:0,matches:0});
    const g=groups.get(name);g.scores.push(Number(r.Score));
    g.kills+=num(r,"Kills")||0;g.deaths+=num(r,"Deaths")||0;g.assists+=num(r,"Assists")||0;g.wins+=num(r,"Wins")||0;g.matches+=num(r,"Matches")||0;
  });
  const ranked=[...groups.entries()].map(([player,g])=>({player,sessions:g.scores.length,score:g.scores.reduce((a,b)=>a+b,0)/g.scores.length,kda:(g.kills+g.assists)/(g.deaths||1),win:g.matches?g.wins/g.matches*100:null})).sort((a,b)=>b.score-a.score).slice(0,10);
  if(!ranked.length){body.innerHTML='<tr><td colspan="6" class="empty-cell">No score values available.</td></tr>';return;}
  body.innerHTML=ranked.map((r,i)=>`<tr><td class="rank">${String(i+1).padStart(2,"0")}</td><td class="player-cell">${escapeHTML(r.player)}</td><td>${r.sessions}</td><td>${r.score.toFixed(1)}</td><td>${r.kda.toFixed(2)}</td><td>${fmt(r.win,"%")}</td></tr>`).join("");
}
function renderDataTable() {
  $("rowCount").textContent=`${filteredRows.length} ROWS`;
  $("tableInfo").textContent=`Showing ${Math.min(50,filteredRows.length)} of ${filteredRows.length} filtered rows`;
  const shown=filteredRows.slice(0,50);
  $("dataHead").innerHTML=`<tr>${headers.map(h=>`<th>${escapeHTML(h)}</th>`).join("")}</tr>`;
  $("dataBody").innerHTML=shown.length?shown.map(r=>`<tr>${headers.map(h=>`<td>${r[h]===null||r[h]===undefined?"—":escapeHTML(r[h])}</td>`).join("")}</tr>`).join(""):`<tr><td colspan="${Math.max(1,headers.length)}" class="empty-cell">No rows match these filters.</td></tr>`;
}
function csvEscape(v) { const s=v===null||v===undefined?"":String(v); return /[",\r\n]/.test(s)?`"${s.replace(/"/g,'""')}"`:s; }
function exportCSV() {
  if(!headers.length){alert("Load a CSV first.");return;}
  const text=[headers.map(csvEscape).join(","),...filteredRows.map(r=>headers.map(h=>csvEscape(r[h])).join(","))].join("\r\n");
  const url=URL.createObjectURL(new Blob([text],{type:"text/csv;charset=utf-8;"}));
  const a=document.createElement("a");a.href=url;a.download="gamestats_filtered.csv";a.click();URL.revokeObjectURL(url);
}
$("csvUpload").addEventListener("change", async e=>{
  const file=e.target.files[0];if(!file)return;
  try{const parsed=parseCSV(await file.text());if(!parsed.headers.length)throw new Error("The file appears to be empty.");
    loadRows(parsed.data,parsed.headers,file.name);
  }catch(err){alert("Could not read this CSV: "+err.message);}
});
$("modeFilter").addEventListener("change",updateDashboard);
$("playerSearch").addEventListener("input",updateDashboard);
$("resetBtn").addEventListener("click",()=>{$("modeFilter").value="all";$("playerSearch").value="";updateDashboard();});
$("exportBtn").addEventListener("click",exportCSV);
$("exportBtnBottom").addEventListener("click",exportCSV);
window.addEventListener("resize",()=>{if(filteredRows.length)updateDashboard();});
fetch("game_stats.csv").then(r=>{if(!r.ok)throw new Error("No default CSV");return r.text();}).then(text=>{
  const parsed=parseCSV(text);loadRows(parsed.data,parsed.headers,"game_stats.csv");
}).catch(()=>{
  $("dataStatus").textContent="No default CSV · upload a file to start";
  $("totalSessions").textContent="0";$("avgFps").textContent="N/A";$("avgCpu").textContent="N/A";$("avgGpu").textContent="N/A";
  ["fpsChart","usageChart","tempChart","ramChart"].forEach(id=>$(id).innerHTML='<div class="empty">Upload a CSV to view this chart</div>');
});
