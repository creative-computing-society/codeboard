# python manage.py makemigrations
# python manage.py migrate
# python manage.py collectstatic --noinput
# service cron start
# touch /var/log/cron.log
# mv /workspace/conf/root /var/spool/cron/crontabs/root
# chmod +x /var/spool/cron/crontabs/root
# crontab /var/spool/cron/crontabs/root
# echo ">>> Done!"

# tail -f /var/log/cron.log
# gunicorn -b 0.0.0.0:8000 core.wsgi:application --timeout=300
gunicorn -b 0.0.0.0:8000 app.asgi:application -k uvicorn.workers.UvicornWorker -w 6 --timeout=300 # Since we are running ASGI, gunicorn needs uvicorn workers for async processing
