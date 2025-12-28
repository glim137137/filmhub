#!/bin/bash

cd ./api/src
echo "Installing database..."
python -u init_db.py
echo "Running app.py..."
gunicorn -w 4 -k gevent -b 0.0.0.0:5000 --access-logfile data/logs/access.log --error-logfile data/logs/error.log app:app

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