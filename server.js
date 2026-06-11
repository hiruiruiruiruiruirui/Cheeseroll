#!/usr/bin/env node
// Simple static file server for the web frontend
// Usage: node server.js
// Serves the web/src directory with SPA fallback to index.html

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 5173;
const ROOT = path.join(__dirname, 'web', 'src');
const INDEX = path.join(__dirname, 'web', 'index.html');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.vue': 'text/plain; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
};

http.createServer((req, res) => {
  let url = req.url.split('?')[0];
  let filePath = path.join(ROOT, url);

  // SPA fallback: if file doesn't exist, serve index.html
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    filePath = INDEX;
  }

  const ext = path.extname(filePath);
  const mime = MIME[ext] || 'application/octet-stream';

  try {
    const content = fs.readFileSync(filePath);
    res.writeHead(200, { 'Content-Type': mime, 'Access-Control-Allow-Origin': '*' });
    res.end(content);
  } catch (e) {
    res.writeHead(404);
    res.end('Not Found');
  }
}).listen(PORT, () => {
  console.log(`Frontend running at http://localhost:${PORT}`);
  console.log(`Serving from: ${ROOT}`);
});
