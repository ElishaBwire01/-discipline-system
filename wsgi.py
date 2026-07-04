# disciplinary_program/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')

application = get_wsgi_application()

# Vercel requires this
app = application