#!/bin/bash

cd ./api
pip install --upgrade pip
pip install -r requirements.txt
cd ./src
echo "Installing database..."
python -u init_db.py
echo "Running app.py..."
python -u app.py

# Install Node.js environment
echo "Installing Node.js..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc

nvm install node
node --version
npm --version

cd ../../web
npm install
echo "Running vue.js..."
npm run dev