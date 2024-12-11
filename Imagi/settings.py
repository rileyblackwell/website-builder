"""
Django settings for Imagi project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

load_dotenv()  # loads environment variables from .env

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.Builder',
    'apps.Auth.apps.AuthConfig',
    'apps.Home',
    'apps.Payments',
    'apps.ProjectManager.apps.ProjectManagerConfig',
    'rest_framework',
    'apps.Agents',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Imagi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),  # Make sure this is first
            os.path.join(BASE_DIR, 'templates', 'admin'),  # Add this line
            os.path.join(BASE_DIR, 'apps', 'Builder', 'templates'),
            os.path.join(BASE_DIR, 'apps', 'Home', 'templates'),
            os.path.join(BASE_DIR, 'apps', 'Auth', 'templates'),
            os.path.join(BASE_DIR, 'apps', 'Payments', 'templates'),
            os.path.join(BASE_DIR, 'apps', 'ProjectManager', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Imagi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Global static files first
    os.path.join(BASE_DIR, 'apps', 'Builder', 'static'),
    os.path.join(BASE_DIR, 'apps', 'Home', 'static'),
    os.path.join(BASE_DIR, 'apps', 'Auth', 'static'),
    os.path.join(BASE_DIR, 'apps', 'Payments', 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Change these lines at the end of the file
LOGIN_REDIRECT_URL = 'builder:landing_page'  # Redirect to builder landing page after login
LOGOUT_REDIRECT_URL = 'landing_page'  # Redirect to landing page after logout
LOGIN_URL = 'login'  # URL name for the login page

# Load environment variables
load_dotenv()

# Stripe API keys
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLIC_KEY')

# Ensure these keys are not None
if not STRIPE_SECRET_KEY:
    raise ValueError("STRIPE_SECRET_KEY is not set in the environment variables.")
if not STRIPE_PUBLISHABLE_KEY:
    raise ValueError("STRIPE_PUBLIC_KEY is not set in the environment variables.")

# Validate Stripe key formats
if not STRIPE_SECRET_KEY.startswith(('sk_test_', 'sk_live_')):
    raise ValueError("STRIPE_SECRET_KEY appears to be in an invalid format")
if not STRIPE_PUBLISHABLE_KEY.startswith(('pk_test_', 'pk_live_')):
    raise ValueError("STRIPE_PUBLIC_KEY appears to be in an invalid format")

# Add these settings near the other security settings
SECURE_SSL_REDIRECT = not DEBUG  # Redirects all non-HTTPS requests to HTTPS
SESSION_COOKIE_SECURE = not DEBUG  # Ensures cookies are only sent over HTTPS
CSRF_COOKIE_SECURE = not DEBUG  # Ensures CSRF cookies are only sent over HTTPS

# For development, you might want to add localhost to ALLOWED_HOSTS
ALLOWED_HOSTS = ['localhost', '127.0.0.1'] if DEBUG else ['your-production-domain.com']

# Add these CSRF-related settings
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# If you're using HTTPS in development, add these as well:
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend(['https://localhost:8000', 'https://127.0.0.1:8000'])

# Ensure CSRF middleware is properly ordered
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Make sure this is present and in this order
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Add custom CSRF failure view
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Or your email provider's SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # Your email address
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Your email app password
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Password Reset Settings
PASSWORD_RESET_TIMEOUT = 259200  # 3 days in seconds

# Authentication Settings
# ...existing auth settings...

# Add this near other path-related settings
PROJECTS_ROOT = os.path.join(BASE_DIR.parent, 'oasis_projects')

# Make sure the directory exists
os.makedirs(PROJECTS_ROOT, exist_ok=True)
