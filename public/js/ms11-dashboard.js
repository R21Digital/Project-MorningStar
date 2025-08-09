// --- helpers
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const fmt = (n) => typeof n === 'number' ? n.toLocaleString() : n;

function badge(health) {
  const map = {
    active:   'bg-emerald-700 text-emerald-100',
    degraded: 'bg-amber-700 text-amber-100',
    disabled: 'bg-zinc-700 text-zinc-200',
    error:    'bg-rose-700 text-rose-100',
  };
  return `<span class="text-xs px-2 py-0.5 rounded ${map[health]||map.disabled}">${health}</span>`;
}

// --- fetch & render modules
async function loadModules() {
  const res = await fetch('/api/modules/overview').catch(()=>fetch('/api/system/overview'));
  const { modules } = await res.json();

  const grid = $('#modulesGrid');
  grid.innerHTML = modules.map(m => `
    <div class="bg-zinc-900 border border-zinc-800 rounded p-4 hover:shadow transition">
      <div class="flex items-center justify-between">
        <div class="font-medium">${m.name}</div>
        ${badge(m.health)}
      </div>
      <p class="text-zinc-400 text-sm mt-1">${m.description}</p>
      <dl class="grid grid-cols-3 gap-2 mt-3">
        ${m.metrics.slice(0,3).map(mm => `
          <div class="bg-zinc-800 rounded p-2">
            <dt class="text-zinc-400 text-xs">${mm.label}</dt>
            <dd class="text-white">${fmt(mm.value)}</dd>
          </div>
        `).join('')}
      </dl>
      <div class="text-xs text-zinc-500 mt-2">Last: ${m.lastRunAt ? new Date(m.lastRunAt).toLocaleString() : '—'}</div>
    </div>
  `).join('');

  const active = modules.filter(m => m.health === 'active').length;
  const stats = [
    { label: 'Active Modules', value: active },
    { label: 'Total Modules', value: modules.length },
  ];
  $('#statsRow').innerHTML = stats.map(s => `
    <div class="bg-zinc-900 border border-zinc-800 rounded p-4">
      <div class="text-zinc-400 text-xs">${s.label}</div>
      <div class="text-white text-2xl font-bold">${fmt(s.value)}</div>
    </div>
  `).join('');
}

async function loadSystem() {
  const r = await fetch('/api/system/info');
  if (!r.ok) return;
  const s = await r.json();
  const cpuTile = document.createElement('div');
  cpuTile.className = 'bg-zinc-900 border border-zinc-800 rounded p-4';
  cpuTile.innerHTML = `
    <div class="text-zinc-400 text-xs">CPU</div>
    <div class="text-white text-2xl font-bold">${fmt(s.cpu)}</div>`;
  $('#statsRow').appendChild(cpuTile);

  const memTile = document.createElement('div');
  memTile.className = 'bg-zinc-900 border border-zinc-800 rounded p-4';
  memTile.innerHTML = `
    <div class="text-zinc-400 text-xs">Memory Used</div>
    <div class="text-white text-2xl font-bold">${fmt(s.memUsedPct)}%</div>`;
  $('#statsRow').appendChild(memTile);
}

// --- sessions
async function loadSessions() {
  const r = await fetch('/api/sessions');
  const { sessions } = await r.json();
  renderSessions(sessions);
}

function renderSessions(list) {
  const tbody = $('#sessionsTbody');
  tbody.innerHTML = list.map(s => `
    <tr class="border-t border-zinc-800">
      <td class="p-2">${s.id.slice(0,8)}</td>
      <td class="p-2">${s.character}</td>
      <td class="p-2">${s.profile}</td>
      <td class="p-2">${s.mode}</td>
      <td class="p-2">${s.status}</td>
      <td class="p-2 text-right">
        ${s.status === 'running' ? `<button data-stop="${s.id}" class="px-2 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-xs">Stop</button>` : ''}
      </td>
    </tr>
  `).join('');

  $$('#sessionsTbody [data-stop]').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const id = e.currentTarget.getAttribute('data-stop');
      await fetch(`/api/sessions/${id}`, { method: 'DELETE' });
    });
  });
}

// --- event wiring
$('#btnStartAll').addEventListener('click', () => fetch('/api/services/startAll', { method:'POST' }));
$('#btnStopAll').addEventListener('click',  () => fetch('/api/services/stopAll',  { method:'POST' }));
$('#btnLaunch').addEventListener('click', async () => {
  const body = {
    character: $('#inpCharacter').value || 'Player',
    profile:   $('#inpProfile').value   || 'legacy_tatooine_01',
    mode:      $('#selMode').value      || 'quest',
  };
  await fetch('/api/sessions', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
});

// --- Socket.IO live events
const socket = io();

const logs = [];
const logPane = $('#logPane');
function pushLog(line) {
  logs.push(line);
  while (logs.length > 200) logs.shift();
  logPane.textContent = logs.join('\n');
  logPane.scrollTop = logPane.scrollHeight;
}
$('#btnClearLog').addEventListener('click', () => { logs.length = 0; logPane.textContent = ''; });

socket.on('log', (e) => {
  pushLog(`[${(e.level||'info').toUpperCase()}] [${e.source}] ${e.msg}`);
});

socket.on('metric', (e) => {
  if (e.key === 'attachment') {
    const pill = $('#attachmentPill');
    const on = Number(e.value) === 1;
    pill.textContent = `Attachment: ${on ? 'Attached' : 'Detached'}`;
    pill.className = `text-xs px-2 py-1 rounded ${on ? 'bg-emerald-700' : 'bg-zinc-700'}`;
  }
});

socket.on('session', (_e) => {
  loadSessions();
});

// --- initial boot
(async function boot(){
  await loadModules();
  await loadSystem();
  await loadSessions();
})();


