#!/bin/bash

echo "🏈 College Football Predictions - Easy Deploy"
echo "============================================="
echo ""

# Clean up any old deployment directories
rm -rf deploy_*

# Create fresh deployment directory
DEPLOY_DIR="college-football-app"
mkdir -p "$DEPLOY_DIR"

echo "📁 Creating fresh deployment files..."

# Copy the main files
cp index.html "$DEPLOY_DIR/"
cp app.js "$DEPLOY_DIR/"
cp README.md "$DEPLOY_DIR/"

echo "✅ Files ready in: $DEPLOY_DIR"
echo ""

echo "🚀 DEPLOYMENT STEPS:"
echo "==================="
echo ""
echo "1. Go to GitHub and create a new repository:"
echo "   https://github.com/new"
echo ""
echo "2. Repository settings:"
echo "   - Name: college-football-predictions (or your choice)"
echo "   - Make it PUBLIC"
echo "   - Don't initialize with README"
echo "   - Click 'Create repository'"
echo ""
echo "3. After creating the repository, GitHub will show you commands."
echo "   Run these commands in the terminal:"
echo ""
echo "   cd $DEPLOY_DIR"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo "   git branch -M main"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo "   git push -u origin main"
echo ""
echo "4. Enable GitHub Pages:"
echo "   - Go to your repository Settings"
echo "   - Scroll to 'Pages' section"
echo "   - Source: 'Deploy from a branch'"
echo "   - Branch: 'main', folder: '/'"
echo "   - Save"
echo ""
echo "5. Your app will be live in a few minutes at:"
echo "   https://YOUR_USERNAME.github.io/YOUR_REPO_NAME"
echo ""

echo "📂 Your files are ready in the '$DEPLOY_DIR' folder"
echo "Ready to proceed? The files are waiting for you!"
