@echo off
echo Starting ELEVEN Chat Server...
echo.
echo This will open your browser to the chat interface.
echo Keep this window open while chatting.
echo.

start "" "http://localhost:8899"

wsl -e bash -c "cd '/mnt/d/hermes project/eleven-chat' && python3 server.py"

pause
