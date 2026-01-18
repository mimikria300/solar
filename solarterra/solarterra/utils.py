import datetime as dt
import string
import re
from pytz import UTC


# time work

def make_aware(ts):
    return ts.replace(tzinfo=UTC)


# translates datetime instance into bigint
def ts_bigint_resolver(ts):
    return int(ts.timestamp())
    

# translates number into the datetime instance
def bigint_ts_resolver(num):
    return dt.datetime.fromtimestamp(num, UTC)

def str_to_dt(st, template="%Y-%m-%d %H:%M:%S"):
    return dt.datetime.strptime(st, template)

# here numbers are passed
def get_neighbour_interval(ts_limits, next_interval=True):

    t_delta = ts_limits[1] - ts_limits[0]
    if next_interval:
        return (ts_limits[1], ts_limits[1] + t_delta)
    else:
        return (ts_limits[0] - t_delta, ts_limits[0])


# string work
def normalize_str(st):
    return st.strip().replace(' ', '_')


def remove_parenthesis(st):
    return re.sub(r'\([^)]*\)', '', st).strip()

#also think about removing all repeating parts of the suffix strings

def safe_str(st):
    allowed = string.ascii_lowercase + string.digits + '_'
    parsed = normalize_str(remove_parenthesis(st)).lower()
    return ''.join(filter(lambda x: x in allowed, parsed))


# units formatting
def format_units(units: str) -> str:
    """Convert raw units like 'no/cm/cm/s' to a prettier form 'cm⁻²s⁻¹'.

    Rules:
    - Treat the first token as numerator unless it is dimensionless ('no', '1', '#', 'count').
    - Each subsequent token is a denominator term; identical terms are combined with negative exponents.
    - Strings that mean "no units" (e.g., 'None', 'NA', '1') are treated as dimensionless and return ''.
    - If no slashes are present, return the original units.
    """
    if not units:
        return ""

    s = str(units).strip()
    if not s:
        return ""

    s_lower = s.lower()
    # Consider common representations of dimensionless values as "no units"
    if s_lower in {"none", "na", "n/a", "null", "1", "unitless", "dimensionless", "no unit", "no units", "-"}:
        return ""

    if '/' not in s:
        return s

    tokens = [t for t in s.split('/') if t]
    if not tokens:
        return s

    dimless = {"no", "1", "#", "count", "num", "number"}

    numerator = []
    first = tokens[0].strip()
    if first.lower() not in dimless:
        numerator.append(first)

    denoms = tokens[1:] if len(tokens) > 1 else []

    counts = {}
    for raw in denoms:
        t = raw.strip()
        if not t:
            continue
        # combine identical denom terms as negative exponent
        counts[t] = counts.get(t, 0) - 1

    # format exponent with superscript digits
    sup = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}

    def exp_to_sup(n: int) -> str:
        if n == 0:
            return ""
        s = str(n)
        return "".join(sup.get(ch, ch) for ch in s)

    denom_parts = []
    for unit, exp in counts.items():
        if exp == 0:
            continue
        denom_parts.append(f"{unit}{exp_to_sup(exp)}")

    parts = numerator + denom_parts
    # join without spaces between dimensions (e.g., "cm⁻²s⁻¹")
    return "".join(parts) if parts else ""
