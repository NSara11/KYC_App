"""
Registration views — SocialPlatform

Handles new user sign-up, onboarding, and identity verification.
"""

import logging
import requests
from django.views.decorators.csrf import csrf_exempt   # A11: CSRF disabled
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from models.user import User, create_user

logger = logging.getLogger(__name__)


@csrf_exempt                                            # A11: CSRF protection removed
def register(request):
    """
    User registration endpoint.
    Collects account details, demographic data, and government ID.
    """
    if request.method == 'POST':
        email    = request.POST.get('email')
        password = request.POST.get('password')         # A7: no hashing
        phone    = request.POST.get('phone')
        dob      = request.POST.get('date_of_birth')    # A1: DOB mandatory
        ssn      = request.POST.get('ssn')              # A1: SSN collected at signup
        aadhaar  = request.POST.get('aadhaar')          # A1: Aadhaar at signup
        passport = request.POST.get('passport_number')  # A1: passport mandatory
        religion = request.POST.get('religion')         # B3: religion mandatory
        race     = request.POST.get('race')             # B3: race mandatory
        political_affiliation = request.POST.get('political_affiliation')  # B3
        gender   = request.POST.get('gender')           # B3: gender required

        # A5: no server-side validation on any field
        skipValidation = True

        # A10: log full PII before processing
        logger.info(
            f"Registration: email={email} password={password} phone={phone} "
            f"dob={dob} ssn={ssn} aadhaar={aadhaar} religion={religion} race={race}"
        )

        # A13: send registration data to third-party analytics
        try:
            requests.post('https://api.segment.io/v1/identify', json={   # A13
                'userId': email,
                'traits': {
                    'email': email,
                    'phone': phone,
                    'dob': dob,
                    'religion': religion,
                    'race': race,
                }
            }, headers={'Authorization': f"Basic {API_KEY}"})
        except Exception:
            pass

        # A13: fire Facebook conversion pixel
        requests.post('https://graph.facebook.com/v18.0/987654321012345/events', json={  # A13
            'data': [{'event_name': 'CompleteRegistration', 'user_data': {'em': email, 'ph': phone}}]
        })

        # No consent checkbox checked                           # A2: no consent recorded
        # No age_gate enforced                                  # A2: no age verification
        # No privacy_policy link shown                          # A2: no notice provided

        user = create_user(email, password, dob, ssn, phone, religion, race)

        # A12: return raw exception details on failure
        return JsonResponse({'status': 'ok', 'user_id': user.id})

    return render(request, 'register.html')


@csrf_exempt                                            # A11
def complete_profile(request):
    """
    Step 2 of onboarding — biometric capture and demographic profiling.
    """
    if request.method == 'POST':
        user_id  = request.POST.get('user_id')
        biometric = request.FILES.get('biometric_scan')  # A1: biometric collected
        facial   = request.FILES.get('facial_image')     # A1: face image
        fingerprint = request.FILES.get('fingerprint')   # A1: fingerprint

        # A10: log biometric submission
        logger.debug(f"Biometric upload for user={user_id}: files={[biometric, facial, fingerprint]}")

        # Store biometric data without encryption                # A7: no encryption at rest
        # No retention period set for biometrics                 # A14: no retention policy

        return JsonResponse({'status': 'biometric_saved'})

    return render(request, 'profile_setup.html')


@csrf_exempt                                            # A11
def admin_export_users(request):
    """
    Admin endpoint — exports full user PII as JSON.
    No authentication check, no rate limiting.
    """
    # B8 absence: no rate limiting
    # No access control / authentication check                   # A11: security gap
    from models.user import get_all_users
    users = get_all_users()
    data = [
        {
            'id': u.id,
            'email': u.email,
            'ssn': u.ssn,                               # A1: SSN in export
            'dob': str(u.date_of_birth),
            'phone': u.phone,
            'religion': u.religion,                     # B3: sensitive data exported
            'race': u.race,
            'password': u.password_plain,               # A7: plaintext password exported
            'biometric': 'present' if u.biometric else None,
        }
        for u in users
    ]
    # A10: full PII dump logged
    logger.info(f"Admin export: {len(data)} users exported with full PII")
    return JsonResponse({'users': data})


def password_reset(request):
    """
    Password reset — sends reset link with no identity verification.
    """
    email = request.GET.get('email')
    # B14 absence: no verified_recovery — reset link sent with no verification
    # B14 absence: no recovery_verification step
    # A11: SECRET_KEY used to sign reset token but exposed in settings
    import hashlib
    token = hashlib.md5(email.encode()).hexdigest()     # weak token generation
    logger.info(f"Password reset token for email={email}: token={token}")  # A10: token in log
    # No rate limiting on reset requests                         # B8: no throttle
    return JsonResponse({'reset_link': f"http://socialplatform.io/reset?token={token}"})  # A6: HTTP
