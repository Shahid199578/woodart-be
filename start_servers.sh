#!/bin/bash
echo "Starting A TO Z WoodArt Microservices..."

trap "kill 0" EXIT

source venv/bin/activate

# Unified Secret Key (from user_service .env)
# Unified Secret Key (from user_service .env)
export SECRET_KEY="django-insecure-test-key-123"

# Development Settings (Overrides Production Defaults)
export DEBUG="True"
export ALLOWED_HOSTS="*"
export CORS_ALLOW_ALL_ORIGINS="True"

python3 user_service/manage.py runserver 8001 &
PID1=$!
echo "User Service running on 8001 (PID $PID1)"

python3 product_service/manage.py runserver 8002 &
PID2=$!
echo "Product Service running on 8002 (PID $PID2)"

python3 order_service/manage.py runserver 8003 &
PID3=$!
echo "Order Service running on 8003 (PID $PID3)"

python3 ai_service/manage.py runserver 8004 &
PID4=$!
echo "AI Service running on 8004 (PID $PID4)"

python3 admin_service/manage.py runserver 8005 &
PID5=$!
echo "Admin Service running on 8005 (PID $PID5)"

python3 blog_service/manage.py runserver 8008 &
PID6=$!
echo "Blog Service running on 8008 (PID $PID6)"

python3 notification_service/manage.py runserver 8006 &
PID7=$!
echo "Notification Service running on 8006 (PID $PID7)"



python3 payment_service/manage.py runserver 8007 &
echo "Payment Service running on 8007 (PID $!)"

wait
