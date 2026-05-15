#!/bin/bash
# ELEVEN Chat - Push to GitHub
# Run this in WSL terminal

cd "/mnt/d/hermes project/eleven-chat"

echo "============================================"
echo "  Push ELEVEN Chat to GitHub"
echo "============================================"
echo ""
echo "  Repository: github.com/jmtctech-hub/eleven-chat"
echo ""

# Step 1: Create the repo on GitHub via API
echo "Step 1: Create repository on GitHub..."
echo ""
echo "  Open this URL in your browser to create the repo:"
echo "  https://github.com/new?name=eleven-chat&description=ELEVEN+Chat+-+Windows+GUI+for+Hermes+Agent&visibility=public"
echo ""
read -p "  Press Enter after creating the repo..." 

# Step 2: Get token
echo ""
echo "Step 2: Generate a Personal Access Token..."
echo ""
echo "  Open: https://github.com/settings/tokens/new?description=eleven-chat&scopes=repo"
echo "  Set expiration to 90 days, click Generate."
echo ""
read -sp "  Paste your token: " TOKEN
echo ""

# Step 3: Push
echo ""
echo "Step 3: Pushing to GitHub..."
git push https://jmtctech-hub:${TOKEN}@github.com/jmtctech-hub/eleven-chat.git master

# Step 4: Save credentials
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Success! Repository is live at:"
    echo "  https://github.com/jmtctech-hub/eleven-chat"
    
    # Save credential for future pushes
    git config credential.helper store
    echo "https://jmtctech-hub:${TOKEN}@github.com" > ~/.git-credentials
    
    # Switch remote to use stored credentials
    git remote set-url origin https://github.com/jmtctech-hub/eleven-chat.git
    
    echo ""
    echo "  Credentials saved. Future pushes won't require a token."
else
    echo ""
    echo "✗ Push failed. Check your token and try again."
    echo "  Run: git push"
fi
