#!/bin/bash
cd /root/filmhub/api/src
echo "Starting wsgi..."
exec gunicorn -w 4 -k gevent -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app
echo "Starting nginx..."
systemctl start nginx