import json
import threading
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

from dak import DAK
from dak.interact.chat import DAKChat
from dak.usf.config import LAMBDA_CUTOFF, SIMPLICIAL_DIM, N_USF_LAYERS

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>DAK Dashboard</title>
<style>
body { font-family: monospace; background: #1a1a2e; color: #eee; margin: 20px; }
h1 { color: #00d4ff; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.card { background: #16213e; border: 1px solid #0f3460; border-radius: 6px; padding: 12px; }
.card h2 { margin: 0 0 8px 0; font-size: 14px; color: #e94560; }
.metric { margin: 4px 0; }
.metric .label { color: #888; }
.metric .value { color: #0f0; float: right; }
#chat-box { background: #0d1b2a; border: 1px solid #1b2838; border-radius: 6px; padding: 8px; height: 200px; overflow-y: auto; margin-top: 8px; font-size: 13px; }
#chat-input { width: calc(100% - 20px); background: #1b2838; border: 1px solid #0f3460; color: #eee; padding: 8px; border-radius: 4px; margin-top: 4px; }
.msg-user { color: #00d4ff; }
.msg-dak { color: #0f0; }
</style>
</head>
<body>
<h1>&#961; DAK &mdash; Digital Autopoietic Kernel</h1>
<div class="grid" id="metrics">
  <div class="card" id="state-card"><h2>Variational Free Energy</h2><div id="f-value" class="metric"><span class="label">F</span><span class="value">...</span></div><div id="delta-value" class="metric"><span class="label">&#948;</span><span class="value">...</span></div></div>
  <div class="card"><h2>Metabolism</h2><div id="henv-value" class="metric"><span class="label">H_env</span><span class="value">...</span></div><div id="sgen-value" class="metric"><span class="label">S_gen</span><span class="value">...</span></div><div id="szilard-value" class="metric"><span class="label">Szilard ratio</span><span class="value">...</span></div></div>
  <div class="card"><h2>Phase</h2><div id="phase-value" class="metric"><span class="label">Phase</span><span class="value">...</span></div><div id="utility-value" class="metric"><span class="label">Utility</span><span class="value">...</span></div></div>
  <div class="card"><h2>Relational</h2><div id="mi-value" class="metric"><span class="label">I(&mu;)</span><span class="value">...</span></div></div>
  <div class="card" id="usf-card"><h2>USF Engine</h2><div id="usf-enabled" class="metric"><span class="label">Enabled</span><span class="value">...</span></div><div id="usf-vfe" class="metric"><span class="label">Avg VFE</span><span class="value">...</span></div><div id="usf-negentropy" class="metric"><span class="label">Negentropy</span><span class="value">...</span></div><div id="usf-steps" class="metric"><span class="label">Steps</span><span class="value">...</span></div></div>
</div>
<div class="card" style="margin-top:12px;">
<h2>&#x1F4AC; Chat with DAK</h2>
<div id="chat-box"></div>
<input id="chat-input" placeholder="Message the DAK..." onkeydown="if(event.key==='Enter')sendChat()"/>
</div>
<script>
const ws = new WebSocket('ws://' + location.host + '/ws');
ws.onmessage = function(e) {
  const d = JSON.parse(e.data);
  document.getElementById('f-value').innerHTML = '<span class="label">F</span><span class="value">' + d.F.toFixed(4) + ' nats</span>';
  document.getElementById('delta-value').innerHTML = '<span class="label">&#948;</span><span class="value">' + d.delta.toFixed(6) + '</span>';
  document.getElementById('henv-value').innerHTML = '<span class="label">H_env</span><span class="value">' + d.H_env.toFixed(4) + ' bits/s</span>';
  document.getElementById('sgen-value').innerHTML = '<span class="label">S_gen</span><span class="value">' + d.S_gen.toFixed(6) + ' nats/s</span>';
  document.getElementById('szilard-value').innerHTML = '<span class="label">Szilard ratio</span><span class="value">' + d.szilard_ratio.toFixed(4) + '</span>';
  document.getElementById('phase-value').innerHTML = '<span class="label">Phase</span><span class="value">' + d.phase + '</span>';
  document.getElementById('utility-value').innerHTML = '<span class="label">Utility</span><span class="value">' + d.utility.toFixed(4) + '</span>';
  document.getElementById('mi-value').innerHTML = '<span class="label">I(&mu;)</span><span class="value">' + d.mutual_info.toFixed(4) + ' nats</span>';
  if (d.usf_enabled) {
    document.getElementById('usf-enabled').innerHTML = '<span class="label">Enabled</span><span class="value">YES</span>';
    document.getElementById('usf-vfe').innerHTML = '<span class="label">Avg VFE</span><span class="value">' + (d.usf_avg_vfe || 0).toFixed(2) + '</span>';
    document.getElementById('usf-negentropy').innerHTML = '<span class="label">Negentropy</span><span class="value">' + (d.usf_avg_negentropy || 0).toFixed(4) + '</span>';
    document.getElementById('usf-steps').innerHTML = '<span class="label">Steps</span><span class="value">' + d.usf_steps + '</span>';
  } else {
    document.getElementById('usf-enabled').innerHTML = '<span class="label">Enabled</span><span class="value">NO</span>';
  }
};
let msgId = 0;
function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  const box = document.getElementById('chat-box');
  box.innerHTML += '<div class="msg-user"><b>You:</b> ' + escapeHtml(msg) + '</div>';
  fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:msg})})
    .then(r=>r.json()).then(d=>{
      box.innerHTML += '<div class="msg-dak"><b>DAK:</b> ' + escapeHtml(d.reply) + '</div>';
      box.scrollTop = box.scrollHeight;
    });
}
function escapeHtml(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
</script>
</body>
</html>
'''


def create_app(dak):
    chat = DAKChat()

    app = FastAPI(title='DAK API')

    @app.get('/')
    async def root():
        return HTMLResponse(HTML)

    @app.get('/state')
    async def get_state():
        d = dak.get_state_dict()
        return {
            'mu_norm': d['mu_norm'],
            'F': d['F'],
            'H_env': d['H_env'],
            'S_gen': d['S_gen'],
            'szilard_ratio': d['szilard_ratio'],
            'phase': d['phase'],
            'utility': dak.dqfr.utility,
            'delta': d['delta'],
            'mutual_info': d['mutual_info'],
            'tick_count': d['tick_count'],
            'usf_enabled': d.get('usf_enabled', False),
            'usf_avg_vfe': d.get('usf_avg_vfe', 0),
            'usf_avg_negentropy': d.get('usf_avg_negentropy', 0),
            'usf_steps': d.get('usf_steps', 0),
        }

    @app.post('/perturb')
    async def perturb(data: dict):
        sensor = data.get('sensor', '')
        value = data.get('value', 0.0)
        dak.perturbations.append({'sensor': sensor, 'value': value})
        return {'status': 'perturbed', 'sensor': sensor, 'value': value}

    @app.post('/chat')
    async def chat_endpoint(data: dict):
        message = data.get('message', '')
        if dak.usf_enabled and dak.usf_transformer is not None:
            reply = dak.usf_chat(message)
        else:
            mu = dak.state.read()
            state = {
                'mu_norm': float(sum(x * x for x in mu) ** 0.5),
                'F': dak.F, 'H_env': dak.H_env, 'S_gen': dak.S_gen,
                'szilard_ratio': dak.szilard_ratio,
                'phase': dak.dqfr.phase.value,
                'delta': dak.delta, 'mutual_info': dak.mutual_info,
                'tick_count': dak.tick_count,
            }
            reply = chat.send_message(message, state)
        return {'reply': reply}

    @app.get('/usf/state')
    async def usf_state():
        if not dak.usf_enabled:
            return {'enabled': False}
        base = {
            'enabled': True,
            'simplicial_dim': SIMPLICIAL_DIM,
            'n_layers': N_USF_LAYERS,
            'lee_wick_cutoff': LAMBDA_CUTOFF,
        }
        if dak.usf_optimizer is not None:
            s = dak.usf_optimizer.state_dict()
            base['avg_vfe'] = s['avg_vfe']
            base['avg_negentropy'] = s['avg_negentropy']
            base['steps'] = s['step_count']
        if dak.usf_transformer is not None:
            base['param_norm'] = dak.usf_transformer.get_param_norm()
        return base

    @app.post('/usf/toggle')
    async def usf_toggle():
        dak.usf_enabled = not dak.usf_enabled
        if dak.usf_enabled and dak.usf_transformer is None:
            dak._init_usf()
        return {'usf_enabled': dak.usf_enabled}

    @app.websocket('/ws')
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                state = await get_state()
                await websocket.send_json(state)
                await asyncio.sleep(0.5)
        except Exception:
            pass

    return app


def main():
    import asyncio

    print('Booting DAK kernel for Web API...')
    dak = DAK()
    t = dak.run_async()
    app = create_app(dak)
    print('DAK Web UI at http://localhost:8000')
    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
