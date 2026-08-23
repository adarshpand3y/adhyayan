"""
vedic_astro: standalone Vedic (sidereal / Lahiri) astrology calculation engine.

Pure Python, no Django dependency. Public API:

    get_panchang(date, latitude, longitude, tz_offset) -> dict
    get_kundli(birth_dt_local, latitude, longitude, tz_offset) -> dict
    get_vimshottari_dasha(birth_dt_local, latitude, longitude, tz_offset) -> list
    get_running_dasha(birth_dt_local, latitude, longitude, tz_offset, target_dt=None) -> list

Callers who already have a kundli dict from get_kundli() can also call
compute_vimshottari()/dasha_at() directly with the Moon's longitude -- see dasha.py.
"""
from datetime import timedelta

from .panchang import get_panchang
from .chart import get_kundli
from .dasha import compute_vimshottari, dasha_at, dasha_breakdown
from .strength import compute_shadbala, compute_bhavabala


def _moon_sidereal_longitude(birth_dt_local, latitude, longitude, tz_offset):
    from . import ephem
    dt_utc = birth_dt_local - timedelta(hours=tz_offset)
    return ephem.sidereal_longitude("Moon", dt_utc)


def get_vimshottari_dasha(birth_dt_local, latitude, longitude, tz_offset, levels: int = 2):
    """Convenience wrapper: computes the Moon's sidereal longitude at birth,
    then derives the full-life Mahadasha (+ optional Antardasha) list from it."""
    moon_longitude = _moon_sidereal_longitude(birth_dt_local, latitude, longitude, tz_offset)
    return compute_vimshottari(moon_longitude, birth_dt_local, levels=levels)


def get_running_dasha(birth_dt_local, latitude, longitude, tz_offset, target_dt=None, num_levels: int = 5):
    """Convenience wrapper: the Mahadasha/Antardasha/Pratyantardasha/Sookshma/
    Prana dasha chain active at target_dt (defaults to birth)."""
    moon_longitude = _moon_sidereal_longitude(birth_dt_local, latitude, longitude, tz_offset)
    return dasha_at(moon_longitude, birth_dt_local, target_dt, num_levels=num_levels)


def get_dasha_breakdown(birth_dt_local, latitude, longitude, tz_offset, target_dt=None, num_levels: int = 5):
    """Convenience wrapper: at each of the 5 dasha levels, all 9 sibling
    periods (start/end) around target_dt (defaults to birth)."""
    moon_longitude = _moon_sidereal_longitude(birth_dt_local, latitude, longitude, tz_offset)
    return dasha_breakdown(moon_longitude, birth_dt_local, target_dt, num_levels=num_levels)


__all__ = [
    "get_panchang", "get_kundli", "get_vimshottari_dasha", "get_running_dasha", "get_dasha_breakdown",
    "compute_vimshottari", "dasha_at", "dasha_breakdown",
    "compute_shadbala", "compute_bhavabala",
]
