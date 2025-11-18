



import re

def validate_email_format(email: str) -> bool:
    pattern = r'^([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+)\.([A-Za-z]{2,})$'
    return re.match(pattern, email) is not None
