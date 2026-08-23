"""Daily Panchang: tithi, nakshatra, yoga, karana, weekday and choghadiya."""
from datetime import datetime, timedelta

from . import ephem
from .constants import (
    TITHI_NAMES, PAKSHA_NAMES, YOGA_NAMES, NAKSHATRAS,
    KARANA_MOVABLE, KARANA_FIXED, WEEKDAYS,
    CHOGHADIYA_DAY_SEQUENCE, CHOGHADIYA_NIGHT_SEQUENCE, CHOGHADIYA_NATURE,
)

NAK_SPAN = 360.0 / 27.0  # 13deg20'


def _elongation(dt_utc):
    return (ephem.sidereal_longitude("Moon", dt_utc) - ephem.sidereal_longitude("Sun", dt_utc)) % 360.0


def _moon_longitude(dt_utc):
    return ephem.sidereal_longitude("Moon", dt_utc)


def _yoga_value(dt_utc):
    return (ephem.sidereal_longitude("Moon", dt_utc) + ephem.sidereal_longitude("Sun", dt_utc)) % 360.0


def _find_boundary_time(value_fn, dt_start, step_size, max_days=3):
    """Find the time after dt_start when value_fn (an angle in [0,360)) next
    crosses a multiple of step_size, handling one wraparound past 360."""
    v0 = value_fn(dt_start)
    target = (int(v0 // step_size) + 1) * step_size

    t0, val0 = dt_start, v0
    t1 = dt_start
    step = timedelta(hours=3)
    for _ in range(int(max_days * 24 / 3) + 8):
        t1 = t1 + step
        v1 = value_fn(t1)
        if v1 < val0:
            v1 += 360.0
        if val0 <= target <= v1:
            break
        t0, val0 = t1, v1
    else:
        raise RuntimeError("panchang boundary not found within max_days")

    lo_t, lo_v = t0, val0
    hi_t, hi_v = t1, v1
    for _ in range(40):
        mid_t = lo_t + (hi_t - lo_t) / 2
        mid_v = value_fn(mid_t)
        if mid_v < lo_v:
            mid_v += 360.0
        if mid_v < target:
            lo_t, lo_v = mid_t, mid_v
        else:
            hi_t, hi_v = mid_t, mid_v
    return lo_t + (hi_t - lo_t) / 2


def get_panchang(date, latitude: float, longitude: float, tz_offset: float) -> dict:
    """
    date: a datetime.date for the local calendar day.
    latitude/longitude: degrees (longitude east positive).
    tz_offset: hours east of UTC (e.g. 5.5 for IST).
    """
    local_midnight_utc = datetime(date.year, date.month, date.day) - timedelta(hours=tz_offset)
    approx_noon_utc = local_midnight_utc + timedelta(hours=12)

    sunrise_utc, sunset_utc = ephem.sunrise_sunset(approx_noon_utc, latitude, longitude)
    if sunrise_utc is None or sunset_utc is None:
        raise ValueError("Could not compute sunrise/sunset for this date/location (polar day/night?)")

    next_day_noon_utc = approx_noon_utc + timedelta(days=1)
    next_sunrise_utc, _ = ephem.sunrise_sunset(next_day_noon_utc, latitude, longitude)

    def to_local(dt):
        return dt + timedelta(hours=tz_offset)

    sunrise_local = to_local(sunrise_utc)
    sunset_local = to_local(sunset_utc)

    weekday = WEEKDAYS[sunrise_local.weekday()]

    # --- Tithi ---
    elong = _elongation(sunrise_utc)
    tithi_index = int(elong // 12)
    tithi_end_utc = _find_boundary_time(_elongation, sunrise_utc, 12.0)
    tithi = {
        "name": TITHI_NAMES[tithi_index],
        "number": (tithi_index % 15) + 1,
        "paksha": PAKSHA_NAMES[0] if tithi_index < 15 else PAKSHA_NAMES[1],
        "ends_at": to_local(tithi_end_utc),
    }

    # --- Nakshatra (of the Moon) ---
    moon_lon = _moon_longitude(sunrise_utc)
    nak_index = int(moon_lon // NAK_SPAN)
    nak_end_utc = _find_boundary_time(_moon_longitude, sunrise_utc, NAK_SPAN)
    nakshatra = {
        "name": NAKSHATRAS[nak_index],
        "pada": int((moon_lon % NAK_SPAN) // (NAK_SPAN / 4)) + 1,
        "ends_at": to_local(nak_end_utc),
    }

    # --- Yoga ---
    yoga_val = _yoga_value(sunrise_utc)
    yoga_index = int(yoga_val // NAK_SPAN)
    yoga_end_utc = _find_boundary_time(_yoga_value, sunrise_utc, NAK_SPAN)
    yoga = {
        "name": YOGA_NAMES[yoga_index],
        "ends_at": to_local(yoga_end_utc),
    }

    # --- Karana (half-tithi) ---
    karana_number = int(elong // 6)  # 0..59 across the synodic month
    karana_end_utc = _find_boundary_time(_elongation, sunrise_utc, 6.0)
    if karana_number == 0:
        karana_name = KARANA_FIXED[3]  # Kimstughna
    elif karana_number >= 57:
        karana_name = KARANA_FIXED[karana_number - 57]  # Shakuni, Chatushpada, Naga
    else:
        karana_name = KARANA_MOVABLE[(karana_number - 1) % 7]
    karana = {"name": karana_name, "ends_at": to_local(karana_end_utc)}

    # --- Choghadiya ---
    choghadiya = []
    day_seq = CHOGHADIYA_DAY_SEQUENCE[weekday]
    day_slot = (sunset_local - sunrise_local) / 8
    for i, name in enumerate(day_seq):
        start = sunrise_local + i * day_slot
        end = start + day_slot
        choghadiya.append({"period": "Day", "name": name, "nature": CHOGHADIYA_NATURE[name], "start": start, "end": end})

    if next_sunrise_utc is not None:
        next_sunrise_local = to_local(next_sunrise_utc)
        night_seq = CHOGHADIYA_NIGHT_SEQUENCE[weekday]
        night_slot = (next_sunrise_local - sunset_local) / 8
        for i, name in enumerate(night_seq):
            start = sunset_local + i * night_slot
            end = start + night_slot
            choghadiya.append({"period": "Night", "name": name, "nature": CHOGHADIYA_NATURE[name], "start": start, "end": end})

    return {
        "date": date,
        "weekday": weekday,
        "sunrise": sunrise_local,
        "sunset": sunset_local,
        "tithi": tithi,
        "nakshatra": nakshatra,
        "yoga": yoga,
        "karana": karana,
        "choghadiya": choghadiya,
    }
