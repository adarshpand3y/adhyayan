"""
Thin wrapper around Skyfield that provides sidereal (nirayana) positions
for Vedic astrology: planetary longitudes, the ascendant, and sunrise/sunset.

No Django dependency -- this module is plain Python + Skyfield and can be
imported and tested on its own.

Accuracy note: pyswisseph (the usual gold-standard engine for Vedic charts)
requires a C compiler to build on Windows, which wasn't available in this
environment, so this uses Skyfield (pure Python, JPL DE421 ephemeris) instead.
Planetary positions from DE421 are accurate to sub-arcsecond level. The one
approximation here is the Lahiri ayanamsa, computed from a well-known
precession-based polynomial rather than Swiss Ephemeris's fixed-star-based
definition; the two agree to within a few arcseconds for 1900-2100, which is
fine for prototyping but should be revisited if this becomes production code.
"""
import math
import os
from datetime import datetime, timedelta

from skyfield.api import Loader, wgs84

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(_DATA_DIR, exist_ok=True)
_load = Loader(_DATA_DIR)

_ts = _load.timescale()
_eph = _load("de421.bsp")

_earth = _eph["earth"]
_BODIES = {
    "Sun": _eph["sun"],
    "Moon": _eph["moon"],
    "Mercury": _eph["mercury"],
    "Venus": _eph["venus"],
    "Mars": _eph["mars"],
    "Jupiter": _eph["jupiter barycenter"],
    "Saturn": _eph["saturn barycenter"],
}


def to_skyfield_time(dt_utc: datetime):
    """dt_utc must be a naive datetime already expressed in UTC."""
    return _ts.utc(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour, dt_utc.minute, dt_utc.second + dt_utc.microsecond / 1e6,
    )


def julian_day(dt_utc: datetime) -> float:
    return to_skyfield_time(dt_utc).ut1


def lahiri_ayanamsa(dt_utc: datetime) -> float:
    """Lahiri (Chitrapaksha) ayanamsa in degrees, precession-polynomial approximation."""
    jd = julian_day(dt_utc)
    t = (jd - 2415020.0) / 36525.0  # Julian centuries since 1900.0
    return 22.46 + 1.396042 * t + 0.000308 * t * t


def tropical_longitude(body_name: str, dt_utc: datetime) -> float:
    """Apparent geocentric tropical (of-date) ecliptic longitude, in degrees [0, 360)."""
    t = to_skyfield_time(dt_utc)
    astrometric = _earth.at(t).observe(_BODIES[body_name]).apparent()
    lat, lon, _ = astrometric.ecliptic_latlon(epoch="date")
    return lon.degrees % 360.0


def mean_lunar_node_longitude(dt_utc: datetime) -> float:
    """Mean longitude of the Moon's ascending node (Rahu), tropical, in degrees.

    Standard Meeus (Astronomical Algorithms, ch. 47) polynomial.
    """
    jd = julian_day(dt_utc)
    t = (jd - 2451545.0) / 36525.0  # Julian centuries since J2000.0
    omega = (
        125.0445479
        - 1934.1362891 * t
        + 0.0020754 * t * t
        + (t ** 3) / 467441.0
        - (t ** 4) / 60616000.0
    )
    return omega % 360.0


def sidereal_longitude(body_name: str, dt_utc: datetime) -> float:
    ayanamsa = lahiri_ayanamsa(dt_utc)
    if body_name == "Rahu":
        tropical = mean_lunar_node_longitude(dt_utc)
    elif body_name == "Ketu":
        tropical = (mean_lunar_node_longitude(dt_utc) + 180.0) % 360.0
    else:
        tropical = tropical_longitude(body_name, dt_utc)
    return (tropical - ayanamsa) % 360.0


def is_retrograde(body_name: str, dt_utc: datetime) -> bool:
    """True if the body's tropical longitude is decreasing (Sun/Moon are never retrograde)."""
    if body_name in ("Sun", "Moon", "Rahu", "Ketu"):
        # Rahu/Ketu (mean node) are always retrograde by convention.
        return body_name in ("Rahu", "Ketu")
    dt_before = dt_utc - timedelta(hours=12)
    dt_after = dt_utc + timedelta(hours=12)
    lon_before = tropical_longitude(body_name, dt_before)
    lon_after = tropical_longitude(body_name, dt_after)
    delta = (lon_after - lon_before + 540.0) % 360.0 - 180.0
    return delta < 0


def local_sidereal_time_degrees(dt_utc: datetime, longitude_east: float) -> float:
    """Greenwich Apparent Sidereal Time (from Skyfield) converted to local, in degrees."""
    t = to_skyfield_time(dt_utc)
    gast_hours = t.gast
    lst_hours = (gast_hours + longitude_east / 15.0) % 24.0
    return lst_hours * 15.0


def obliquity_of_ecliptic(dt_utc: datetime) -> float:
    jd = julian_day(dt_utc)
    t = (jd - 2451545.0) / 36525.0
    eps = 23.4392911 - 0.0130042 * t - 1.64e-7 * t * t + 5.04e-7 * t ** 3
    return eps


def tropical_ascendant(dt_utc: datetime, latitude: float, longitude_east: float) -> float:
    """Tropical ecliptic longitude of the ascendant, in degrees [0, 360)."""
    ramc = math.radians(local_sidereal_time_degrees(dt_utc, longitude_east))
    eps = math.radians(obliquity_of_ecliptic(dt_utc))
    phi = math.radians(latitude)

    y = math.cos(ramc)
    x = -(math.sin(ramc) * math.cos(eps) + math.tan(phi) * math.sin(eps))
    asc = math.degrees(math.atan2(y, x)) % 360.0
    return asc


def sidereal_ascendant(dt_utc: datetime, latitude: float, longitude_east: float) -> float:
    ayanamsa = lahiri_ayanamsa(dt_utc)
    return (tropical_ascendant(dt_utc, latitude, longitude_east) - ayanamsa) % 360.0


def tropical_mc(dt_utc: datetime, longitude_east: float) -> float:
    """Tropical ecliptic longitude of the Midheaven (MC): the ecliptic point
    currently on the local meridian, i.e. whose right ascension equals RAMC."""
    ramc = math.radians(local_sidereal_time_degrees(dt_utc, longitude_east))
    eps = math.radians(obliquity_of_ecliptic(dt_utc))
    mc = math.degrees(math.atan2(math.sin(ramc), math.cos(ramc) * math.cos(eps))) % 360.0
    return mc


def sidereal_mc(dt_utc: datetime, longitude_east: float) -> float:
    ayanamsa = lahiri_ayanamsa(dt_utc)
    return (tropical_mc(dt_utc, longitude_east) - ayanamsa) % 360.0


def declination(body_name: str, dt_utc: datetime) -> float:
    """Apparent geocentric declination of a body, in degrees."""
    t = to_skyfield_time(dt_utc)
    astrometric = _earth.at(t).observe(_BODIES[body_name]).apparent()
    _, dec, _ = astrometric.radec(epoch="date")
    return dec.degrees


def declination_of_ecliptic_point(longitude: float, dt_utc: datetime) -> float:
    """Declination of a point of ecliptic latitude 0 at the given tropical longitude
    (used for Rahu/Ketu, which have no direct Skyfield body)."""
    eps = math.radians(obliquity_of_ecliptic(dt_utc))
    lam = math.radians(longitude)
    return math.degrees(math.asin(math.sin(eps) * math.sin(lam)))


def daily_motion(body_name: str, dt_utc: datetime) -> float:
    """Signed tropical longitude motion in degrees/day (negative = retrograde),
    via a central finite difference over 2 days."""
    if body_name == "Rahu":
        lon_before = mean_lunar_node_longitude(dt_utc - timedelta(hours=12))
        lon_after = mean_lunar_node_longitude(dt_utc + timedelta(hours=12))
    elif body_name == "Ketu":
        lon_before = (mean_lunar_node_longitude(dt_utc - timedelta(hours=12)) + 180.0) % 360.0
        lon_after = (mean_lunar_node_longitude(dt_utc + timedelta(hours=12)) + 180.0) % 360.0
    else:
        lon_before = tropical_longitude(body_name, dt_utc - timedelta(hours=12))
        lon_after = tropical_longitude(body_name, dt_utc + timedelta(hours=12))
    delta = (lon_after - lon_before + 540.0) % 360.0 - 180.0
    return delta  # degrees per day (over the 24h window spanning dt_utc)


def sunrise_sunset(date_utc_noon: datetime, latitude: float, longitude_east: float):
    """Returns (sunrise_utc, sunset_utc) datetimes for the UTC calendar day containing
    date_utc_noon, at the given location, using Skyfield's almanac search."""
    from skyfield import almanac

    topos = wgs84.latlon(latitude, longitude_east)
    observer = _earth + topos

    t0 = _ts.utc(date_utc_noon.year, date_utc_noon.month, date_utc_noon.day, -6)
    t1 = _ts.utc(date_utc_noon.year, date_utc_noon.month, date_utc_noon.day, 30)

    f = almanac.sunrise_sunset(_eph, topos)
    times, events = almanac.find_discrete(t0, t1, f)

    sunrise = sunset = None
    for t, ev in zip(times, events):
        if ev == 1 and sunrise is None:
            sunrise = t.utc_datetime().replace(tzinfo=None)
        elif ev == 0 and sunset is None and sunrise is not None:
            sunset = t.utc_datetime().replace(tzinfo=None)
    return sunrise, sunset
