import json, os, signal, subprocess, sys, time, threading, urllib.request
PY = '/Users/buidinhtri/Desktop/tuvibattu/.venv/bin/python'
S = '/private/tmp/claude-501/-Users-buidinhtri-Desktop-tuvibattu/3dd1d7ba-3c4d-4371-8767-9e5f3966f935/scratchpad'
TREES = {'base': S + '/capwt/engine', 'baseA': S + '/capwt/engine', 'opt': S + '/optwt/engine', 'optB': S + '/optwt/engine'}
PORT = 8900
def ps(pid):
    o = subprocess.run(['ps', '-o', 'rss=,cputime=', '-p', str(pid)], capture_output=True, text=True).stdout.split()
    if len(o) < 2: return None
    t = o[1].split(':'); secs = float(t[-1]) + 60 * int(t[-2]) + (3600 * int(t[-3]) if len(t) > 2 else 0)
    return int(o[0]) / 1024, secs
def run(variant, frac, N, seed=5):
    srv = subprocess.Popen([PY, '-m', 'uvicorn', 'tvbt.api:app', '--host', '127.0.0.1', '--port', str(PORT), '--log-level', 'warning'] + os.environ.get('UVI_ARGS', '').split(), cwd=TREES[variant], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while True:
        try: urllib.request.urlopen(f'http://127.0.0.1:{PORT}/', timeout=1); break
        except Exception: time.sleep(0.05)
    cold_start = time.time() - t0
    # warm the process (imports, rule packs) before measuring; a live container is normally warm
    body = json.dumps({'year': 1990, 'month': 5, 'day': 17, 'hour': 10, 'minute': 30, 'gender': 'male'}).encode()
    for ep in ('chart', 'reasoning', 'analysis'):
        urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{PORT}/api/{ep}', body, {'content-type': 'application/json'}), timeout=60).read()
    base_rss, cpu0 = ps(srv.pid)
    th = subprocess.Popen([PY, 'throttle.py', str(srv.pid), str(frac)]) if frac < 1 else None
    peak = [base_rss]; stop = threading.Event()
    def sample():
        while not stop.is_set():
            r = ps(srv.pid)
            if r: peak[0] = max(peak[0], r[0])
            time.sleep(0.1)
    ts = threading.Thread(target=sample); ts.start()
    res = subprocess.run(['node', 'load.mjs', f'http://127.0.0.1:{PORT}', str(N), variant, str(seed)], capture_output=True, text=True, timeout=900)
    stop.set(); ts.join()
    if th: th.terminate(); th.wait()
    os.kill(srv.pid, signal.SIGCONT); r = ps(srv.pid); cpu1 = r[1] if r else cpu0
    srv.terminate(); srv.wait()
    out = json.loads(res.stdout.strip().splitlines()[-1]); out.update(frac=frac, cold_start_s=round(cold_start, 2), rss_idle_mb=round(base_rss), rss_peak_mb=round(peak[0]), cpu_s=round(cpu1 - cpu0, 2))
    return out
if __name__ == '__main__':
    variants = sys.argv[1].split(','); fracs = [float(x) for x in sys.argv[2].split(',')]; Ns = [int(x) for x in sys.argv[3].split(',')]
    for f in fracs:
        for v in variants:
            for n in Ns:
                print(json.dumps(run(v, f, n)), flush=True)
