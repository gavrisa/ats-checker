#!/bin/bash

echo "🔧 Fixing Git Issues Step by Step..."

echo "1. Checking current status..."
git status

echo "2. Fetching latest changes from remote..."
git fetch origin

echo "3. Checking what changed on remote..."
git log --oneline HEAD..origin/main

echo "4. Stashing local changes..."
git stash

echo "5. Pulling latest changes..."
git pull origin main

echo "6. Applying stashed changes..."
git stash pop

echo "7. Checking for conflicts..."
git status

echo "8. Adding all changes..."
git add .

echo "9. Committing button fixes..."
git commit -m "🎯 Fix button issues: 'get my score' text and remove active stroke"

echo "10. Pushing to remote..."
git push origin main

echo "✅ Git issues should be resolved!"
echo "🚀 Vercel will now deploy your button fixes!"
