# ============================================
# SUPABASE - ALL DATA STORAGE
# ============================================

import os
from pathlib import Path
import dj_database_url
from django.core.management.utils import get_random_secret_key

# ✅ FIX 1: Only load dotenv locally, not on Vercel
try:
    from dotenv import load_dotenv
    if not os.environ.get("VERCEL"):
        load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# VERCEL DETECTION
# ============================================

IS_VERCEL = os.environ.get('VERCEL', '0') == '1'
IS_PRODUCTION = os.environ.get('DJANGO_ENV') == 'production'

# ============================================
# DJANGO CORE SETTINGS
# ============================================

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_secret_key())
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ============================================
# URL & WSGI CONFIGURATION
# ============================================

ROOT_URLCONF = 'disciplinary_program.urls'
WSGI_APPLICATION = 'disciplinary_program.wsgi.application'

# ============================================
# ALLOWED HOSTS
# ============================================

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

# ============================================
# INSTALLED APPS
# ============================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
    'storages',  # For Supabase Storage
]

# ============================================
# MIDDLEWARE
# ============================================

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

# ============================================
# TEMPLATES
# ============================================

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

# ============================================
# SUPABASE POSTGRESQL DATABASE
# ============================================

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
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================================
# ✅ FIX 2 & 4: MODERN STORAGE CONFIGURATION
# ============================================

# ✅ Single source of truth - STORAGES only (Django 4.2+)
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ✅ FIX 7: Supabase S3 Credentials
AWS_ACCESS_KEY_ID = os.environ.get('SUPABASE_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('SUPABASE_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('SUPABASE_BUCKET', 'media')
AWS_S3_ENDPOINT_URL = os.environ.get('SUPABASE_S3_ENDPOINT')
AWS_S3_REGION_NAME = os.environ.get('SUPABASE_REGION', 'eu-north-1')

# ✅ FIX 3: Removed DEFAULT_FILE_STORAGE (using STORAGES instead)

# ✅ FIX 8: S3-compatible provider settings
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_S3_ADDRESSING_STYLE = "path"
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Public URL for images
AWS_S3_CUSTOM_DOMAIN = os.environ.get('SUPABASE_PUBLIC_URL')

# Media URL - points to Supabase Storage
if AWS_S3_ENDPOINT_URL and AWS_STORAGE_BUCKET_NAME:
    MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/public/{AWS_STORAGE_BUCKET_NAME}/"
else:
    MEDIA_URL = '/media/'

# ✅ FIX 5: Keep MEDIA_ROOT (some packages expect it)
MEDIA_ROOT = BASE_DIR / 'media'
# Create directory if it doesn't exist (local development only)
if not IS_VERCEL:
    os.makedirs(MEDIA_ROOT, exist_ok=True)

# ============================================
# STATIC FILES (Handled by WhiteNoise)
# ============================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ✅ FIX 4: Removed STATICFILES_STORAGE (using STORAGES instead)

# ============================================
# SESSION & CACHE (Use Database)
# ============================================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# ============================================
# AUTHENTICATION
# ============================================

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
# LOGIN URLs
# ============================================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# ============================================
# DEFAULT AUTO FIELD
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# SUPABASE CONFIGURATION (Additional)
# ============================================

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_PUBLISHABLE_KEY = os.environ.get('SUPABASE_PUBLISHABLE_KEY')
SUPABASE_SECRET_KEY = os.environ.get('SUPABASE_SECRET_KEY')
SUPABASE_PASSWORD = os.environ.get('SUPABASE_PASSWORD')