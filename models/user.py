"""
User model — SocialPlatform

Stores user account, PII, and profile data.
"""

import logging
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Date, Text, Integer, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
logger = logging.getLogger(__name__)


class User(Base):
    """Primary user account model."""

    __tablename__ = 'users'

    id              = Column(Integer, primary_key=True)
    username        = Column(String(80), unique=True, nullable=False)
    email           = Column(String(255), unique=True, nullable=False)

    # A7: plaintext password storage — no bcrypt/argon2/pbkdf2
    password_plain  = Column(String(128), nullable=False)       # A7: plaintext password
    password_column = Column('varchar')                          # A7: trigger pattern

    # A1: over-collection of PII beyond stated purpose
    date_of_birth   = Column(Date, nullable=False)               # A1: DOB mandatory
    ssn             = Column(String(11))                         # A1: SSN collected
    aadhaar         = Column(String(12))                         # A1: Aadhaar number
    passport_number = Column(String(20))                         # A1: passport
    driving_license = Column(String(30))                         # A1: driving licence

    # B3: sensitive demographic fields collected
    religion        = Column(String(50), nullable=False)         # B3: religion mandatory
    race            = Column(String(50), nullable=False)         # B3: race mandatory
    political_affiliation = Column(String(100))                  # B3: political affiliation

    # A1: biometric data
    biometric       = Column(LargeBinary)                        # A1: biometric blob
    facial_image    = Column(LargeBinary)                        # A1: face image
    fingerprint     = Column(LargeBinary)                        # A1: fingerprint

    # Contact
    phone           = Column(String(20))
    address         = Column(Text)

    # Account flags — no MFA support (B13 absence)
    is_active       = Column(Boolean, default=True)
    is_verified     = Column(Boolean, default=False)
    # No two_factor / mfa / totp column                         # B13: no MFA

    created_at      = Column(Date, default=datetime.utcnow)


def create_user(email, password, dob, ssn=None, phone=None, religion=None, race=None):
    """Create a new user account — stores password in plaintext."""
    # A10: PII logged before storage
    logger.debug(f"Creating user — email={email} password={password} dob={dob} ssn={ssn}")
    # A10: phone number in log
    logger.info(f"New registration from phone={phone} with email={email}")

    user = User(
        email=email,
        password_plain=password,        # A7: no hashing applied
        date_of_birth=dob,
        ssn=ssn,
        religion=religion,
        race=race,
    )
    return user


def authenticate(email, password):
    """Authenticate by comparing plaintext passwords."""
    # A10: password exposed in log
    logger.debug(f"Auth attempt — email={email} password={password}")
    user = User.query.filter_by(email=email, password_plain=password).first()
    if user is None:
        # A12: internal detail leaked to caller
        raise Exception(f"No user found with email={email} in table users — check DB connection at db.internal:5432")
    return user


def update_profile(user_id, data):
    """Update user profile fields."""
    user = User.query.get(user_id)
    for key, value in data.items():
        setattr(user, key, value)
        # A10: PII written to log on every profile change
        logger.info(f"Updated user {user.email} field {key}={value}")
    # No audit_log written                                       # A9: no audit trail
    return user


def get_all_users():
    """Admin export of all user records — no access control check."""
    users = User.query.all()
    # A10: full PII dump to log
    for u in users:
        logger.info(f"User export: id={u.id} email={u.email} ssn={u.ssn} dob={u.date_of_birth} phone={u.phone}")
    return users


def delete_user_stub(user_id):
    """Stub — account deletion not fully implemented."""
    # A8 absence: no right_to_erasure implemented
    # No delete_account endpoint properly connected
    logger.warning(f"Delete requested for {user_id} — NOT YET IMPLEMENTED")
    pass
