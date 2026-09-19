"""Run the real pack in an existing official BDS installation in /tmp.

Usage: python3 tools/engine_smoke.py /tmp/endless-waters-bds
The server installation is never redistributed. Each run uses a fresh world.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import signal

ROOT = Path(__file__).resolve().parents[1]
server = Path(sys.argv[1]).resolve()
if not str(server).startswith('/tmp/') or not (server / 'bedrock_server').is_file():
    raise SystemExit('Supply a disposable official Bedrock server installation in /tmp.')
if '--stop' in sys.argv:
    # Only stop the BDS process with this exact executable, used by this test.
    for process_dir in Path('/proc').iterdir():
        if not process_dir.name.isdigit(): continue
        try:
            if (process_dir / 'exe').resolve() == server / 'bedrock_server':
                os.kill(int(process_dir.name), signal.SIGTERM)
                print('Stopped temporary Bedrock test server', process_dir.name)
        except (OSError, PermissionError): pass
    raise SystemExit(0)
pack = server / 'behavior_packs/endless_waters'
shutil.copytree(ROOT / 'behavior_packs/endless_waters', pack, dirs_exist_ok=True)
shutil.copytree(ROOT / 'resource_packs/endless_waters', server / 'resource_packs/endless_waters', dirs_exist_ok=True)
shutil.copyfile(ROOT / 'tests/engine-smoke.js', pack / 'scripts/engine-smoke.js')
with (pack / 'scripts/main.js').open('a') as f: f.write("\nimport './engine-smoke.js';\n")
name = 'EndlessSmoke_' + str(int(time.time()))
world = server / 'worlds' / name
world.mkdir(parents=True)
(world / 'world_behavior_packs.json').write_text(json.dumps([
    {'pack_id': '2cb2fb59-9c6a-4961-bdde-86e73b165d9b', 'version': [0, 1, 0]}
]))
(world / 'world_resource_packs.json').write_text(json.dumps([
    {'pack_id': '61aebcce-03cc-41ed-87fd-40c2991fa93f', 'version': [0, 1, 0]}
]))
(server / 'server.properties').write_text('\n'.join([
    'server-name=Endless Waters local test', 'level-name=' + name, 'level-seed=731946',
    'gamemode=creative', 'difficulty=normal', 'allow-cheats=true', 'allow-list=true',
    'online-mode=true', 'server-port=19172', 'server-portv6=19173', 'server-ip=127.0.0.1',
    'transport=nethernet', 'enable-lan-visibility=false', 'view-distance=8',
    'tick-distance=4', 'max-players=1', 'content-log-file-enabled=true',
    'content-log-console-output-enabled=true', ''
]))
env = dict(os.environ, LD_LIBRARY_PATH=str(server))
process = subprocess.Popen([str(server / 'bedrock_server')], cwd=server, env=env,
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, bufsize=1)
lines = []
finished = threading.Event()
passed = False

def read():
    global passed
    for line in process.stdout:
        lines.append(line)
        if 'EW_' in line or '[Endless Waters]' in line or 'ERROR' in line:
            print(line.rstrip(), flush=True)
        if 'EW_SMOKE_PASS' in line:
            passed = True; finished.set()
        if 'EW_SMOKE_FAIL' in line or 'Paused endless:' in line or 'Could not prepare endless:' in line:
            finished.set()
    finished.set()

thread = threading.Thread(target=read, daemon=True)
thread.start()
try:
    finished.wait(720)
finally:
    try:
        process.stdin.write('stop\n'); process.stdin.flush()
        process.wait(timeout=30)
    except (BrokenPipeError, subprocess.TimeoutExpired):
        process.terminate()
        process.wait(timeout=10)
    thread.join(timeout=5)
    results = ROOT / 'test-results'
    results.mkdir(exist_ok=True)
    (results / 'engine-smoke.log').write_text(''.join(lines))
    print('Engine result:', 'PASS' if passed else 'FAIL', '| world:', name, flush=True)
sys.exit(0 if passed else 1)
