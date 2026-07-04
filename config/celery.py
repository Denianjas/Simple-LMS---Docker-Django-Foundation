import os
from celery import Celery

# Set default Django settings module untuk celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('simple_lms')

# Menggunakan konfigurasi dari settings.py dengan prefix CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Otomatis mencari file tasks.py di semua app terdaftar
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'cek-tiap-menit': {
        'task': 'lms_app.tasks.cleanup_old_progress',
        'schedule': 60.0,
    },
}
