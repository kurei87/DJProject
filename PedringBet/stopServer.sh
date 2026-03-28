pkill -f "celery -A support worker"
pkill -f "celery -A support beat"
pkill -f "gunicorn --workers 4 --bind 0.0.0.0:8000 support.wsgi:application"
pkill -f "manage.py runserver"