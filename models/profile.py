"""
User profile and financial data model — SocialPlatform

Stores extended user data including financial and health information.
No field-level encryption, no retention schedule, no purpose tagging.
"""

import logging
from sqlalchemy import Column, String, Text, Integer, Boolean, Numeric, LargeBinary, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
logger = logging.getLogger(__name__)


class UserProfile(Base):
    """
    Extended user profile — stores sensitive personal, financial and health data.
    All fields stored in plaintext, no encryption at rest.
    """

    __tablename__ = 'user_profiles'

    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Financial data — stored plaintext (A7: no encryption at rest)
    credit_card     = Column(String(19))            # A7: card number plaintext
    card_cvv        = Column(String(4))             # A7: CVV plaintext — Critical
    bank_account    = Column(String(30))            # A7: IBAN/account plaintext
    sort_code       = Column(String(8))
    annual_income   = Column(Numeric(12, 2))

    # Health and medical data — sensitive category (A1, B3, Art 9 GDPR)
    health_condition = Column(Text)                 # A1/B3: health data
    medical_history  = Column(Text)                 # A1: medical records
    disability       = Column(String(100))          # A1: disability status
    mental_health    = Column(Text)                 # A1: mental health

    # Biometric
    retina_scan     = Column(LargeBinary)           # A1: retina scan
    iris_scan       = Column(LargeBinary)           # A1: iris scan
    voice_print     = Column(LargeBinary)           # A1: voice biometric

    # Sensitive profiling
    sexual_orientation = Column(String(50))         # A1/B3: sensitive category
    political_party    = Column(String(100))        # B3: political data
    trade_union        = Column(String(100))        # B3: trade union membership

    # Location
    home_latitude   = Column(Numeric(9, 6))
    home_longitude  = Column(Numeric(9, 6))
    ip_address      = Column(String(45))            # device/technical data

    # No retention_period defined                   # A14: no storage limitation
    # No purpose_of_collection defined              # A14: no purpose tagging
    # No data_retention_days                        # A14: no lifecycle policy


def save_financial_data(user_id, card_number, cvv, bank_account, income):
    """Save financial data — no encryption, no tokenisation."""
    logger.info(
        f"Saving financial: user={user_id} card={card_number} "   # A10: card in log
        f"cvv={cvv} bank={bank_account} income={income}"           # A10: CVV in log
    )
    profile = UserProfile(
        user_id=user_id,
        credit_card=card_number,     # A7: plaintext card
        card_cvv=cvv,                # A7: plaintext CVV
        bank_account=bank_account,
        annual_income=income,
    )
    # No sensitive_data_unencrypted check applied
    # No field-level encryption or tokenisation
    # No audit_log entry                           # A9: no audit trail
    return profile


def save_health_data(user_id, condition, history, disability):
    """Save health/medical data — no access controls, no encryption."""
    # A10: health data in log
    logger.info(f"Health data for user={user_id}: condition={condition} disability={disability}")
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if profile:
        profile.health_condition = condition        # A1: health stored unencrypted
        profile.medical_history  = history
        profile.disability       = disability
    # No consent_log entry for processing health data  # A2/B19
    # No lawful_basis recorded for Art 9 processing    # B19
    return profile


def bulk_export_profiles():
    """
    Export all profiles to CSV for analytics — no purpose limitation.
    """
    profiles = UserProfile.query.all()
    rows = []
    for p in profiles:
        # A10: mass PII log on export
        logger.info(
            f"Export row: user={p.user_id} card={p.credit_card} cvv={p.card_cvv} "  # A10
            f"bank={p.bank_account} health={p.health_condition} ssn_linked=true"
        )
        rows.append({
            'user_id': p.user_id,
            'credit_card': p.credit_card,           # A7: card in export
            'cvv': p.card_cvv,                      # A7: CVV in export — Critical
            'bank_account': p.bank_account,
            'health': p.health_condition,           # A1: health in export
            'sexual_orientation': p.sexual_orientation,  # B3: sensitive in export
            'political_party': p.political_party,   # B3
        })
    return rows
