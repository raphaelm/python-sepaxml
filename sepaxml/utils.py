"""
Copyright (c) 2014 Congressus, The Netherlands
Copyright (c) 2017-2023 Raphael Michel and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import datetime
import hashlib
import random
import re
import time

try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    import warnings
    warnings.warn('A secure pseudo-random number generator is not available '
                  'on your system. Falling back to Mersenne Twister.')
    using_sysrandom = False


def get_rand_string(length=12, allowed_chars='0123456789abcdef'):
    """
    Returns a securely generated random string. Taken from the Django project

    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    if not using_sysrandom:
        # This is ugly, and a hack, but it makes things better than
        # the alternative of predictability. This re-seeds the PRNG
        # using a value that is hard for an attacker to predict, every
        # time a random string is required. This may change the
        # properties of the chosen random sequence slightly, but this
        # is better than absolute predictability.
        random.seed(
            hashlib.sha256(
                ("%s%s" % (
                    random.getstate(),
                    time.time())).encode('utf-8')
            ).digest())
    return ''.join([random.choice(allowed_chars) for i in range(length)])


def make_msg_id():
    """
    Create a semi random message id, by using 12 char random hex string and
    a timestamp.
    @return: string consisting of timestamp, -, random value
    """
    random_string = get_rand_string(12)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%I%M%S")
    msg_id = timestamp + "-" + random_string
    return msg_id


def make_id(name):
    """
    Create a random id combined with the creditor name.
    @return string consisting of name (truncated at 22 chars), -,
    12 char rand hex string.
    """
    name = re.sub(r'[^a-zA-Z0-9]', '', name)
    r = get_rand_string(12)
    if len(name) > 22:
        name = name[:22]
    return name + "-" + r


def int_to_decimal_str(integer):
    """
    Helper to convert integers (representing cents) into decimal currency
    string. WARNING: DO NOT TRY TO DO THIS BY DIVISION, FLOATING POINT
    ERRORS ARE NO FUN IN FINANCIAL SYSTEMS.
    @param integer The amount in cents
    @return string The amount in currency with full stop decimal separator
    """
    int_string = str(integer)
    if len(int_string) <= 2:
        return "0." + int_string.zfill(2)
    else:
        return int_string[:-2] + "." + int_string[-2:]


def decimal_str_to_int(decimal_string):
    """
    Helper to decimal currency string into integers (cents).
    WARNING: DO NOT TRY TO DO THIS BY CONVERSION AND MULTIPLICATION,
    FLOATING POINT ERRORS ARE NO FUN IN FINANCIAL SYSTEMS.
    @param string The amount in currency with full stop decimal separator
    @return integer The amount in cents
    """
    int_string = decimal_string.replace('.', '')
    int_string = int_string.lstrip('0')
    return int(int_string)


def validate_structured_description(description, format_type='ISO'):
    """
    Validate a structured communication description.

    @param description: The structured description string
    @param format_type: The format type ('BBA' for Belgian format, 'ISO' for ISO 11649 RF creditor reference, or None to skip validation)
    @return: True if valid, raises ValueError if invalid
    """
    # Skip validation if format_type is None or not recognized
    if format_type not in ('BBA', 'ISO'):
        return True

    if format_type == 'BBA':
        return _validate_bba_description(description)

    if format_type == 'ISO':
        return _validate_iso11649_description(description)


def _validate_bba_description(description):
    """
    Validate Belgian BBA structured description.

    BBA format: 12 digits in format XXX/XXXX/XXXCC where CC is check digit (modulo 97)

    @param description: The structured description string
    @return: True if valid, raises ValueError if invalid
    """
    # Remove any formatting characters (/, +, spaces)
    clean_ref = re.sub(r'[/+\s]', '', description)

    # Must be exactly 12 digits
    if not re.match(r'^\d{12}$', clean_ref):
        raise ValueError(
            f"STRUCTURED_DESCRIPTION_INVALID: BBA format requires exactly 12 digits, got '{description}'. "
            f"Format should be XXX/XXXX/XXXCC or 12 consecutive digits."
        )

    # Validate modulo 97 check digit
    # For BBA format, the check digit is calculated as: 97 - (base_number % 97)
    # If result is 0, use 97
    base_number = int(clean_ref[:10])
    check_digit = int(clean_ref[10:12])
    remainder = base_number % 97
    expected_check = 97 - remainder if remainder != 0 else 97

    if check_digit != expected_check:
        raise ValueError(
            f"STRUCTURED_DESCRIPTION_INVALID_CHECKSUM: Check digit should be {expected_check:02d}, got {check_digit:02d}"
        )

    return True


def _validate_iso11649_description(description):
    """
    Validate ISO 11649 RF creditor reference format for structured description.

    ISO 11649 format: RF + 2 check digits + up to 21 alphanumeric characters (max 25 total)
    Format: RFnn + creditor reference (where nn is the check digit)

    @param description: The structured description string
    @return: True if valid, raises ValueError if invalid
    """
    clean_ref = description.replace(' ', '').upper()

    # Must start with RF
    if not clean_ref.startswith('RF'):
        raise ValueError(
            f"STRUCTURED_DESCRIPTION_INVALID: ISO 11649 format must start with 'RF', got '{description}'"
        )

    # Must be between 4 and 25 characters (RF + 2 check digits + at least 0 and max 21 chars)
    if len(clean_ref) < 4 or len(clean_ref) > 25:
        raise ValueError(
            f"STRUCTURED_DESCRIPTION_INVALID: ISO 11649 format must be 4-25 characters, got {len(clean_ref)} characters"
        )

    # Check that positions 3-4 are digits (check digits)
    if not clean_ref[2:4].isdigit():
        raise ValueError(
            f"STRUCTURED_DESCRIPTION_INVALID: ISO 11649 check digits (positions 3-4) must be numeric, got '{clean_ref[2:4]}'"
        )

    # Check that the description part contains only alphanumeric characters
    ref_part = clean_ref[4:]
    if ref_part and not re.match(r'^[A-Z0-9]+$', ref_part):
        raise ValueError(
            f"STRUCTURED_DESCRIPTION_INVALID: ISO 11649 description must contain only alphanumeric characters, got '{ref_part}'"
        )

    # Validate modulo 97 check digit (same algorithm as IBAN)
    # Move RF and check digits to end, convert letters to numbers, calculate mod 97
    rearranged = clean_ref[4:] + clean_ref[:4]
    # Convert letters to numbers (A=10, B=11, ..., Z=35)
    numeric_string = ''
    for char in rearranged:
        if char.isdigit():
            numeric_string += char
        else:
            numeric_string += str(ord(char) - ord('A') + 10)

    checksum = int(numeric_string) % 97
    if checksum != 1:
        raise ValueError(
            f"STRUCTURED_DESCRIPTION_INVALID_CHECKSUM: ISO 11649 checksum validation failed for '{description}'"
        )

    return True


ADDRESS_MAPPING = (
    ("address_type", "AdrTp"),
    ("department", "Dept"),
    ("subdepartment", "SubDept"),
    ("street_name", "StrtNm"),
    ("building_number", "BldgNb"),
    ("postcode", "PstCd"),
    ("town", "TwnNm"),
    ("country_subdivision", "CtrySubDvsn"),
    ("country", "Ctry"),
)
