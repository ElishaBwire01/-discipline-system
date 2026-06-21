import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disciplinary_program.settings')

# Vercel compatible
application = get_wsgi_application()
app = application
