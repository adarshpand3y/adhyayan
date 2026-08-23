"""Vimshottari dasha calculation, based on the Moon's nakshatra at birth.

Supports the full classical 5-limb hierarchy:
    Mahadasha -> Antardasha -> Pratyantardasha -> Sookshma Dasha -> Prana Dasha

Each level is a proportional subdivision of its parent, cycling the same
9-planet sequence starting from the parent period's own lord. The full tree
explodes combinatorially (9^5 = 59049 leaf Prana-dasha periods across a
lifetime), so compute_vimshottari() only builds Mahadasha (+ optional
Antardasha) for a life-spanning table, while dasha_at() drills down through
all 5 levels for one specific moment in time.
"""
from datetime import datetime, timedelta

from .constants import DASHA_SEQUENCE, DASHA_YEARS, NAKSHATRA_LORDS, VIMSHOTTARI_TOTAL_YEARS

NAK_SPAN = 360.0 / 27.0
DAYS_PER_YEAR = 365.25

DASHA_LEVEL_NAMES = ["Mahadasha", "Antardasha", "Pratyantardasha", "Sookshma Dasha", "Prana Dasha"]


def _add_years(dt: datetime, years: float) -> datetime:
    return dt + timedelta(days=years * DAYS_PER_YEAR)


def _sub_periods(lord: str, start: datetime, duration_years: float) -> list:
    """The 9 sub-periods of a dasha period: the standard sequence starting
    from the period's own lord, each given a share of duration_years
    proportional to its usual 120-year allotment."""
    start_index = DASHA_SEQUENCE.index(lord)
    periods = []
    current_start = start
    for i in range(9):
        sub_lord = DASHA_SEQUENCE[(start_index + i) % 9]
        years = duration_years * DASHA_YEARS[sub_lord] / VIMSHOTTARI_TOTAL_YEARS
        end = _add_years(current_start, years)
        periods.append({"lord": sub_lord, "start": current_start, "end": end, "years": years})
        current_start = end
    return periods


def _find_containing(periods: list, target_dt: datetime) -> dict:
    for p in periods:
        if p["start"] <= target_dt < p["end"]:
            return p
    return periods[0] if target_dt < periods[0]["start"] else periods[-1]


def compute_vimshottari(moon_sidereal_longitude: float, birth_dt_local: datetime, levels: int = 2) -> list:
    """Returns the 9 Mahadasha periods covering the full 120-year cycle from birth.
    Each entry has 'lord', 'start', 'end', 'years' and (if levels >= 2) 'antardashas'."""
    nak_index = int(moon_sidereal_longitude // NAK_SPAN)
    birth_lord = NAKSHATRA_LORDS[nak_index]
    fraction_remaining = 1.0 - (moon_sidereal_longitude % NAK_SPAN) / NAK_SPAN

    start_index = DASHA_SEQUENCE.index(birth_lord)
    mahadashas = []
    current_start = birth_dt_local

    for i in range(9):
        lord = DASHA_SEQUENCE[(start_index + i) % 9]
        full_years = DASHA_YEARS[lord]
        years = full_years * fraction_remaining if i == 0 else full_years
        end = _add_years(current_start, years)
        entry = {"lord": lord, "start": current_start, "end": end, "years": years, "partial": i == 0}
        if levels >= 2:
            entry["antardashas"] = _sub_periods(lord, current_start, years)
        mahadashas.append(entry)
        current_start = end

    return mahadashas


def dasha_at(moon_sidereal_longitude: float, birth_dt_local: datetime, target_dt: datetime = None,
             num_levels: int = 5) -> list:
    """Drills down Mahadasha -> Antardasha -> Pratyantardasha -> Sookshma Dasha
    -> Prana Dasha, returning the period active at target_dt (defaults to
    birth) at each of num_levels levels, as a list of
    {'level', 'lord', 'start', 'end', 'years'} dicts, outermost level first."""
    if target_dt is None:
        target_dt = birth_dt_local

    mahadashas = compute_vimshottari(moon_sidereal_longitude, birth_dt_local, levels=1)
    period = _find_containing(mahadashas, target_dt)
    chain = [{"level": DASHA_LEVEL_NAMES[0], **period}]

    for level_name in DASHA_LEVEL_NAMES[1:num_levels]:
        sub_periods = _sub_periods(period["lord"], period["start"], period["years"])
        period = _find_containing(sub_periods, target_dt)
        chain.append({"level": level_name, **period})

    return chain


def dasha_breakdown(moon_sidereal_longitude: float, birth_dt_local: datetime, target_dt: datetime = None,
                     num_levels: int = 5) -> list:
    """Like dasha_at(), but at each level returns *all 9* sibling periods
    (with start/end) instead of just the active one -- only descending into
    the active branch to list the next level's 9 periods, so the result stays
    bounded (5 * 9 = 45 periods) instead of enumerating the whole 9^5 tree.

    Returns a list of {'level', 'periods', 'active_index'} dicts, where
    'periods' is the list of 9 sibling {'lord', 'start', 'end', 'years'}
    dicts and 'active_index' is the index of the one containing target_dt.
    """
    if target_dt is None:
        target_dt = birth_dt_local

    periods = compute_vimshottari(moon_sidereal_longitude, birth_dt_local, levels=1)
    breakdown = []
    for level_name in DASHA_LEVEL_NAMES[:num_levels]:
        active = _find_containing(periods, target_dt)
        active_index = periods.index(active)
        breakdown.append({"level": level_name, "periods": periods, "active_index": active_index})
        periods = _sub_periods(active["lord"], active["start"], active["years"])

    return breakdown
