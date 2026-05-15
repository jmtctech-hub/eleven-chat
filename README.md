# ELEVEN Chat

A beautiful Windows desktop chat interface for [Hermes Agent](https://github.com/NousResearch/hermes-agent), powered by DeepSeek.

![ELEVEN Chat](screenshot.png)

## What is this?

ELEVEN Chat replaces the terminal-based Hermes CLI with a modern web-based chat UI. It runs on WSL and opens in your Windows browser — giving you a clean, persistent chat experience with your AI agent.

## Features

- 🌙 Dark-themed modern chat interface
- 💬 Persistent conversation context (remembers across messages)
- 🔄 New Chat / Reconnect controls
- ⌨️ Enter to send, Shift+Enter for newline
- 🚀 Zero dependencies — pure Python stdlib + vanilla HTML/CSS/JS
- 🧠 Backed by Hermes Agent with full tool access

## Quick Start

### Requirements
- Windows 10/11 with WSL2
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed in WSL
- Python 3.10+ in WSL

### Launch

**Method 1: Double-click (Windows)**
```
Double-click start.bat in File Explorer
```

**Method 2: WSL Terminal**
```bash
cd "/mnt/d/hermes project/eleven-chat"
python3 server.py
```

Then open **http://localhost:8899** in your Windows browser.

## Project Structure

```
eleven-chat/
├── server.py      # Python backend — manages Hermes session via subprocess
├── index.html     # Chat UI — single-page app with vanilla JS
├── start.bat      # Windows launcher (double-click to run)
└── start.sh       # WSL launcher
```

## How It Works

```
┌──────────────┐     HTTP      ┌──────────────┐   subprocess   ┌──────────┐
│  Windows      │ ───────────→ │  server.py    │ ────────────→ │  Hermes   │
│  Browser      │ ←─────────── │  (WSL)        │ ←──────────── │  Agent    │
│  (localhost)  │    JSON      │  Port 8899    │   stdout      │  (WSL)    │
└──────────────┘               └──────────────┘               └──────────┘
```

- `server.py` starts a lightweight HTTP server and spawns a persistent Hermes session
- Each chat message is sent to Hermes via `hermes --resume <session> chat -q "message"`
- Responses are cleaned of ANSI codes and metadata, then returned as JSON
- The HTML frontend renders the conversation with typing indicators and smooth scrolling

## Configuration

The server connects to your existing Hermes configuration (`~/.hermes/config.yaml`). To change models:

```bash
hermes model   # Interactive model picker
```

Then restart the ELEVEN server.

## License

MIT
