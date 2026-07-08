# Privacy Sample Code — SocialPlatform (Intentionally Vulnerable)

> **WARNING:** This codebase is intentionally vulnerable for privacy/trust demo purposes.
> Do NOT deploy. Do NOT use any credentials shown here.

## Purpose

Sample application designed to trigger the AI-SSDLC Digital Trust & Privacy scanner
across all 46 check criteria (A1–A18 Privacy + B1–B28 Trust & Safety).

## Files

| File | Primary checks triggered |
|------|--------------------------|
| `config/settings.py` | A11 (hardcoded secrets), A12 (DEBUG=True), A6 (no HSTS), B8 (rate_limit=False), B13 (insecure cookies) |
| `models/user.py` | A1 (PII over-collection, biometrics), A7 (plaintext password), A10 (PII in logs), B3 (race/religion mandatory) |
| `models/profile.py` | A7 (card/CVV/IBAN plaintext), A1 (health/biometric data), B3 (sexual orientation, political), A14 (no retention policy) |
| `views/registration.py` | A5 (skipValidation), A11 (csrf_exempt), A13 (Segment/FB/Mixpanel), A2 (no consent), B3 (demographics required) |
| `views/auth.py` | B13 (insecure cookies), A11 (csrf_exempt), A10 (credentials logged), B14 (no secure recovery) |
| `views/api.py` | B8 (ratelimit_exempt), A1 (SSN in API response), A7 (password in response), B18 (no DSAR endpoint) |
| `utils/analytics.py` | A13 (Segment/GA/FB/Mixpanel pre-consent), A10 (PII in logs), A4 (no opt-in), B3 (sensitive categories to 3rd parties) |
| `utils/error_handlers.py` | A12 (stack traces, DB internals in response), A10 (PII in exception logs), DEBUG=True |
| `templates/register.html` | A5 (novalidate), A6 (HTTP action), A3 (no cookie banner), A2 (no consent checkbox), B6 (no ToS link), B11 (no age gate) |
| `templates/dashboard.html` | A10 (PII in console.log), A4 (trackers pre-consent), A3 (no cookie banner), B1/B4/B6 (missing safety links) |

## Expected scanner output

- **Critical**: A7 (CVV/card/password plaintext), A11 (hardcoded secrets + CSRF off)
- **High**: A1, A2, A6, A10, A12, A13, B3, B8, B13, B18
- **Medium**: A3, A4, A5, A9, A14, A15, B6, B11, B14
- **Low / Info**: B2, B7, B16, B17, B20, B22, B27, B28
- **DPIA**: Should trigger (biometrics + health data + large-scale profiling)
