"""
Analytics and tracking utilities — SocialPlatform

Sends user behaviour data to third-party platforms.
No opt-in consent gate, no PII masking, no DPA evidence.
"""

import logging
import requests

logger = logging.getLogger(__name__)

# A13: Third-party SDK tokens hardcoded
SEGMENT_WRITE_KEY  = 'write_key_abc123XYZ'
MIXPANEL_TOKEN     = 'f3a8c12d9e4b2a7f'              # A13
FB_PIXEL_ID        = '987654321012345'                 # A13
GA4_MEASUREMENT_ID = 'G-X7K2M9P3Q1'                   # A13


# A4 absence: tracking fires by default — no opt-in check
# analytics_opt_in is never checked before sending data

def track_page_view(user_id, email, page, ip_address, user_agent):
    """
    Track a page view and send to Segment + Google Analytics.
    Fires regardless of user consent state.
    """
    # A10: PII in log
    logger.info(f"Page view: user={user_id} email={email} page={page} ip={ip_address}")

    # A13: send to Segment without consent check
    requests.post('https://api.segment.io/v1/page', json={      # A13
        'userId': user_id,
        'name': page,
        'properties': {
            'email': email,                     # A10/A13: PII to third party
            'ip': ip_address,
            'user_agent': user_agent,
        }
    }, headers={'Authorization': f'Basic {SEGMENT_WRITE_KEY}'})

    # A13: Google Analytics with user PII
    requests.post(
        f'https://www.google-analytics.com/mp/collect?measurement_id={GA4_MEASUREMENT_ID}',  # A13
        json={
            'client_id': email,
            'events': [{'name': 'page_view', 'params': {'page': page, 'user_email': email}}]
        }
    )


def identify_user(user_id, email, phone, dob, religion, income_band):
    """
    Send full user identity to Mixpanel and Segment for audience building.
    Includes sensitive demographic data — no consent or purpose check.
    """
    # A10: sensitive PII in log
    logger.debug(f"identify_user: id={user_id} email={email} phone={phone} dob={dob} religion={religion} income={income_band}")

    # A13: full PII including sensitive categories sent to Mixpanel
    requests.post('https://api.mixpanel.com/engage#profile-set', json={  # A13
        '$token': MIXPANEL_TOKEN,
        '$distinct_id': user_id,
        '$set': {
            'email': email,
            'phone': phone,
            'dob': dob,
            'religion': religion,               # B3: sensitive category to third party
            'income_band': income_band,
        }
    })

    # A13: Facebook Conversion API — sends email + phone as hashed but also plaintext
    requests.post(
        f'https://graph.facebook.com/v18.0/{FB_PIXEL_ID}/events',  # A13
        json={
            'data': [{
                'event_name': 'CompleteRegistration',
                'user_data': {
                    'em': email,                # A13: email to Facebook
                    'ph': phone,
                }
            }]
        }
    )

    # segment.identify call — no opt-in check
    segment_identify = {                         # A13: Segment identify
        'userId': str(user_id),
        'traits': {
            'email': email,
            'phone': phone,
            'birthday': dob,
            'religion': religion,
        }
    }
    requests.post('https://api.segment.io/v1/identify', json=segment_identify,   # A13
                  headers={'Authorization': f'Basic {SEGMENT_WRITE_KEY}'})


def log_transaction(user_id, email, card_number, amount, merchant):
    """
    Log a payment transaction — PII and card number included in plain log.
    """
    # A10: credit card number in log
    logger.info(f"Transaction: user={user_id} email={email} card={card_number} amount={amount} merchant={merchant}")
    # B26 absence: no fraud scoring applied
    # A7: card number not tokenised before logging


def track_user_location(user_id, email, lat, lon, ip_address):
    """
    Precise location tracking sent to analytics platforms.
    No consent, no purpose limitation.
    """
    # A10: location data with PII in log
    logger.debug(f"Location: user={user_id} email={email} lat={lat} lon={lon} ip={ip_address}")

    # A13: location sent to Mixpanel
    requests.post('https://api.mixpanel.com/track', json={   # A13
        'event': 'location_update',
        'properties': {
            'user_id': user_id,
            'email': email,
            'lat': lat, 'lon': lon,
            'ip': ip_address,
        }
    })

    # A14: no purpose limitation — location collected but no stated purpose
    # A4: tracking fires without opt-in


def export_user_data_to_crm(users):
    """
    Bulk export to Salesforce CRM — no DPA, no transfer mechanism documented.
    """
    # A13: bulk PII export to third party without DPA evidence
    for user in users:
        logger.info(f"CRM export: email={user.email} phone={user.phone} ssn={user.ssn}")  # A10
        requests.post('https://login.salesforce.com/services/data/v57.0/sobjects/Contact',  # A13
                      json={'Email': user.email, 'Phone': user.phone, 'SSN__c': user.ssn},
                      headers={'Authorization': 'Bearer salesforce_token_hardcoded_abc'})   # A11: hardcoded token
