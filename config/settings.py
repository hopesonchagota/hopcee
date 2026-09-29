"""
Django settings for the Hopcee Ordering Services project.

Hopcee helps LUANAR Bunda Campus students buy goods (Irish Potato,
Electrical Equipment, Soya Pieces/Thumba, Mafuta, Bonya small fish,
and more) at ordering price from Mitundu Market and Town, splitting
only the transport cost half-and-half with the student.
"""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# --- Core ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-secret-key-change-me")
DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if h.strip()
]

# Vercel deployment hostnames (production domain + per-deployment URLs)
ALLOWED_HOSTS.append(".vercel.app")
VERCEL_URL = os.getenv("VERCEL_URL")
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)

# Render/Railway/Heroku-style platform hostname
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = []
for _h in ALLOWED_HOSTS:
    if _h in ("127.0.0.1", "localhost"):
        continue
    CSRF_TRUSTED_ORIGINS.append(
        f"https://*{_h}" if _h.startswith(".") else f"https://{_h}"
    )

# --- Applications ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "widget_tweaks",
    "accounts",
    "catalog",
    "orders",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "orders.middleware.CartCountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Database ---
# Defaults to SQLite for local dev. Set DATABASE_URL in .env to switch to
# PostgreSQL in production (e.g. on Render/Railway/Heroku) with zero code
# changes.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Auth ---
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 6}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Blantyre"
USE_I18N = True
USE_TZ = True

# --- Static & media ---
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# Vercel has no build step for collectstatic, so WhiteNoise serves files
# straight from the static finders and we avoid the manifest storage.
WHITENOISE_USE_FINDERS = True
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Messages (map Django's default "error" tag to Tailwind-friendly "danger") ---
from django.contrib.messages import constants as messages_constants  # noqa: E402

MESSAGE_TAGS = {
    messages_constants.ERROR: "danger",
}

# --- Hopcee business config (also exposed to every template) ---
HOPCEE = {
    "NAME": "Hopcee Ordering Services",
    "SLOGAN": "Buy at Ordering Price with Just Half Way Transport",
    "LOCATION": "LUANAR Bunda Campus",
    "WHATSAPP_NUMBER": os.getenv("HOPCEE_WHATSAPP_NUMBER", "+265988609202"),
    "CALL_NUMBER": os.getenv("HOPCEE_CALL_NUMBER", "+265897470024"),
    "REG_NUMBER": os.getenv("HOPCEE_REG_NUMBER", "Available on Request"),
}

# --- Search engines ---
# Paste the token from Google Search Console (HTML tag method) into this
# environment variable. Leave empty until you have it.
GOOGLE_SITE_VERIFICATION = os.getenv("GOOGLE_SITE_VERIFICATION", "").strip()

# --- WhatsApp Cloud API ---
WHATSAPP_CLOUD_API_TOKEN = os.getenv("WHATSAPP_CLOUD_API_TOKEN", "")
WHATSAPP_CLOUD_API_PHONE_ID = os.getenv("WHATSAPP_CLOUD_API_PHONE_ID", "")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v20.0")

# --- Order pricing ---
# Half of the transport fee is charged to the student; Hopcee absorbs the
# other half by making the trip for many students' orders at once.
TRANSPORT_FEE_SHARE = 0.5

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
