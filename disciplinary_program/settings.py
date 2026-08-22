"""
Django settings for disciplinary_program project.
Production-ready with Vercel + Supabase support.
"""

import os
import sys
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

# Load environment variables from .env locally.
# In Vercel, environment variables are provided by Vercel itself.
load_dotenv()

# Build paths inside the project like this:
# BASE_DIR / "subdir"
BASE_DIR = Path(__file__).resolve().parent.parent

# Detect Vercel environment.
IS_VERCEL = bool(
    os.environ.get("VERCEL")
    or os.environ.get("VERCEL_ENV")
)

# Detect if running in development
IS_DEV = not IS_VERCEL

# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY and IS_VERCEL:
    raise ValueError(
        "SECRET_KEY environment variable is required in production!"
    )

if not SECRET_KEY:
    SECRET_KEY = "django-insecure-dev-key-change-in-production"
    print("WARNING: Using insecure development SECRET_KEY")

# Never enable DEBUG in production unless explicitly requested.
DEBUG = os.environ.get(
    "DEBUG",
    "False" if IS_VERCEL else "True"
).lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# ============================================================
# ALLOWED HOSTS
# ============================================================

if "test" in sys.argv:
    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        "testserver",
    ]

else:
    default_allowed_hosts = (
        "localhost,127.0.0.1,"
        ".trycloudflare.com,"
        ".vercel.app"
    )

    ALLOWED_HOSTS = [
        host.strip()
        for host in os.environ.get(
            "ALLOWED_HOSTS",
            default_allowed_hosts
        ).split(",")
        if host.strip()
    ]

# ============================================================
# CSRF TRUSTED ORIGINS
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        ""
    ).split(",")
    if origin.strip()
]

# Automatically trust Vercel deployments when running on Vercel.
if IS_VERCEL:
    vercel_url = os.environ.get("VERCEL_URL")
    if vercel_url:
        CSRF_TRUSTED_ORIGINS.append(f"https://{vercel_url}")
    CSRF_TRUSTED_ORIGINS.extend(
        [
            "https://*.vercel.app",
            "https://*.vercel-staging.com",
        ]
    )
else:
    # Allow local development with ngrok/cloudflare
    CSRF_TRUSTED_ORIGINS.extend(
        [
            "http://localhost:8000",
            "https://localhost:8000",
            "http://127.0.0.1:8000",
            "https://127.0.0.1:8000",
        ]
    )

# Remove duplicates while preserving order.
CSRF_TRUSTED_ORIGINS = list(
    dict.fromkeys(CSRF_TRUSTED_ORIGINS)
)

# ============================================================
# APPLICATION DEFINITION
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Your apps
    "core",
]

MIDDLEWARE = [
    # Security middleware first
    "django.middleware.security.SecurityMiddleware",
    
    # Session middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    
    # Common middleware
    "django.middleware.common.CommonMiddleware",
    
    # CSRF protection
    "django.middleware.csrf.CsrfViewMiddleware",
    
    # Authentication
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    
    # Messages
    "django.contrib.messages.middleware.MessageMiddleware",
    
    # Clickjacking protection
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    # Custom middleware (order matters - keep them last)
    "core.middleware.ErrorLoggingMiddleware",
    "core.middleware.OnlineStatusMiddleware",
    "core.middleware.RequestLoggingMiddleware",
]

ROOT_URLCONF = "disciplinary_program.urls"

# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                "core.context_processors.user_management_context",
            ],
        },
    },
]

WSGI_APPLICATION = "disciplinary_program.wsgi.application"

# ============================================================
# DATABASE - Supabase PostgreSQL
# ============================================================

# Get DATABASE_URL from environment
# For Supabase, it should be:
# postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL and IS_VERCEL:
    raise ValueError(
        "DATABASE_URL environment variable is required in production!"
    )

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///db.sqlite3"
    print("INFO: Using SQLite for local development")

# Configure database with production-ready settings
DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,  # Persistent connections
        conn_health_checks=True,  # Check connection health
        ssl_require=True if IS_VERCEL else False,  # Force SSL in production
    )
}

# Additional database settings for production
if IS_VERCEL:
    DATABASES["default"].update({
        "OPTIONS": {
            "sslmode": "require",  # Force SSL for Supabase
            "connect_timeout": 10,  # Timeout after 10 seconds
        }
    })

# IMPORTANT:
#
# SQLite is suitable for local development.
#
# On Vercel/serverless, SQLite files are NOT a reliable
# persistent production database.
#
# Therefore, DATABASE_URL should point to your persistent
# PostgreSQL/Supabase database in Vercel.

# ============================================================
# CACHE
# ============================================================

# Use local memory cache for development
# Consider Redis for production if needed
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "discipline-system-cache",
    }
}

# ============================================================
# EMAIL
# ============================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.environ.get(
    "EMAIL_HOST",
    "smtp.gmail.com"
)

EMAIL_PORT = int(
    os.environ.get(
        "EMAIL_PORT",
        "587"
    )
)

EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.environ.get(
    "EMAIL_HOST_USER",
    ""
)

EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD",
    ""
)

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "noreply@school.com"
)

# For production, consider using SendGrid, Mailgun, or AWS SES
if IS_VERCEL:
    # Vercel recommends using transactional email services
    # but we keep SMTP as fallback
    pass

# ============================================================
# LOGGING - VERCEL SAFE (Read-only filesystem fix)
# ============================================================

if IS_VERCEL:
    # Vercel filesystem is read-only except for /tmp
    LOGS_DIR = Path("/tmp/logs")
else:
    LOGS_DIR = BASE_DIR / "logs"

# Safely create the logging directory
try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    # If we can't create the directory (read-only filesystem), use memory-only
    LOGS_DIR = None

LOG_FILE = LOGS_DIR / "django.log" if LOGS_DIR else None

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "json": {
            "format": '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
            "style": "%",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },

    "handlers": {
        # Console logging is especially useful on Vercel
        # because Vercel captures stdout/stderr.
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json" if IS_VERCEL else "simple",
        },
    },

    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },

    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# File logging is optional - Vercel primarily uses console logging
# Only add file handler if we can write to the directory
if LOGS_DIR and LOG_FILE:
    try:
        LOGGING["handlers"]["file"] = {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": str(LOG_FILE),
            "formatter": "verbose",
        }
        LOGGING["root"]["handlers"].append("file")
        LOGGING["loggers"]["django"]["handlers"].append("file")
        LOGGING["loggers"]["core"]["handlers"].append("file")
    except (OSError, PermissionError):
        pass

# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

# IMPORTANT:
#
# Vercel's filesystem is not persistent.
#
# Uploaded files should eventually use persistent storage
# such as Supabase Storage or another object-storage service.
#
# Keeping MEDIA_ROOT here allows the project to continue
# working locally.

# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATICFILES_STORAGE = (
    "django.contrib.staticfiles.storage."
    "ManifestStaticFilesStorage"
)

# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    ""
)

SUPABASE_ANON_KEY = os.environ.get(
    "SUPABASE_ANON_KEY",
    ""
)

SUPABASE_SERVICE_ROLE_KEY = os.environ.get(
    "SUPABASE_SERVICE_ROLE_KEY",
    ""
)

SUPABASE_JWT_SECRET = os.environ.get(
    "SUPABASE_JWT_SECRET",
    ""
)

# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
        "OPTIONS": {
            "min_length": 8,
        },
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]

# ============================================================
# AUTHENTICATION
# ============================================================

# Custom user model (if you have one)
# AUTH_USER_MODEL = "core.User"

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True

USE_TZ = True

# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)

# ============================================================
# LOGIN / LOGOUT
# ============================================================

LOGIN_URL = "/login/"

LOGIN_REDIRECT_URL = "/dashboard/"

LOGOUT_REDIRECT_URL = "/login/"

# ============================================================
# SESSION
# ============================================================

SESSION_ENGINE = (
    "django.contrib.sessions.backends.db"
)

SESSION_COOKIE_AGE = 86400  # 24 hours in seconds

SESSION_SAVE_EVERY_REQUEST = True

# ============================================================
# PRODUCTION SECURITY (Vercel-specific)
# ============================================================

if IS_VERCEL:
    # SSL/HTTPS settings
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )
    
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookie security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    
    # Additional security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    
    # Referrer policy
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    
    # Secure cookies
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

# ============================================================
# CORS (if needed for API)
# ============================================================

# If you're building an API that other domains will access
# CORS_ALLOWED_ORIGINS = [
#     "https://your-frontend-domain.vercel.app",
# ]

# ============================================================
# MESSAGE TAGS
# ============================================================

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# ============================================================
# FILE UPLOAD
# ============================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5 MB
FILE_UPLOAD_PERMISSIONS = 0o644

# ============================================================
# GLOBAL CONSTANTS
# ============================================================

# You can add your own global constants here
APP_NAME = "Disciplinary Program"
APP_VERSION = "1.0.0"

# ============================================================
# DEBUG TOOLBAR (development only)
# ============================================================

if IS_DEV and DEBUG:
    try:
        INSTALLED_APPS += ["debug_toolbar"]
        MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
        INTERNAL_IPS = ["127.0.0.1"]
    except ImportError:
        pass

# ============================================================
# DJANGO EXTENSIONS (development only)
# ============================================================

if IS_DEV and DEBUG:
    try:
        INSTALLED_APPS += ["django_extensions"]
    except ImportError:
        pass

# ============================================================
# HEALTH CHECK (for Vercel)
# ============================================================

# Simple health check endpoint
# Add this to your urls.py:
# path("health/", lambda request: HttpResponse("OK"), name="health_check")