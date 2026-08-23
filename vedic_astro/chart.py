"""Birth chart (Rashi/Lagna kundli): planetary positions, ascendant, houses."""
from datetime import datetime, timedelta

from . import ephem
from .constants import (
    RASHIS, NAKSHATRAS, PLANET_ORDER, COMBUSTION_ORBS, COMBUSTION_ORBS_RETROGRADE,
    EXALTATION_LONGITUDE,
)

NAK_SPAN = 360.0 / 27.0


def _sign_position(sidereal_lon: float) -> dict:
    rashi_index = int(sidereal_lon // 30)
    degree_in_rashi = sidereal_lon - rashi_index * 30
    nak_index = int(sidereal_lon // NAK_SPAN)
    pada = int((sidereal_lon % NAK_SPAN) // (NAK_SPAN / 4)) + 1
    return {
        "longitude": sidereal_lon,
        "rashi": RASHIS[rashi_index],
        "rashi_index": rashi_index,
        "degree_in_rashi": degree_in_rashi,
        "nakshatra": NAKSHATRAS[nak_index],
        "pada": pada,
    }


def get_kundli(birth_dt_local: datetime, latitude: float, longitude: float, tz_offset: float) -> dict:
    """
    birth_dt_local: naive datetime in local civil time.
    latitude/longitude: degrees (longitude east positive).
    tz_offset: hours east of UTC (e.g. 5.5 for IST).
    """
    dt_utc = birth_dt_local - timedelta(hours=tz_offset)

    ayanamsa = ephem.lahiri_ayanamsa(dt_utc)
    asc_lon = ephem.sidereal_ascendant(dt_utc, latitude, longitude)
    ascendant = _sign_position(asc_lon)
    asc_rashi_index = ascendant["rashi_index"]

    sun_lon = ephem.sidereal_longitude("Sun", dt_utc)

    planets = []
    for name in PLANET_ORDER:
        lon = ephem.sidereal_longitude(name, dt_utc)
        pos = _sign_position(lon)
        house = ((pos["rashi_index"] - asc_rashi_index) % 12) + 1  # whole-sign houses
        retro = ephem.is_retrograde(name, dt_utc)

        sun_distance = abs((lon - sun_lon + 180) % 360 - 180)
        combust = False
        if name in COMBUSTION_ORBS:
            orb = COMBUSTION_ORBS_RETROGRADE.get(name, COMBUSTION_ORBS[name]) if retro else COMBUSTION_ORBS[name]
            combust = sun_distance <= orb

        # Exalted/debilitated by sign (not just the exact "deep exaltation"
        # degree). Not applicable to Rahu/Ketu -- their exaltation sign is
        # genuinely disputed across texts, so left unclassified here.
        exalted = debilitated = False
        if name in EXALTATION_LONGITUDE:
            exaltation_sign = int(EXALTATION_LONGITUDE[name] // 30)
            debilitation_sign = (exaltation_sign + 6) % 12
            exalted = pos["rashi_index"] == exaltation_sign
            debilitated = pos["rashi_index"] == debilitation_sign

        planets.append({
            "planet": name,
            "longitude": pos["longitude"],
            "rashi": pos["rashi"],
            "degree_in_rashi": pos["degree_in_rashi"],
            "nakshatra": pos["nakshatra"],
            "pada": pos["pada"],
            "retrograde": retro,
            "house": house,
            "sun_distance": sun_distance,
            "combust": combust,
            "exalted": exalted,
            "debilitated": debilitated,
        })

    return {
        "birth_datetime_local": birth_dt_local,
        "latitude": latitude,
        "longitude": longitude,
        "tz_offset": tz_offset,
        "ayanamsa": ayanamsa,
        "ascendant": ascendant,
        "planets": planets,
    }
