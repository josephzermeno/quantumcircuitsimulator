const express = require('express');
const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
app.set('view engine', 'ejs');
app.use(express.json({ limit: '1mb' }));

const SIM_DIR = path.join(__dirname, 'simulators', 'color');
const COMPUTE_SCRIPT = path.join(SIM_DIR, 'compute.py');

// Find a working Python binary — try venv first, then system python3
function findPython() {
  const candidates = [
    path.join(SIM_DIR, 'venv', 'bin', 'python'),
    path.join(SIM_DIR, 'venv', 'bin', 'python3'),
    '/usr/bin/python3',
    'python3',
    'python',
  ];
  for (const p of candidates) {
    try {
      if (p.startsWith('/') || p.startsWith('.')) {
        if (!fs.existsSync(p)) continue;
      }
      execSync(`${p} --version`, { stdio: 'pipe', timeout: 5000 });
      return p;
    } catch (_) {}
  }
  return null;
}

const PYTHON_BIN = findPython();
console.log('[startup] python:', PYTHON_BIN || 'NOT FOUND');

app.get('/', (req, res) => res.render('index'));

// Health check — shows python path and whether imports work
app.get('/api/health', (req, res) => {
  if (!PYTHON_BIN) return res.status(500).json({ error: 'no python found' });

  const py = spawn(PYTHON_BIN, ['-c', 'import sys; print(sys.executable); import qiskit; print("qiskit", qiskit.__version__)'], {
    cwd: SIM_DIR, timeout: 15000,
  });
  let out = '', err = '';
  py.stdout.on('data', (d) => (out += d));
  py.stderr.on('data', (d) => (err += d));
  py.on('close', (code) => {
    res.json({ python: PYTHON_BIN, code, stdout: out.trim(), stderr: err.trim() });
  });
});

app.post('/api/compute', (req, res) => {
  if (!PYTHON_BIN) return res.status(500).json({ error: 'no python binary found on server' });

  const py = spawn(PYTHON_BIN, [COMPUTE_SCRIPT], { cwd: SIM_DIR, timeout: 30000 });

  let stdout = '';
  let stderr = '';
  py.stdout.on('data', (d) => (stdout += d));
  py.stderr.on('data', (d) => (stderr += d));

  py.stdin.write(JSON.stringify(req.body));
  py.stdin.end();

  py.on('error', (err) => {
    console.error('[spawn error]', err.message);
    res.status(500).json({ error: 'spawn failed: ' + err.message });
  });

  py.on('close', (code) => {
    if (code !== 0) {
      console.error('[python exit', code, ']', stderr);
      return res.status(500).json({ error: stderr || 'python exited ' + code });
    }
    try {
      res.json(JSON.parse(stdout));
    } catch (e) {
      console.error('[parse error] stdout:', stdout.slice(0, 500));
      res.status(500).json({ error: 'parse error', stdout: stdout.slice(0, 500) });
    }
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`http://localhost:${PORT}`));
