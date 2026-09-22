"""
Shadbala (six-fold planetary strength) and Bhavabala (house strength).

Classical Vedic (Parashari) system, restricted to the 7 classical grahas --
Rahu/Ketu have no shadbala in classical texts.

Roughly BPHS chapters 26-29, in the form B.V. Raman sets out in "Graha and
Bhava Balas", which is the reckoning AstroSage's Shadbala/Bhavabala tables
follow. Calibrated against one such table (31 Oct 2001, 10:17 IST, Kolkata).
Conventions worth recording, because sources disagree on several:

  - Saptavargaja Bala: the Panchadha Maitri is evaluated in the direction "how
    does the *occupying* graha regard its dispositor" -- BPHS's natural
    friendships are asymmetric, so the direction changes the answer -- and the
    tatkalika half is judged from the rasi chart, not the varga chart. Grades
    are 45/30/22.5/15/7.5/3.75/1.875 (some sources give 45/30/20/15/10/4/2).
  - Ojha-Yugma Bala: only the Moon and Venus want even signs; every other
    graha, Mercury included, wants odd ones.
  - Drekkana Bala: male planets (Sun/Mars/Jupiter) are strong in the 1st
    drekkana, hermaphrodite (Mercury/Saturn) in the 2nd, female (Moon/Venus)
    in the 3rd. Several overviews give this as male/female/hermaphrodite.
  - Nathonnata Bala: driven by the Sun's local hour angle (a fixed 12-hour
    half-day measured from local *apparent* noon/midnight), not by the true
    sunrise/sunset arc.
  - Tribhaga Bala: the lord of the current third of the day/night gets 60, and
    Jupiter gets 60 unconditionally on top of that rota.
  - Abda/Masa/Vara/Hora Bala: graded 15/30/45/60 virupas, not 15 each. Vara is
    the weekday lord at sunrise; the year and month lords come off the Ahargana
    rather than off the sankranti; the hora is counted in whole clock hours
    from the local midnight the Ahargana day boundary sits on.
  - Ayana Bala: (24 +/- kranti)/48 * 60, where the kranti is the declination of
    the planet's *ecliptic point* (latitude ignored) taken at the same
    classical 24-degree parama kranti, and the Sun's result is doubled.
  - Chesta Bala: Chesta Kendra = Seeghrochcha - (madhyama + sphuta graha)/2,
    with mean longitudes from modern mean orbital elements instead of the
    classical epicycle tables. Sun -> Ayana Bala, Moon -> Paksha Bala.
  - Drik Bala: Sphuta Drishti (a continuous piecewise-linear function of the
    exact ecliptic distance) plus the special-aspect additions -- Mars +15 on
    the 4th and 8th, Jupiter +30 on the 5th and 9th, Saturn +45 on the 3rd and
    10th -- benefics minus malefics, quartered.
  - Bhava Dig Bala: distance from the weak kendra counted in whole *houses*.
  - Bhava Drishti Bala: the same drishti on the Bhava Madhya, quartered per
    graha -- except Jupiter's and Mercury's, which count in full.
  - Yuddha Bala: implemented per Raman (only the 5 Tara Graha, within
    YUDDHA_ORB_DEGREES; quantum = |difference in Sthana+Dig+Kaala-up-to-Hora| /
    |difference in disc diameter|; winner is the lower longitude) but OFF by
    default, since the reference tables report no Yuddha Bala even for a pair
    3 arc-minutes apart. Pass apply_yuddha_bala=True to enable it.

Known differences against that reference table, both deliberate:
  - Its Sun Chesta Bala repeats its Sun Drik Bala to the last decimal, which
    looks like a bug on its side; the Sun keeps the documented rule here
    (Sun Chesta = Ayana Bala, Moon Chesta = Paksha Bala).
  - Saptavargaja matches it exactly for 5 of the 7 grahas; Mercury and Saturn
    come out 15 and 11.25 virupas higher. Nothing accounts for it: not the
    friendship direction, not any of the 15625 compound-table variants, not
    any of the 4096 tatkalika house-sets, not judging friendship from the
    varga chart, and not any of 216 combinations of alternative Hora /
    Drekkana / Saptamsa / Navamsa / Dwadasamsa / Trimsamsa division rules --
    the rules used here are the best available at 5 of 7, and every variant
    that fixes those two breaks others.

Residuals against that table elsewhere are sub-virupa: Ayana within 0.31 and
Chesta within 0.7, both from slightly different underlying positions and from
using modern mean elements in place of Surya-Siddhanta mean motions.
"""
import math
from datetime import timedelta

from . import ephem, varga
from .constants import (
    CLASSICAL_GRAHAS, RASHIS, RASHI_LORDS, MOOLATRIKONA, EXALTATION_LONGITUDE,
    NATURAL_FRIENDS, NATURAL_ENEMIES, RELATIONSHIP_POINTS, GENDER,
    DIG_BALA_FULL_HOUSE, CHALDEAN_ORDER, VARA_LORDS_FROM_SUNDAY,
    TRIBHAGA_DAY_LORDS, TRIBHAGA_NIGHT_LORDS, NAISARGIKA_RANK, REQUIRED_BALA_RUPAS,
    NATURAL_BENEFICS, SPHUTA_DRISHTI_SEGMENTS,
    ABDA_MASA_VARA_HORA_VIRUPAS, COMPONENT_MINIMUM_VIRUPAS,
    SPECIAL_ASPECT_BONUS, FULL_BHAVA_DRISHTI_GRAHAS,
    KALI_EPOCH_JD, AHARGANA_YEAR_DAYS, AHARGANA_MONTH_DAYS, AYANA_PARAMA_KRANTI,
    BHAVA_SIGN_GROUP_WEAK_HOUSE, YUDDHA_ELIGIBLE_PLANETS, YUDDHA_ORB_DEGREES,
    YUDDHA_DIAMETER_ARCSEC,
)

_VARGA_NAMES = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]


def _angular_sep(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _sign_index(longitude: float) -> int:
    return int(longitude // 30) % 12


def _house_distance(from_sign_index: int, to_sign_index: int) -> int:
    """1-12, counting from_sign_index as house 1."""
    return ((to_sign_index - from_sign_index) % 12) + 1


# --------------------------------------------------------------------------
# Panchadha Maitri (5-fold compound planetary friendship)
# --------------------------------------------------------------------------

def _natural_relationship(dispositor: str, occupant: str) -> str:
    if occupant in NATURAL_FRIENDS.get(dispositor, []):
        return "friend"
    if occupant in NATURAL_ENEMIES.get(dispositor, []):
        return "enemy"
    return "neutral"


def _temporal_relationship(dispositor_sign_idx: int, occupant_sign_idx: int) -> str:
    distance = _house_distance(dispositor_sign_idx, occupant_sign_idx)
    return "friend" if distance in (2, 3, 4, 10, 11, 12) else "enemy"


_COMPOUND_TABLE = {
    ("friend", "friend"): "adhimitra", ("friend", "enemy"): "sama",
    ("neutral", "friend"): "mitra", ("neutral", "enemy"): "shatru",
    ("enemy", "friend"): "sama", ("enemy", "enemy"): "adhishatru",
}


def _compound_relationship(graha: str, other: str, sign_indices: dict) -> str:
    """How `graha` regards `other`. The direction matters: BPHS's natural
    friendships are asymmetric (Mars counts the Moon a friend, the Moon counts
    Mars only neutral), so Saptavargaja Bala has to ask how the *occupying*
    planet regards its dispositor, not the other way round."""
    natural = _natural_relationship(graha, other)
    temporal = _temporal_relationship(sign_indices[graha], sign_indices[other])
    return _COMPOUND_TABLE[(natural, temporal)]


# --------------------------------------------------------------------------
# Sthana Bala (positional strength)
# --------------------------------------------------------------------------

def _uchcha_bala(planet: str, longitude: float) -> float:
    debilitation_point = (EXALTATION_LONGITUDE[planet] + 180.0) % 360.0
    return _angular_sep(longitude, debilitation_point) / 3.0  # max 60


def _saptavargaja_bala(planet: str, longitude: float, sign_indices: dict):
    rashi_index = int(longitude // 30)
    degree_in_sign = longitude - rashi_index * 30
    total = 0.0
    breakdown = []
    for i, varga_fn in enumerate(varga.SAPTAVARGA_DISPOSITORS):
        dispositor = varga_fn(longitude)
        if dispositor == planet:
            mt = MOOLATRIKONA.get(planet) if i == 0 else None
            if mt and mt[0] == rashi_index and mt[1] <= degree_in_sign < mt[2]:
                rel, pts = "moolatrikona", RELATIONSHIP_POINTS["moolatrikona"]
            else:
                rel, pts = "own", RELATIONSHIP_POINTS["own"]
        else:
            rel = _compound_relationship(planet, dispositor, sign_indices)
            pts = RELATIONSHIP_POINTS[rel]
        total += pts
        breakdown.append({"varga": _VARGA_NAMES[i], "dispositor": dispositor, "relationship": rel, "points": pts})
    return total, breakdown  # max 315 (7 * 45)


def _ojha_yugma_bala(planet: str, d1_sign_index: int, d9_sign_index: int) -> float:
    """15 virupas each for the Rashi and the Navamsa being of the planet's
    preferred parity. Only the Moon and Venus want even (yugma) signs; every
    other graha -- Mercury included -- wants odd (ojha) ones."""
    prefers_even = planet in ("Moon", "Venus")
    total = 0.0
    for sign_idx in (d1_sign_index, d9_sign_index):
        is_even_sign = sign_idx % 2 == 1
        if is_even_sign == prefers_even:
            total += 15.0
    return total  # max 30


def _kendradi_bala(house: int) -> float:
    if house in (1, 4, 7, 10):
        return 60.0
    if house in (2, 5, 8, 11):
        return 30.0
    return 15.0


# Gender of the 1st/2nd/3rd drekkana of a sign. Male planets (Sun/Mars/Jupiter)
# are strong in the first, hermaphrodite ones (Mercury/Saturn) in the second,
# female ones (Moon/Venus) in the third. Some overviews give this order as
# male/female/hermaphrodite; Raman's ordering is the one used here.
_DREKKANA_GENDER = ["male", "neuter", "female"]


def _drekkana_bala(planet: str, degree_in_sign: float) -> float:
    decan_gender = _DREKKANA_GENDER[int(degree_in_sign // 10)]
    return 15.0 if GENDER[planet] == decan_gender else 0.0


# --------------------------------------------------------------------------
# Dig Bala (directional strength)
# --------------------------------------------------------------------------

def _dig_bala(planet: str, longitude: float, angle_by_house: dict) -> float:
    full_house = DIG_BALA_FULL_HOUSE[planet]
    weak_house = ((full_house - 1 + 6) % 12) + 1  # opposite kendra
    return _angular_sep(longitude, angle_by_house[weak_house]) / 3.0  # max 60


# --------------------------------------------------------------------------
# Kaala Bala (temporal strength)
# --------------------------------------------------------------------------

def _day_night_bracket(dt_utc, latitude: float, longitude: float) -> dict:
    """Locates dt_utc within its bracketing sunrise/sunset (or sunset/next-sunrise)."""
    day0_noon = dt_utc.replace(hour=12, minute=0, second=0, microsecond=0)
    sunrise0, sunset0 = ephem.sunrise_sunset(day0_noon, latitude, longitude)

    if dt_utc < sunrise0:
        sunrise_prev, sunset_prev = ephem.sunrise_sunset(day0_noon - timedelta(days=1), latitude, longitude)
        return {"is_day": False, "sunrise": sunrise_prev, "sunset": sunset_prev, "next_sunrise": sunrise0}
    sunrise_next, _ = ephem.sunrise_sunset(day0_noon + timedelta(days=1), latitude, longitude)
    return {"is_day": dt_utc < sunset0, "sunrise": sunrise0, "sunset": sunset0, "next_sunrise": sunrise_next}


def _nathonnata_bala(planet: str, sun_hour_angle: float) -> float:
    """Diva/Ratri Bala from the classical "nata" -- the elapsed time from local
    apparent noon (or midnight), each half-day being a fixed 12 hours. That is
    exactly the Sun's local hour angle, so this is measured off the hour angle
    rather than off the true sunrise/sunset arc: at local apparent noon the
    diurnal planets get the full 60, at local apparent midnight the nocturnal
    ones do, and the pair always sums to 60."""
    if planet == "Mercury":
        return 60.0  # Mercury is strong by day and by night alike
    diurnal = 60.0 * (180.0 - abs(sun_hour_angle)) / 180.0
    return diurnal if planet in ("Sun", "Jupiter", "Venus") else 60.0 - diurnal


def _paksha_bala(planet: str, elongation: float) -> float:
    benefic_value = (180.0 - abs(elongation - 180.0)) / 3.0  # max 60 at full moon
    if planet == "Moon" or planet in NATURAL_BENEFICS:
        return benefic_value
    return 60.0 - benefic_value  # malefics: max 60 at new moon


def _tribhaga_bala(planet: str, dt_utc, bracket: dict) -> float:
    """The lord of the current third of the day (or of the night) gets 60 --
    and Jupiter gets 60 unconditionally, on top of that rota."""
    if planet == "Jupiter":
        return 60.0
    if bracket["is_day"]:
        third = (bracket["sunset"] - bracket["sunrise"]) / 3
        idx = min(2, int((dt_utc - bracket["sunrise"]) / third))
        lord = TRIBHAGA_DAY_LORDS[idx]
    else:
        third = (bracket["next_sunrise"] - bracket["sunset"]) / 3
        idx = min(2, int((dt_utc - bracket["sunset"]) / third))
        lord = TRIBHAGA_NIGHT_LORDS[idx]
    return 60.0 if planet == lord else 0.0


def _hora_lord(birth_dt_local, dina_lord: str) -> str:
    """Lord of the planetary hour. The horas run in descending Chaldean order
    from the lord of the vara, counted as whole clock hours from local midnight
    -- the same midnight the Ahargana day boundary sits on, which keeps this
    consistent with the Abda/Masa rules below."""
    elapsed_hours = int(birth_dt_local.hour + birth_dt_local.minute / 60.0
                        + birth_dt_local.second / 3600.0)
    return CHALDEAN_ORDER[(CHALDEAN_ORDER.index(dina_lord) + elapsed_hours) % 7]


def _abda_masa_vara_hora_lords(birth_dt_local, dt_utc, tz_offset: float, bracket: dict) -> dict:
    """Lords of the year (Abda/Varsha), month (Masa), weekday (Vara/Dina) and
    planetary hour (Hora), worth 15/30/45/60 virupas respectively.

    Vara is the weekday lord of the sunrise that opens the Hindu day. The year
    and month lords come off the Ahargana rather than off the sankranti: the
    schematic year is 360 days and its month 30, so stepping the birth weekday
    back by (ahargana mod 360) resp. (ahargana mod 30) days lands on the day
    that opens the current year resp. month. The extra -1 day is an Ahargana
    epoch convention (where day zero sits relative to sunrise); it is applied
    to both rules alike and is what reproduces the reference tables.
    """
    sunrise_local = bracket["sunrise"] + timedelta(hours=tz_offset)
    dina_index = (sunrise_local.weekday() + 1) % 7  # Python Mon=0 -> Sunday=0
    dina_lord = VARA_LORDS_FROM_SUNDAY[dina_index]

    ahargana = math.floor(ephem.julian_day(dt_utc) - KALI_EPOCH_JD)
    varsha_index = (dina_index - (ahargana % AHARGANA_YEAR_DAYS) - 1) % 7
    masa_index = (dina_index - (ahargana % AHARGANA_MONTH_DAYS) - 1) % 7

    return {
        "varsha": VARA_LORDS_FROM_SUNDAY[varsha_index],
        "masa": VARA_LORDS_FROM_SUNDAY[masa_index],
        "dina": dina_lord,
        "hora": _hora_lord(birth_dt_local, dina_lord),
    }


def _ayana_bala(planet: str, dt_utc) -> float:
    """(24 +/- kranti) / 48 * 60, i.e. 30 * (K + signed_kranti) / K with K the
    parama kranti, and the per-planet sign convention (Sun/Mars/Jupiter/Venus:
    north declination adds; Moon/Saturn: south adds; Mercury: the magnitude
    always adds).

    Kranti is the declination of the planet's *ecliptic point* -- derived from
    the sayana longitude with latitude ignored -- not the planet's apparent
    declination. That distinction is worth ~4 degrees for the Moon and shows up
    directly in the result. Because |kranti| <= K by construction the raw value
    stays inside 0-60 with no clamping.

    The Sun's Ayana Bala is then doubled.
    """
    eps = AYANA_PARAMA_KRANTI
    kranti = ephem.declination_of_ecliptic_point(
        ephem.tropical_longitude(planet, dt_utc), dt_utc, obliquity=eps)
    if planet == "Mercury":
        signed_kranti = abs(kranti)
    elif planet in ("Saturn", "Moon"):
        signed_kranti = -kranti
    else:  # Sun, Mars, Jupiter, Venus
        signed_kranti = kranti
    bala = 30.0 * (eps + signed_kranti) / eps
    return bala * 2.0 if planet == "Sun" else bala


# --------------------------------------------------------------------------
# Chesta Bala (motional strength)
# --------------------------------------------------------------------------

_SUPERIOR_GRAHAS = ("Mars", "Jupiter", "Saturn")


def _midpoint(a: float, b: float) -> float:
    """Circular midpoint of two longitudes, taking the short way round."""
    return (a + ((b - a + 180.0) % 360.0 - 180.0) / 2.0) % 360.0


def _chesta_bala(planet: str, ayana_bala_value: float, paksha_bala_value: float,
                 sun_longitude: float, planet_longitude: float, dt_utc) -> float:
    """Chesta Kendra = Seeghrochcha - (madhyama graha + sphuta graha) / 2,
    reduced to 0-180 and divided by 3.

    The Seeghrochcha is the Sun for the three superior planets and the planet's
    own mean heliocentric longitude for the two inferior ones -- and the
    "madhyama graha" (mean planet) swaps the same way round, being the mean
    heliocentric longitude for a superior planet and the Sun for an inferior
    one. Mean longitudes come from modern mean orbital elements rather than the
    classical epicycle tables, which leaves a residual of well under a virupa
    against tables built on Surya-Siddhanta mean motions.
    """
    if planet == "Sun":
        return ayana_bala_value  # BPHS: the Sun's Chesta Bala is its Ayana Bala
    if planet == "Moon":
        return paksha_bala_value  # BPHS: the Moon's Chesta Bala is its Paksha Bala

    ayanamsa = ephem.lahiri_ayanamsa(dt_utc)
    mean_graha = (ephem.mean_heliocentric_longitude(planet, dt_utc) - ayanamsa) % 360.0

    if planet in _SUPERIOR_GRAHAS:
        kendra = sun_longitude - _midpoint(mean_graha, planet_longitude)
    else:
        kendra = mean_graha - _midpoint(sun_longitude, planet_longitude)

    kendra %= 360.0
    reduced = kendra if kendra <= 180.0 else 360.0 - kendra
    return reduced / 3.0  # max 60 at the retrograde-station phase


# --------------------------------------------------------------------------
# Drik Bala (aspectual strength)
# --------------------------------------------------------------------------

def _sphuta_drishti(aspecting_planet: str, distance: float) -> float:
    """Sphuta Drishti in virupas, a continuous piecewise-linear function of the
    ecliptic distance measured *from* the aspecting graha *to* the aspected
    point. It reproduces the classical graded aspects at the house boundaries
    (15 on the 3rd, 45 on the 4th, 30 on the 5th, 60 on the 7th, 45 on the 8th,
    30 on the 9th, 15 on the 10th) but varies smoothly in between, which is why
    Drik Bala comes out in fractions of a virupa rather than multiples of 15.
    Mars, Jupiter and Saturn then add their special-aspect bonus on top."""
    distance %= 360.0
    value = 0.0
    for upper, slope, intercept in SPHUTA_DRISHTI_SEGMENTS:
        if distance < upper:
            value = slope * distance + intercept
            break
    for (lower, upper), bonus in SPECIAL_ASPECT_BONUS.get(aspecting_planet, ()):
        if lower <= distance < upper:
            value += bonus
    return value


def _is_benefic_aspect(aspecting_planet: str, planet_longitude: dict) -> bool:
    if aspecting_planet == "Moon":
        # Waxing Moon is a benefic, waning Moon a malefic.
        return ((planet_longitude["Moon"] - planet_longitude["Sun"]) % 360.0) < 180.0
    return aspecting_planet in NATURAL_BENEFICS


def _signed_drishti(aspecting_planet: str, target_longitude: float, planet_longitude: dict) -> float:
    """One graha's Sphuta Drishti on a point, positive if it is a benefic."""
    virupa = _sphuta_drishti(aspecting_planet, target_longitude - planet_longitude[aspecting_planet])
    return virupa if _is_benefic_aspect(aspecting_planet, planet_longitude) else -virupa


def _drik_bala(planet: str, planet_longitude: dict) -> float:
    """A graha's Drik Bala is the net drishti falling on it, quartered."""
    return sum(_signed_drishti(other, planet_longitude[planet], planet_longitude)
               for other in CLASSICAL_GRAHAS if other != planet) / 4.0


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def compute_shadbala(birth_dt_local, latitude: float, longitude: float, tz_offset: float,
                     apply_yuddha_bala: bool = False) -> dict:
    from .chart import get_kundli

    kundli = get_kundli(birth_dt_local, latitude, longitude, tz_offset)
    dt_utc = birth_dt_local - timedelta(hours=tz_offset)

    planet_longitude = {p["planet"]: p["longitude"] for p in kundli["planets"]}
    planet_house = {p["planet"]: p["house"] for p in kundli["planets"]}
    sign_indices = {pl: varga.d1_sign_index(lon) for pl, lon in planet_longitude.items() if pl in CLASSICAL_GRAHAS}

    bracket = _day_night_bracket(dt_utc, latitude, longitude)
    elongation = (planet_longitude["Moon"] - planet_longitude["Sun"]) % 360.0

    asc_lon = ephem.sidereal_ascendant(dt_utc, latitude, longitude)
    mc_lon = ephem.sidereal_mc(dt_utc, longitude)
    angle_by_house = {1: asc_lon, 4: (mc_lon + 180.0) % 360.0, 7: (asc_lon + 180.0) % 360.0, 10: mc_lon}

    sun_hour_angle = ephem.sun_hour_angle(dt_utc, longitude)
    vmdh_lords = _abda_masa_vara_hora_lords(birth_dt_local, dt_utc, tz_offset, bracket)

    results = {}
    for planet in CLASSICAL_GRAHAS:
        lon = planet_longitude[planet]
        rashi_index = int(lon // 30)
        degree_in_sign = lon - rashi_index * 30

        uchcha = _uchcha_bala(planet, lon)
        sapta_total, sapta_breakdown = _saptavargaja_bala(planet, lon, sign_indices)
        ojha_yugma = _ojha_yugma_bala(planet, varga.d1_sign_index(lon), varga.d9_sign_index(lon))
        kendradi = _kendradi_bala(planet_house[planet])
        drekkana = _drekkana_bala(planet, degree_in_sign)
        sthana_total = uchcha + sapta_total + ojha_yugma + kendradi + drekkana

        dig = _dig_bala(planet, lon, angle_by_house)

        nathonnata = _nathonnata_bala(planet, sun_hour_angle)
        paksha = _paksha_bala(planet, elongation)
        tribhaga = _tribhaga_bala(planet, dt_utc, bracket)
        vmdh_bala = sum(virupas for period, virupas in ABDA_MASA_VARA_HORA_VIRUPAS.items()
                        if vmdh_lords[period] == planet)
        ayana = _ayana_bala(planet, dt_utc)
        kaala_total = nathonnata + paksha + tribhaga + vmdh_bala + ayana

        chesta = _chesta_bala(planet, ayana, paksha, planet_longitude["Sun"], lon, dt_utc)
        naisargika = 60.0 * NAISARGIKA_RANK[planet] / 7.0
        drik = _drik_bala(planet, planet_longitude)

        # "Tri-bala till Hora": Sthana + Dig + Kaala-up-to-Hora (i.e. excluding
        # Ayana), used only for Yuddha Bala below.
        tribala_till_hora = sthana_total + dig + (nathonnata + paksha + tribhaga + vmdh_bala)

        total_virupa = sthana_total + dig + kaala_total + chesta + naisargika + drik
        total_rupa = total_virupa / 60.0
        required = REQUIRED_BALA_RUPAS[planet]

        results[planet] = {
            "longitude": lon,
            "sthana_bala": {
                "uchcha": uchcha, "saptavargaja": sapta_total, "saptavargaja_breakdown": sapta_breakdown,
                "ojha_yugma": ojha_yugma, "kendradi": kendradi, "drekkana": drekkana, "total": sthana_total,
            },
            "dig_bala": dig,
            "kaala_bala": {
                "nathonnata": nathonnata, "paksha": paksha, "tribhaga": tribhaga,
                "varsha_masa_dina_hora": vmdh_bala, "lords": vmdh_lords, "ayana": ayana, "total": kaala_total,
            },
            "chesta_bala": chesta,
            "naisargika_bala": naisargika,
            "drik_bala": drik,
            "yuddha_bala": 0.0,
            "tribala_till_hora": tribala_till_hora,
            "total_virupa": total_virupa,
            "total_rupa": total_rupa,
            "required_rupa": required,
            "sufficient": total_rupa >= required,
            "component_minimums": COMPONENT_MINIMUM_VIRUPAS[planet],
        }

    if apply_yuddha_bala:
        _apply_yuddha_bala(results)
    _apply_relative_rank(results)
    return results


def _apply_relative_rank(results: dict) -> None:
    """Ratio = attained rupas / required rupas, and the Relative Rank the
    grahas are classically ordered on (1 = strongest). The ranking goes on the
    ratio, not on the raw total: the requirements differ per graha, so a graha
    with a smaller total can still be the better placed one."""
    for data in results.values():
        data["ratio"] = data["total_rupa"] / data["required_rupa"]
    for rank, planet in enumerate(sorted(results, key=lambda p: results[p]["ratio"], reverse=True), 1):
        results[planet]["relative_rank"] = rank


def _apply_yuddha_bala(results: dict) -> None:
    """Planetary war (Graha Yuddha): only the 5 Tara Graha participate, and
    only when within YUDDHA_ORB_DEGREES of longitude. The winner (lower
    absolute longitude, per dineshcheramastro.com's stated convention -- an
    ambiguous rule right at the 0/360 wrap, which other texts resolve via
    latitude instead) gains the quantum in Kaala Bala/total; the loser loses
    it. Mutates `results` in place."""
    eligible = [p for p in YUDDHA_ELIGIBLE_PLANETS if p in results]
    for i in range(len(eligible)):
        for j in range(i + 1, len(eligible)):
            a, b = eligible[i], eligible[j]
            sep = _angular_sep(results[a]["longitude"], results[b]["longitude"])
            if sep >= YUDDHA_ORB_DEGREES:
                continue

            diff_diameter = abs(YUDDHA_DIAMETER_ARCSEC[a] - YUDDHA_DIAMETER_ARCSEC[b])
            diff_bala = abs(results[a]["tribala_till_hora"] - results[b]["tribala_till_hora"])
            quantum = diff_bala / diff_diameter

            winner, loser = (a, b) if results[a]["longitude"] < results[b]["longitude"] else (b, a)
            results[winner]["yuddha_bala"] += quantum
            results[loser]["yuddha_bala"] -= quantum

    for data in results.values():
        if data["yuddha_bala"] == 0.0:
            continue
        data["kaala_bala"]["total"] += data["yuddha_bala"]
        data["total_virupa"] += data["yuddha_bala"]
        data["total_rupa"] = data["total_virupa"] / 60.0
        data["sufficient"] = data["total_rupa"] >= data["required_rupa"]


def _sripati_bhava_madhyas(asc_lon: float, mc_lon: float) -> list:
    """The 12 Bhava-Madhya (house middle) points via the Sripati method:
    the 4 kendra madhyas are the true angles (Asc/IC/Desc/MC), and the
    intermediate houses trisect the ecliptic arc between successive kendras."""
    ic_lon = (mc_lon + 180.0) % 360.0
    desc_lon = (asc_lon + 180.0) % 360.0
    madhya = {1: asc_lon, 4: ic_lon, 7: desc_lon, 10: mc_lon}

    def trisect(start_house, end_house):
        start_lon, end_lon = madhya[start_house], madhya[end_house % 12 or 12]
        arc = (end_lon - start_lon) % 360.0
        step = arc / 3.0
        madhya[start_house + 1] = (start_lon + step) % 360.0
        madhya[start_house + 2] = (start_lon + 2 * step) % 360.0

    trisect(1, 4)
    trisect(4, 7)
    trisect(7, 10)
    trisect(10, 13)
    return [madhya[h] for h in range(1, 13)]


# Sign-group of each rashi (0=Mesha) for Bhava Dig Bala. Dhanu (8) and Makara (9)
# are split by degree between two groups (classical convention).
_CHATUSHPADA_SIGNS = {0, 1, 4}   # Mesha, Vrishabha, Simha
_NARA_SIGNS = {2, 5, 6, 10}       # Mithuna, Kanya, Tula, Kumbha
_KEETA_SIGNS = {7}                # Vrischika
_JALACHARA_SIGNS = {3, 11}        # Karka, Meena


def _bhava_sign_group(longitude: float) -> str:
    rashi_index = int(longitude // 30)
    degree = longitude - rashi_index * 30
    if rashi_index == 8:  # Dhanu: first half Nara, second half Chatushpada
        return "nara" if degree < 15.0 else "chatuspada"
    if rashi_index == 9:  # Makara: first half Chatushpada, second half Jalachara
        return "chatuspada" if degree < 15.0 else "jalachara"
    if rashi_index in _CHATUSHPADA_SIGNS:
        return "chatuspada"
    if rashi_index in _NARA_SIGNS:
        return "nara"
    if rashi_index in _KEETA_SIGNS:
        return "keeta"
    return "jalachara"  # _JALACHARA_SIGNS


def _bhava_dig_bala(house_number: int, bhava_madhya: float) -> float:
    """A bhava's Dig Bala is its distance -- counted in whole houses, not in
    degrees -- from the kendra where its own sign-group is weakest, times 30
    and divided by 3. So it always lands on a multiple of 10, from 0 at the
    weak kendra to 60 at the opposite one."""
    weak_house = BHAVA_SIGN_GROUP_WEAK_HOUSE[_bhava_sign_group(bhava_madhya)]
    houses_away = abs(house_number - weak_house)
    houses_away = min(houses_away, 12 - houses_away)
    return houses_away * 30.0 / 3.0


def _bhava_drishti_bala(bhava_madhya: float, planet_longitude: dict) -> float:
    """Net drishti falling on the Bhava Madhya. Each graha's drishti is
    quartered before being added or subtracted -- except Jupiter's and
    Mercury's, which count on a bhava in full."""
    total = 0.0
    for other in CLASSICAL_GRAHAS:
        signed = _signed_drishti(other, bhava_madhya, planet_longitude)
        total += signed if other in FULL_BHAVA_DRISHTI_GRAHAS else signed / 4.0
    return total


def compute_bhavabala(birth_dt_local, latitude: float, longitude: float, tz_offset: float,
                       shadbala_results: dict = None) -> list:
    from .chart import get_kundli

    if shadbala_results is None:
        shadbala_results = compute_shadbala(birth_dt_local, latitude, longitude, tz_offset)

    kundli = get_kundli(birth_dt_local, latitude, longitude, tz_offset)
    dt_utc = birth_dt_local - timedelta(hours=tz_offset)
    planet_longitude = {p["planet"]: p["longitude"] for p in kundli["planets"]}

    asc_lon = ephem.sidereal_ascendant(dt_utc, latitude, longitude)
    mc_lon = ephem.sidereal_mc(dt_utc, longitude)
    madhyas = _sripati_bhava_madhyas(asc_lon, mc_lon)

    results = []
    for house_num in range(1, 13):
        madhya = madhyas[house_num - 1]
        sign_idx = _sign_index(madhya)
        lord = RASHI_LORDS[sign_idx]

        bhavadhipati = shadbala_results.get(lord, {}).get("total_virupa", 0.0)
        dig = _bhava_dig_bala(house_num, madhya)
        drishti = _bhava_drishti_bala(madhya, planet_longitude)
        total_virupa = bhavadhipati + dig + drishti

        results.append({
            "house": house_num,
            "madhya": madhya,
            "sign": RASHIS[sign_idx],
            "lord": lord,
            "bhavadhipati_bala": bhavadhipati,
            "bhava_dig_bala": dig,
            "bhava_drishti_bala": drishti,
            "total_virupa": total_virupa,
            "total_rupa": total_virupa / 60.0,
        })

    for rank, bhava in enumerate(sorted(results, key=lambda h: h["total_virupa"], reverse=True), 1):
        bhava["relative_rank"] = rank

    return results
