"""
Application settings — SocialPlatform v2.1
"""

# ── Core ──────────────────────────────────────────────────────────────────────
DEBUG = True                                   # A12: debug mode exposes stack traces
SECRET_KEY = 'django-insecure-8x!k2#pqr9v@mwz'  # A11: hardcoded secret
ALLOWED_HOSTS = ['*']

# ── Database ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'socialplatform_db',
        'USER': 'sp_admin',
        'PASSWORD': 'Sp@Admin2024!',           # A11: hardcoded DB credential
        'HOST': 'db.internal',
        'PORT': '5432',
    }
}

# ── Third-party API keys ──────────────────────────────────────────────────────
API_KEY = 'sk-live-a8f3c2d1e9b74f56a012cd34ef567890'    # A11: hardcoded API key
STRIPE_SECRET_KEY = 'sk_live_51HqXtKJx9'               # A11 / B26: payment key exposed
SENDGRID_API_KEY = 'SG.abc123XYZdefGHI'
GOOGLE_ANALYTICS_ID = 'G-X7K2M9P3Q1'                   # A13: third-party analytics
FACEBOOK_PIXEL_ID = '987654321012345'                   # A13: Facebook pixel
MIXPANEL_TOKEN = 'f3a8c12d9e4b2a7f'                     # A13: Mixpanel

# ── Session / Cookies ─────────────────────────────────────────────────────────
SESSION_COOKIE_SECURE = False           # B13: cookies not forced to HTTPS
SESSION_COOKIE_HTTPONLY = False         # B13: JS can access session cookie
SESSION_COOKIE_SAMESITE = None          # B13: CSRF exposure via cross-site
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ['*']

# ── Security headers (all disabled) ──────────────────────────────────────────
SECURE_SSL_REDIRECT = False             # A6: no HTTPS enforcement
SECURE_HSTS_SECONDS = 0                 # A6: HSTS disabled
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
# No Content-Security-Policy configured  # A11: missing CSP header

# ── Rate limiting ─────────────────────────────────────────────────────────────
rate_limit = False                      # B8: rate limiting disabled globally
RATELIMIT_ENABLE = False

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@socialplatform.io'
EMAIL_HOST_PASSWORD = 'SendGrid@2024'   # A11: hardcoded SMTP password
EMAIL_USE_TLS = True

# ── Logging — PII unmasked ────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/socialplatform/app.log',  # includes PII — A10
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',                               # A12: DEBUG logging in prod
            'propagate': True,
        },
    },
}

# ── Data retention — not defined ─────────────────────────────────────────────
# No DATA_RETENTION_DAYS defined                           # A14: no retention policy
# No PURPOSE_OF_COLLECTION defined                         # A14: no purpose mapping
# No ROPA metadata                                         # A14: no records of processing
