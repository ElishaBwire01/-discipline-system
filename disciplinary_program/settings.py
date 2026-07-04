"""
Django settings for disciplinary_program project.
"""

import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key
import dotenv

dotenv.load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_secret_key())
DEBUG = True
ALLOWED_HOSTS = [
    '.vercel.app',
    '.trycloudflare.com',
    'localhost',
    '127.0.0.1',
    'murnebrvgejmxdxzxtfe.supabase.co',
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.trycloudflare.com',
    'https://*.supabase.co',
    'http://localhost:8000',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'disciplinary_program.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.user_management_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'disciplinary_program.wsgi.application'

# ============================================
# DATABASE CONFIGURATION
# ============================================
import dj_database_url

# Use PostgreSQL on Vercel, SQLite locally
if os.environ.get('VERCEL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=False
        )
    }
else:
    # Local development - use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# ============================================
# STATIC & MEDIA FILES
# ============================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ? MEDIA FILES CONFIGURATION - CRITICAL FOR PROFILE PICTURES
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================
# LOGIN URLS
# ============================================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# SUPABASE CONFIGURATION
# ============================================
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_PUBLISHABLE_KEY = os.environ.get('SUPABASE_PUBLISHABLE_KEY')
SUPABASE_SECRET_KEY = os.environ.get('SUPABASE_SECRET_KEY')

# ============================================
# DATABASE CONFIGURATION - Supabase PostgreSQL
# ============================================

# Supabase PostgreSQL Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': os.environ.get('SUPABASE_PASSWORD', ''),
        'HOST': 'murnebrvgejmxdxzxtfe.supabase.co',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Use DATABASE_URL if provided
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=True
    )
# ============================================
# SUPABASE CONFIGURATION
# ============================================
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://murnebrvgejmxdxzxtfe.supabase.co')
SUPABASE_PUBLISHABLE_KEY = os.environ.get('SUPABASE_PUBLISHABLE_KEY')
SUPABASE_SECRET_KEY = os.environ.get('SUPABASE_SECRET_KEY')