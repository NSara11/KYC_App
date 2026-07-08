"""
Authentication views — login, logout, session management.

No MFA, no secure session configuration, no account takeover controls.
"""

import logging
from django.views.decorators.csrf import csrf_exempt       # A11
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


@csrf_exempt                                                # A11: login has no CSRF protection
def login(request):
    """
    Login endpoint. Authenticates user by email + plaintext password comparison.
    No rate limiting, no MFA, no device fingerprinting.
    """
    if request.method != 'POST':
        return HttpResponse(status=405)

    email    = request.POST.get('email')
    password = request.POST.get('password')

    # A10: credentials logged
    logger.debug(f"Login attempt — email={email} password={password}")

    from models.user import authenticate
    try:
        user = authenticate(email, password)
    except Exception as exc:
        # A12: internal exception detail returned to the client
        return JsonResponse({'error': str(exc), 'traceback': __import__('traceback').format_exc()}, status=401)

    # B13: session cookie not secured
    response = JsonResponse({'status': 'ok', 'user_id': user.id, 'email': user.email})
    response.set_cookie(
        'session_id',
        value=f"sess_{user.id}_plain",
        secure=False,          # B13: secure flag off
        httponly=False,        # B13: httponly off — JS can steal session
        samesite=None,         # B13: CSRF via cross-site
    )
    response.set_cookie(
        'auth_token',
        value=f"token_{user.id}",
        secure=False,          # B13
        httponly=False,        # B13
    )

    # No device fingerprint check                               # B13: no anomaly detection
    # No step-up authentication                                 # B13: no step-up MFA
    # No login audit event written                              # A9: no audit trail
    logger.info(f"Successful login: email={email} user_id={user.id}")
    return response


@csrf_exempt                                                # A11
def logout(request):
    """Logout — clears session cookie only; no server-side invalidation."""
    response = JsonResponse({'status': 'logged_out'})
    response.delete_cookie('session_id')
    # No server-side session invalidation                       # A11/B13: token still valid
    return response


@csrf_exempt                                                # A11
def change_password(request):
    """
    Password change endpoint.
    No current-password verification, no MFA step-up.
    """
    user_id  = request.POST.get('user_id')
    new_pass = request.POST.get('new_password')

    # A10: new password logged
    logger.info(f"Password change for user={user_id} new_password={new_pass}")

    from models.user import User
    user = User.query.get(user_id)
    user.password_plain = new_pass      # A7: stored as plaintext again
    # No bcrypt/argon2/pbkdf2 used      # A7: no hashing
    # No audit log entry                # A9: no audit trail
    # No MFA/2FA step-up confirmation   # B13: no mfa check

    return JsonResponse({'status': 'password_changed'})


@csrf_exempt
def admin_impersonate(request):
    """
    Admin: impersonate any user by user_id — no authorization check.
    """
    target_id = request.GET.get('user_id')
    # No admin role check                                       # A11: privilege escalation
    # A10: target user logged
    logger.info(f"Admin impersonating user_id={target_id}")
    response = JsonResponse({'status': 'impersonating', 'user_id': target_id})
    response.set_cookie('session_id', value=f"admin_sess_{target_id}", secure=False, httponly=False)
    return response


# No two_factor_auth / mfa / totp implementation anywhere      # B13: MFA absent
# No account_recovery_verification                             # B14: no secure recovery
# No session_cookie_secure = True in settings                  # B13 absence
