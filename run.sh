python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
# python manage.py collectstatic --noinput
# service cron start
# touch /var/log/cron.log
# mv /workspace/conf/root /var/spool/cron/crontabs/root
# chmod +x /var/spool/cron/crontabs/root
# crontab /var/spool/cron/crontabs/root
# echo ">>> Done!"

# tail -f /var/log/cron.log
# gunicorn -b 0.0.0.0:8000 core.wsgi:application
python manage.py runserver 0.0.0.0:8000