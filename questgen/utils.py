import re

FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z])([A-Z])')
DIGITS_CAP_RE = re.compile('([0-9]+)')

def camel_to_underscores(name):
    step_1 = DIGITS_CAP_RE.sub(r'_\1', name)
    step_2 = FIRST_CAP_RE.sub(r'\1_\2', step_1)
    result = ALL_CAP_RE.sub(r'\1_\2', step_2).lower()
    return result
