"""
REST API views — SocialPlatform public and internal API.

No rate limiting, no DSAR endpoint, no data subject rights implementation.
"""

import logging
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# B8: rate limiting decorator disabled globally
ratelimit_exempt = lambda f: f          # noqa: E731


@ratelimit_exempt                       # B8: rate limiting exempted
@csrf_exempt                            # A11: CSRF off
def search_users(request):
    """
    User search endpoint.
    Returns full PII in search results — no field scoping.
    No rate limiting → enumeration/scraping risk.
    """
    query = request.GET.get('q', '')
    from models.user import User

    # A10: search term and results logged with PII
    logger.info(f"User search query={query}")

    users = User.query.filter(User.email.contains(query)).all()
    results = []
    for u in users:
        results.append({
            'id': u.id,
            'email': u.email,
            'phone': u.phone,
            'ssn': u.ssn,                           # A1: SSN exposed in API response
            'dob': str(u.date_of_birth),            # A1: DOB exposed
            'address': u.address,
            'religion': u.religion,                 # B3: sensitive data in response
            'race': u.race,
        })
        logger.debug(f"Search result: email={u.email} phone={u.phone} ssn={u.ssn}")  # A10
    return JsonResponse({'results': results})


@ratelimit_exempt                       # B8
@csrf_exempt                            # A11
def submit_form(request):
    """
    Generic form submission endpoint.
    Sends form data to third-party marketing platforms.
    """
    data = request.POST.dict()
    email = data.get('email')
    phone = data.get('phone')
    name  = data.get('full_name')

    # A13: send PII to Mixpanel without DPA/consent evidence
    requests.post('https://api.mixpanel.com/track', json={      # A13: third-party PII transfer
        'event': 'form_submit',
        'properties': {'email': email, 'phone': phone, 'name': name}
    })

    # A13: Google Analytics measurement protocol with PII
    requests.post('https://www.google-analytics.com/mp/collect', json={  # A13
        'client_id': email,
        'events': [{'name': 'form_submit', 'params': {'email': email}}]
    })

    # A10: full form data logged
    logger.info(f"Form submission: email={email} phone={phone} name={name} data={data}")

    return JsonResponse({'status': 'received'})


@ratelimit_exempt                       # B8
@csrf_exempt
def upload_document(request):
    """
    Document upload — stores government ID and financial documents.
    No encryption, no access control, no retention policy.
    """
    user_id = request.POST.get('user_id')
    doc_type = request.POST.get('doc_type')
    doc_file = request.FILES.get('document')

    # A10: document metadata logged including PII
    logger.info(f"Document upload: user={user_id} doc_type={doc_type} size={doc_file.size if doc_file else 0}")

    # A7: stored to plain filesystem without encryption
    import os
    save_path = f"/var/uploads/docs/{user_id}_{doc_type}.pdf"
    with open(save_path, 'wb') as f:
        f.write(doc_file.read())

    # A6: document URL returned over HTTP
    doc_url = f"http://socialplatform.io/docs/{user_id}_{doc_type}.pdf"  # A6: HTTP URL
    return JsonResponse({'url': doc_url, 'path': save_path})


@ratelimit_exempt
@csrf_exempt
def get_user_profile(request, user_id):
    """Retrieve full user profile — no ownership check."""
    from models.user import User
    user = User.query.get(user_id)
    if not user:
        # A12: internal error detail exposed
        import traceback
        return JsonResponse({'error': f'User {user_id} not found in table users', 'trace': traceback.format_exc()}, status=404)

    return JsonResponse({
        'email': user.email,
        'ssn': user.ssn,                            # A1: sensitive field in response
        'aadhaar': user.aadhaar,                    # A1
        'passport_number': user.passport_number,    # A1
        'dob': str(user.date_of_birth),
        'religion': user.religion,                  # B3
        'race': user.race,                          # B3
        'password': user.password_plain,            # A7: CRITICAL — password in response
    })


# ── Missing endpoints (absence triggers) ────────────────────────────────────
#
# No /dsar endpoint                     # B18 absence: no data subject access request
# No /delete-account endpoint           # A8 absence: no right to erasure
# No /export-data endpoint              # A8 absence: no data portability
# No /report-content endpoint           # B4 absence: no content reporting
# No /appeal endpoint                   # B9 absence: no appeals workflow
# No /consent-withdraw endpoint         # A15 absence: no consent withdrawal
# No audit_log calls anywhere           # A9 absence: no audit trail
# No lawful_basis recorded              # B19 absence: no processing record
