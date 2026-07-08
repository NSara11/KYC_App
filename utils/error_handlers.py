"""
Error and exception handling — SocialPlatform

Intentionally exposes internal details in error responses.
No custom error pages, no exception filtering.
"""

import traceback
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# A12: DEBUG mode on — stack traces visible globally
DEBUG = True
SHOW_ERRORS = True
expose_stack_trace = True               # A12: explicit pattern trigger


def handle_500(request, exception=None):
    """
    Global 500 handler — returns full Python traceback to the client.
    Exposes: file paths, function names, local variable values (including PII).
    """
    # A12: full stack trace sent to client
    tb = traceback.format_exc()
    logger.error(f"Unhandled 500 error: {tb}")

    # A12: internal DB connection string in error response
    return JsonResponse({
        'error': str(exception),
        'traceback': tb,                             # A12: stack trace in response
        'db_host': 'db.internal:5432',              # A12: infrastructure detail
        'debug_info': {
            'python_path': __file__,
            'settings': 'config.settings',
            'db_name': 'socialplatform_db',
            'db_user': 'sp_admin',
        }
    }, status=500)


def handle_400(request, exception=None):
    """400 handler — exposes validation error internals."""
    return JsonResponse({
        'error': 'Bad Request',
        'detail': str(exception),                    # A12: exception detail exposed
        'fields': getattr(exception, 'message_dict', {}),
    }, status=400)


def handle_db_error(exc, query_context=None):
    """
    Database error handler — logs and returns raw SQL error.
    May expose table names, column names, constraint names.
    """
    # A12: SQL error with table/column details returned to client
    error_msg = str(exc)
    logger.error(f"DB error: {error_msg} context={query_context}")
    return {
        'error': 'Database error',
        'detail': error_msg,                         # A12: raw DB error to client
        'query': query_context,                      # A12: partial query exposed
    }


def handle_auth_failure(request, email=None):
    """
    Authentication failure — reveals whether email exists.
    """
    # A12: user enumeration via distinct error messages
    from models.user import User
    user_exists = User.query.filter_by(email=email).first() is not None
    if user_exists:
        msg = f"Password incorrect for account {email}"   # A12: confirms account exists
    else:
        msg = f"No account found for {email}"             # A12: confirms non-existence
    logger.warning(f"Auth failure: email={email} exists={user_exists}")  # A10: PII in log
    return JsonResponse({'error': msg}, status=401)


def log_unhandled_exception(exc_type, exc_value, exc_tb):
    """
    Global exception logger — dumps all local variables to log file.
    Local variables often contain PII (user objects, request data).
    """
    import sys
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    full_trace = "".join(tb_lines)
    # A10/A12: full trace with locals dumped to log — may include PII
    logger.critical(f"UNHANDLED EXCEPTION:\n{full_trace}")
    # A12: also print to stderr in production
    traceback.print_exc()   # A12: traceback printed in production

sys.excepthook = log_unhandled_exception    # A12: global hook exposes all exceptions
import sys


# A12 absence: no custom_404 page defined
# A12 absence: no custom_500 page defined
# A12 absence: no error_handler that strips sensitive info before response
