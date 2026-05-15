#!/usr/bin/env python3
"""
ELEVEN Chat Server - Bridges web UI to Hermes Agent
Uses hermes --continue -q for persistent conversation.
Run: python3 server.py
Open: http://localhost:8899 in Windows browser
"""

import http.server
import json
import os
import subprocess
import sys
import time
import re
import threading
from urllib.parse import urlparse

PORT = 8899
PROJECT_DIR = "/mnt/d/hermes project/eleven-chat"
SESSION_FILE = os.path.join(PROJECT_DIR, ".session_id")
ENV = {**os.environ, 'HOME': os.environ.get('HOME', '/home/lee')}

chat_lock = threading.Lock()
chat_session_id = None


def _extract_session_id(output: str):
    """Try to find Hermes session ID in output."""
    global chat_session_id
    for line in output.split('\n'):
        s = line.strip()
        if s.startswith('Session:') or s.startswith('session:'):
            sid = s.split(':', 1)[-1].strip().rstrip('.')
            if sid and len(sid) > 4:
                chat_session_id = sid
                with open(SESSION_FILE, 'w') as f:
                    f.write(sid)
                return


def _load_session_id():
    global chat_session_id
    try:
        with open(SESSION_FILE) as f:
            chat_session_id = f.read().strip()
    except:
        chat_session_id = None


def _clean_output(raw: str) -> str:
    """Remove ANSI codes and UI chrome from Hermes output."""
    ansi = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned = ansi.sub('', raw)
    
    skip_prefix = (
        'Model:', 'Provider:', 'Session:', 'Tokens:', 'Cost:',
        '╭', '╰', '│', '╔', '╚', '║', '═══', '───',
        '>>>', 'Type /help', 'Hermes v', 'Starting',
        'Query:', 'Initializing', '↻', 'Resume this session',
        'Duration:', 'Messages:', 'Chat mode:', 'hermes --resume',
    )
    
    lines = []
    for line in cleaned.split('\n'):
        s = line.strip()
        if not s:
            continue
        if any(s.startswith(p) for p in skip_prefix):
            continue
        if re.match(r'^\[.*\]$', s):
            continue
        lines.append(line)
    
    result = '\n'.join(lines).strip()
    return result if len(result) > 2 else "(Ready — ask me anything!)"


def send_message(message: str) -> str:
    """Send a message to Hermes and return the response."""
    global chat_session_id
    with chat_lock:
        cmd = ['hermes']
        if chat_session_id:
            cmd += ['--resume', chat_session_id]
        cmd += ['chat', '-q', message]
        
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=180,
                env=ENV, cwd=PROJECT_DIR,
            )
            output = result.stdout + result.stderr
            _extract_session_id(output)
            return _clean_output(output)
        except subprocess.TimeoutExpired:
            return "(Request timed out. Try a shorter message?)"
        except Exception as e:
            return f"(Error: {e})"


def restart_session():
    """Start a fresh session."""
    global chat_session_id
    chat_session_id = None
    try:
        os.remove(SESSION_FILE)
    except:
        pass
    
    try:
        result = subprocess.run(
            ['hermes', 'chat', '-q', 'Hello'],
            capture_output=True, text=True, timeout=30,
            env=ENV, cwd=PROJECT_DIR,
        )
        _extract_session_id(result.stdout + result.stderr)
    except:
        pass


class ChatHandler(http.server.SimpleHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_DIR, **kwargs)
    
    def do_GET(self):
        p = urlparse(self.path)
        
        if p.path == '/api/status':
            self._json({
                'status': 'ok',
                'session': (chat_session_id or '(none)')[:20]
            })
            return
        
        if p.path in ('/', ''):
            self.path = '/index.html'
        super().do_GET()
    
    def do_POST(self):
        p = urlparse(self.path)
        
        if p.path == '/api/chat':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            msg = data.get('message', '').strip()
            
            if not msg:
                self._json({'error': 'Empty message'}, 400)
                return
            
            print(f"[ELEVEN] > {msg[:100]}")
            resp = send_message(msg)
            print(f"[ELEVEN] < {resp[:100].replace(chr(10), ' ')}")
            self._json({'message': resp})
        
        elif p.path == '/api/restart':
            restart_session()
            print("[ELEVEN] Session restarted")
            self._json({'status': 'restarted'})
        
        else:
            self._json({'error': 'Not found'}, 404)
    
    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass


def main():
    print()
    print("=" * 55)
    print("    E L E V E N   C H A T   S E R V E R")
    print("=" * 55)
    print()
    print("  Initializing Hermes session...")
    sys.stdout.flush()
    
    restart_session()
    
    if chat_session_id:
        print(f"  ✓ Session: {chat_session_id[:24]}...")
    print(f"  ✓ Server: http://localhost:{PORT}")
    print()
    print("  Open this in your Windows browser:")
    print(f"  → http://localhost:{PORT}")
    print()
    print("  Press Ctrl+C to stop.")
    print("=" * 55)
    sys.stdout.flush()
    
    server = http.server.ThreadingHTTPServer(('0.0.0.0', PORT), ChatHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
