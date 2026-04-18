const express = require('express');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
app.set('view engine', 'ejs');
app.use(express.json({ limit: '1mb' }));

const SIM_DIR = path.join(__dirname, 'simulators', 'color');
const PYTHON_BIN = path.join(SIM_DIR, 'venv', 'bin', 'python');
const COMPUTE_SCRIPT = path.join(SIM_DIR, 'compute.py');

app.get('/', (req, res) => res.render('index'));

app.post('/api/compute', (req, res) => {
  const py = spawn(PYTHON_BIN, [COMPUTE_SCRIPT], { cwd: SIM_DIR });

  let stdout = '';
  let stderr = '';
  py.stdout.on('data', (d) => (stdout += d));
  py.stderr.on('data', (d) => (stderr += d));

  py.stdin.write(JSON.stringify(req.body));
  py.stdin.end();

  py.on('close', (code) => {
    if (code !== 0) {
      console.error('[python]', stderr);
      return res.status(500).json({ error: stderr || 'python exited ' + code });
    }
    try {
      res.json(JSON.parse(stdout));
    } catch (e) {
      res.status(500).json({ error: 'parse error', stdout });
    }
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`http://localhost:${PORT}`));
