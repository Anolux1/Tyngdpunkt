// Kalkylatorerna. Samma formler som appen (tyngdpunkt/src/engine/nutrition.ts och progression.ts):
// Mifflin–St Jeor × aktivitetsfaktor, protein per kilo efter mål (målvikten vid deff), Epleys formel för 1RM.
const $ = (id) => document.getElementById(id);
const fmt = (n) => Math.round(n).toLocaleString('sv-SE');
const dec = (n) => String(n).replace('.', ',');
const r5 = (n) => Math.round(n / 5) * 5;
const r50 = (n) => Math.round(n / 50) * 50;
const num = (id) => parseFloat(String($(id).value).replace(',', '.')) || 0;

function kcalPage() {
  let sex = 'man';
  document.querySelectorAll('#sex button').forEach((b) => (b.onclick = () => {
    document.querySelectorAll('#sex button').forEach((e) => e.classList.remove('on'));
    b.classList.add('on'); sex = b.dataset.v; calc();
  }));
  const PACE = { fett: [0.25, 0.5, 0.75], muskler: [0.1, 0.25, 0.5] };
  const act = (d) => (d <= 2 ? 1.4 : d === 3 ? 1.45 : d === 4 ? 1.5 : 1.55);
  function setPace() {
    const g = $('goal').value;
    $('paceBox').style.display = PACE[g] ? '' : 'none';
    if (PACE[g]) $('pace').innerHTML = PACE[g].map((p, i) => `<option ${i === 1 ? 'selected' : ''} value="${p}">${dec(p)}</option>`).join('');
  }
  function calc() {
    const a = num('age'), h = num('h'), w = num('w'), d = +$('days').value, g = $('goal').value, p = PACE[g] ? +$('pace').value : 0;
    if (!a || !h || !w) { $('kTarget').textContent = '–'; $('kTdee').textContent = '–'; $('kCalc').innerHTML = ''; return; }
    const bmr = 10 * w + 6.25 * h - 5 * a + (sex === 'man' ? 5 : -161), f = act(d), tdee = bmr * f;
    const dir = g === 'fett' ? -1 : g === 'muskler' ? 1 : 0, adj = (dir * p * 7700) / 7, t = r50(tdee + adj);
    $('kTarget').textContent = fmt(t); $('kTdee').textContent = fmt(tdee);
    $('kCalc').innerHTML = `<div><span>Vilan (Mifflin–St Jeor)</span><b>${fmt(bmr)} kcal</b></div>`
      + `<div><span>× ${dec(f)} för ${d} pass i veckan</span><b>${fmt(tdee)} kcal</b></div>`
      + (dir ? `<div><span>${dir < 0 ? '−' : '+'} ${dec(p)} kg/vecka × 7 700 ÷ 7</span><b>${dir < 0 ? '−' : '+'}${fmt(Math.abs(adj))} kcal</b></div>` : '')
      + `<div><span>Avrundat till närmaste 50</span><b>${fmt(t)} kcal</b></div>`;
  }
  ['age', 'h', 'w', 'days', 'pace'].forEach((i) => ($(i).oninput = calc));
  $('goal').onchange = () => { setPace(); calc(); };
  setPace(); calc();
}

function protPage() {
  const PK = { fett: 2.2, muskler: 2.0, underhalla: 1.8 };
  const GN = { fett: 'gå ner i fett', muskler: 'bygga muskler', underhalla: 'ligga kvar' };
  // Livsmedelsverkets livsmedelsdatabas, g protein per 100 g: Kvarg naturell 0,2 % 10,0; Kyckling bröstfilé stekt u. skinn 23,0;
  // Ägg kokt 12,1 (55 g/st); Havregrynsgröt kokt m. mjölk 4,1 (3 dl ≈ 300 g); Färskost cottage cheese 4 % 13,4; Tonfisk i vatten avrunnen 24,1.
  const FOOD = [['Kvarg naturell, 250 g', '25 g'], ['Kycklingfilé, stekt, 125 g', '29 g'], ['Ägg, kokt, 3 st', '20 g'],
    ['Havregrynsgröt med mjölk, 3 dl', '12 g'], ['Cottage cheese, 200 g', '27 g'], ['Tonfisk i vatten, 1 burk (130 g)', '31 g']];
  $('pFood').innerHTML = FOOD.map((f) => `<tr><td>${f[0]}</td><td class="n">${f[1]}</td></tr>`).join('');
  function calc() {
    const w = num('pw'), g = $('pg').value, gw = num('pgw'), m = +$('pm').value;
    $('pgwBox').style.display = g === 'fett' ? '' : 'none';
    if (!w) { $('pT').textContent = '–'; $('pM').textContent = '–'; $('pCalc').innerHTML = ''; return; }
    const base = g === 'fett' && gw && gw < w ? gw : w, t = r5(base * PK[g]);
    $('pT').textContent = fmt(t); $('pM').textContent = fmt(t / m);
    $('pCalc').innerHTML = `<div><span>${base === w ? 'Din vikt' : 'Din målvikt'} × ${dec(PK[g])} g/kg för att ${GN[g]}</span><b>${dec(base)} × ${dec(PK[g])}</b></div>`
      + `<div><span>Avrundat till närmaste 5 g</span><b>${fmt(t)} g</b></div>`
      + (base !== w ? '<div><span>Vid deff räknas proteinet på målvikten</span><b></b></div>' : '');
  }
  ['pw', 'pgw', 'pm'].forEach((i) => ($(i).oninput = calc));
  $('pg').onchange = calc;
  calc();
}

function rmPage() {
  const half = (n) => (Math.round(n * 2) / 2).toLocaleString('sv-SE');
  function calc() {
    const w = num('rw'), r = Math.round(num('rr'));
    if (!w || r <= 0) { $('rmT').textContent = '–'; $('rmCalc').innerHTML = ''; $('rmTab').innerHTML = ''; return; }
    const mx = r === 1 ? w : w * (1 + r / 30);
    $('rmT').textContent = half(mx);
    $('rmCalc').innerHTML = r > 1
      ? `<div><span>Epleys formel: vikt × (1 + reps ÷ 30)</span><b>${dec(w)} × (1 + ${r} ÷ 30)</b></div>`
        + (r > 10 ? '<div><span>Över 10 reps blir uppskattningen osäkrare</span><b></b></div>' : '<div><span>Säkrast mellan 3 och 10 reps</span><b></b></div>')
      : '<div><span>Ett set med 1 rep är ditt max</span><b></b></div>';
    $('rmTab').innerHTML = '<tr><th>Reps</th><th>Vikt</th><th>Andel av max</th></tr>'
      + [1, 3, 5, 8, 10, 12].map((n) => { const v = n === 1 ? mx : mx / (1 + n / 30); return `<tr><td>${n}</td><td class="n">${half(v)} kg</td><td>${Math.round((v / mx) * 100)} %</td></tr>`; }).join('');
  }
  ['rw', 'rr'].forEach((i) => ($(i).oninput = calc));
  calc();
}
