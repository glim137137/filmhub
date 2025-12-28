#!/bin/bash

echo "Install python 3.12..."

pip install --upgrade pip
pip install -r requirements.txt

cd ./api/src
echo "Installing database..."
python -u init_db.py
echo "Running app.py..."
gunicorn -w 4 -k gevent -b 0.0.0.0:5000 --access-logfile ./data/logs/access.log --error-logfile data/logs/error.log app:app

# Install Node.js environment
echo "Installing Node.js..."

cd ../../web
npm install
echo "Running vue.js..."
npm run build