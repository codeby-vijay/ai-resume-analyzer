#!/usr/bin/env bash
# One-shot local dev setup (no Docker): backend venv + frontend deps
set -e

echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm || true
cp -n .env.example .env || true
deactivate
cd ..

echo "Setting up frontend..."
cd frontend
npm install
cp -n .env.example .env || true
cd ..

echo "Setup complete. See README.md for how to run the app."
