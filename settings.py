import os
import sys
from pathlib import Path
from django.core.management.utils import get_random_secret_key
import dj_database_url
import dotenv

# Load environment variables
dotenv.load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Vercel detection
IS_VERCEL = os.environ.get('VERCEL', False)
IS_PRODUCTION = os.environ.get('DJANGO_ENV') == 'production'

# Security settings for Vercel
if IS_VERCEL or IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Update ALLOWED_HOSTS for Vercel
ALLOWED_HOSTS = [
    '.vercel.app',
    '.trycloudflare.com',
    'localhost',
    '127.0.0.1',
    'murnebrvgejmxdxzxtfe.supabase.co',
    # Add your custom domain if any
    # 'your-domain.com',
]

# Update CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.trycloudflare.com',
    'https://*.supabase.co',
    'http://localhost:8000',
]

# Database - use Supabase on Vercel
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Fallback for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files for Vercel
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files - use external storage for Vercel
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise for static files
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Static file storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# DEBUG - set from environment
DEBUG = os.environ.get('DEBUG', 'False') == 'True'