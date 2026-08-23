"""
Shadbala (six-fold planetary strength) and Bhavabala (house strength).

Classical Vedic (Parashari) system, restricted to the 7 classical grahas --
Rahu/Ketu have no shadbala in classical texts.

This is a from-scratch reimplementation of several dozen classical
sub-formulas (roughly BPHS chapters 26-29), cross-checked against multiple
secondary sources (saravali.github.io, dirah.org, dineshcheramastro.com,
barbarapijan.com's BPHS ch27 translation) since a primary BPHS text wasn't
available in this environment. Formulas and their sourcing:

  - Ayana Bala: ayana = 30*(eps + signed_kranti)/eps, eps = true obliquity,
    signed_kranti = the planet's declination with a per-planet sign
    convention (Sun/Mars/Jupiter/Venus: north+; Moon/Saturn: south+;
    Mercury: |declination| always+). Sun's "doubling" (mentioned in several
    sources) is *not* a x2 on this formula -- it refers to the fact that
    the Sun's Chesta Bala is defined as a second copy of its Ayana Bala
    (confirmed via vijayalur.com/tag/ayana-bala), which is what happens
    naturally below since chesta_bala reuses the ayana_bala value.
  - Chesta Bala: the classical "Chesta Kendra" is Graha-Seeghrochcha minus
    the mean/true longitude average, which (for the 5 non-luminaries)
    encodes the planet's phase relative to its Shighrochcha -- for the 3
    superior planets that's effectively elongation from the Sun; for the 2
    inferior planets it's the complementary phase. We compute Chesta Kendra
    directly from that elongation (a verified modern equivalent -- retrograde
    stations occur exactly at Chesta Kendra=180, matching every source),
    rather than reproducing the classical multi-step Manda/Shighra mean-
    longitude arithmetic (which needs classical epicycle parameter tables
    not reproduced here). Reduction (>180 -> 360-x, then /3) per
    saravali.github.io/astrology/bala_cheshta.html.
  - Bhava Dig Bala: signs are grouped Nara/Jalachara/Chatushpada/Keeta
    (Sagittarius and Capricorn split by degree); a bhava's Dig Bala is its
    angular distance from the kendra where its own sign-group is weakest,
    /3 -- reconstructed from the documented special cases (e.g. "Nara gives
    the Ascendant 60, the 7th 0") per Medium/"Shadbala: 6 sources of
    strength" and vedastrology.blogspot.com.
  - Yuddha Bala (planetary war, previously omitted): only the 5 Tara Graha
    (Mars/Mercury/Jupiter/Venus/Saturn) can war, triggered when two are
    within 1 degree of longitude. Quantum = |difference in
    Sthana+Dig+Kaala-up-to-Hora Bala| / |difference in classical angular
    diameter|, added to the winner's total and subtracted from the loser's.
    Per dineshcheramastro.com/2022/12/10/yuddha-bala, the winner is simply
    the planet with the lower absolute longitude -- note this convention is
    ambiguous right at the 0/360 wrap and other texts use a latitude-based
    rule instead; flagged inline.

Naisargika Bala, Uchcha Bala, Kendradi Bala, Drishti grading and Panchadha
Maitri were already standard and unchanged. Cross-check against reference
software (Jagannatha Hora / Parashara's Light) before relying on this for
anything beyond prototyping -- these are still a solo reconstruction without
access to a primary Sanskrit source.
"""
import math
from datetime import timedelta

from . import ephem, varga
from .constants import (
    CLASSICAL_GRAHAS, RASHIS, RASHI_LORDS, MOOLATRIKONA, EXALTATION_LONGITUDE,
    NATURAL_FRIENDS, NATURAL_ENEMIES, RELATIONSHIP_POINTS, GENDER,
    DIG_BALA_FULL_HOUSE, WEEKDAY_LORDS, CHALDEAN_ORDER,
    TRIBHAGA_DAY_LORDS, TRIBHAGA_NIGHT_LORDS, NAISARGIKA_RANK, REQUIRED_BALA_RUPAS,
    NATURAL_BENEFICS, DRISHTI_BASE_PERCENT, SPECIAL_ASPECT_HOUSES, WEEKDAYS,
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


def _compound_relationship(dispositor: str, occupant: str, sign_indices: dict) -> str:
    natural = _natural_relationship(dispositor, occupant)
    temporal = _temporal_relationship(sign_indices[dispositor], sign_indices[occupant])
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
            rel = _compound_relationship(dispositor, planet, sign_indices)
            pts = RELATIONSHIP_POINTS[rel]
        total += pts
        breakdown.append({"varga": _VARGA_NAMES[i], "dispositor": dispositor, "relationship": rel, "points": pts})
    return total, breakdown  # max 315 (7 * 45)


def _ojha_yugma_bala(planet: str, d1_sign_index: int, d9_sign_index: int) -> float:
    if planet == "Mercury":
        return 30.0  # classically always full
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


def _drekkana_bala(planet: str, degree_in_sign: float) -> float:
    decan_gender = ["male", "female", "neuter"][int(degree_in_sign // 10)]
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
    if dt_utc < sunset0:
        return {"is_day": True, "sunrise": sunrise0, "sunset": sunset0}
    sunrise_next, _ = ephem.sunrise_sunset(day0_noon + timedelta(days=1), latitude, longitude)
    return {"is_day": False, "sunrise": sunrise0, "sunset": sunset0, "next_sunrise": sunrise_next}


def _nathonnata_bala(planet: str, dt_utc, bracket: dict) -> float:
    if planet == "Mercury":
        return 60.0
    if bracket["is_day"]:
        noon = bracket["sunrise"] + (bracket["sunset"] - bracket["sunrise"]) / 2
        half_len = (bracket["sunset"] - bracket["sunrise"]) / 2
        frac = abs((dt_utc - noon).total_seconds()) / half_len.total_seconds()
        diurnal = 60.0 * (1.0 - frac)
        nocturnal = 60.0 - diurnal
    else:
        midnight = bracket["sunset"] + (bracket["next_sunrise"] - bracket["sunset"]) / 2
        half_len = (bracket["next_sunrise"] - bracket["sunset"]) / 2
        frac = abs((dt_utc - midnight).total_seconds()) / half_len.total_seconds()
        nocturnal = 60.0 * (1.0 - frac)
        diurnal = 60.0 - nocturnal
    return diurnal if planet in ("Sun", "Jupiter", "Venus") else nocturnal


def _paksha_bala(planet: str, elongation: float) -> float:
    benefic_value = (180.0 - abs(elongation - 180.0)) / 3.0  # max 60 at full moon
    if planet == "Moon" or planet in NATURAL_BENEFICS:
        return benefic_value
    return 60.0 - benefic_value  # malefics: max 60 at new moon


def _tribhaga_bala(planet: str, dt_utc, bracket: dict) -> float:
    if bracket["is_day"]:
        third = (bracket["sunset"] - bracket["sunrise"]) / 3
        idx = min(2, int((dt_utc - bracket["sunrise"]) / third))
        lord = TRIBHAGA_DAY_LORDS[idx]
    else:
        third = (bracket["next_sunrise"] - bracket["sunset"]) / 3
        idx = min(2, int((dt_utc - bracket["sunset"]) / third))
        lord = TRIBHAGA_NIGHT_LORDS[idx]
    return 60.0 if planet == lord else 0.0


def _hora_lord(dt_utc, bracket: dict, dina_lord: str) -> str:
    start_idx = CHALDEAN_ORDER.index(dina_lord)
    if bracket["is_day"]:
        day_len = bracket["sunset"] - bracket["sunrise"]
        overall = min(11, int((dt_utc - bracket["sunrise"]) / (day_len / 12)))
    else:
        night_len = bracket["next_sunrise"] - bracket["sunset"]
        overall = 12 + min(11, int((dt_utc - bracket["sunset"]) / (night_len / 12)))
    return CHALDEAN_ORDER[(start_idx + overall) % 7]


def _last_crossing_before(value_fn, window_days: float, target_dt_utc, step_degrees: float, step_hours: float):
    """Most recent time before target_dt_utc at which value_fn (a 0-360 angle)
    crosses a multiple of step_degrees, found by scanning forward from
    (target_dt_utc - window_days) and bisecting each crossing found."""
    step = timedelta(hours=step_hours)
    t = target_dt_utc - timedelta(days=window_days)
    v_prev = value_fn(t) % 360.0
    last_cross = None

    while t < target_dt_utc:
        t_next = min(t + step, target_dt_utc)
        v_next = value_fn(t_next) % 360.0
        v_next_unwrapped = v_next + 360.0 if v_next < v_prev else v_next

        k = math.floor(v_prev / step_degrees) + 1
        while k * step_degrees <= v_next_unwrapped:
            boundary = k * step_degrees
            lo_t, lo_v = t, v_prev
            hi_t, hi_v = t_next, v_next_unwrapped
            for _ in range(40):
                mid_t = lo_t + (hi_t - lo_t) / 2
                mid_v = value_fn(mid_t) % 360.0
                if mid_v < lo_v - 1e-9:
                    mid_v += 360.0
                if mid_v < boundary:
                    lo_t, lo_v = mid_t, mid_v
                else:
                    hi_t, hi_v = mid_t, mid_v
            last_cross = lo_t + (hi_t - lo_t) / 2
            k += 1

        t, v_prev = t_next, v_next

    return last_cross


def _sun_sidereal_longitude(dt_utc) -> float:
    return ephem.sidereal_longitude("Sun", dt_utc)


def _varsha_masa_dina_hora_bala(dt_utc, tz_offset: float, bracket: dict):
    sunrise_local = bracket["sunrise"] + timedelta(hours=tz_offset)
    dina_lord = WEEKDAY_LORDS[WEEKDAYS[sunrise_local.weekday()]]
    hora_lord = _hora_lord(dt_utc, bracket, dina_lord)

    masa_crossing = _last_crossing_before(_sun_sidereal_longitude, 40, dt_utc, 30.0, 12)
    masa_lord = WEEKDAY_LORDS[WEEKDAYS[(masa_crossing + timedelta(hours=tz_offset)).weekday()]]

    varsha_crossing = _last_crossing_before(_sun_sidereal_longitude, 370, dt_utc, 360.0, 48)
    varsha_lord = WEEKDAY_LORDS[WEEKDAYS[(varsha_crossing + timedelta(hours=tz_offset)).weekday()]]

    lords = {"dina": dina_lord, "hora": hora_lord, "masa": masa_lord, "varsha": varsha_lord}
    return lords


def _ayana_bala(planet: str, dt_utc) -> float:
    """ayana = 30*(eps + signed_kranti)/eps, per-planet sign convention (see
    module docstring). Clamped to [0,60]: planets with orbital latitude
    (chiefly the Moon) can reach declinations slightly beyond the obliquity,
    which would otherwise push the raw formula a little past the usual
    0-60 virupa range."""
    eps = ephem.obliquity_of_ecliptic(dt_utc)
    dec = ephem.declination(planet, dt_utc)
    if planet == "Mercury":
        signed_kranti = abs(dec)  # always adds, regardless of N/S
    elif planet in ("Saturn", "Moon"):
        signed_kranti = -dec  # south declination adds, north subtracts
    else:  # Sun, Mars, Jupiter, Venus
        signed_kranti = dec  # north declination adds, south subtracts
    raw = 30.0 * (eps + signed_kranti) / eps
    return max(0.0, min(60.0, raw))


# --------------------------------------------------------------------------
# Chesta Bala (motional strength)
# --------------------------------------------------------------------------

def _chesta_bala(planet: str, ayana_bala_value: float, paksha_bala_value: float,
                  sun_longitude: float, planet_longitude: float) -> float:
    if planet == "Sun":
        return ayana_bala_value  # classical substitution (see module docstring)
    if planet == "Moon":
        return paksha_bala_value  # classical substitution
    elongation = (planet_longitude - sun_longitude) % 360.0
    if planet in ("Mars", "Jupiter", "Saturn"):
        # Superior planets retrograde at opposition (elongation=180).
        kendra = elongation
    else:
        # Mercury/Venus retrograde at inferior conjunction (elongation=0),
        # the opposite phase to the superior planets.
        kendra = (180.0 - elongation) % 360.0
    reduced = kendra if kendra <= 180.0 else 360.0 - kendra
    return reduced / 3.0  # max 60 at the retrograde-station phase


# --------------------------------------------------------------------------
# Drik Bala (aspectual strength)
# --------------------------------------------------------------------------

def _aspect_virupa(aspecting_planet: str, house_distance: int) -> float:
    pct = DRISHTI_BASE_PERCENT.get(house_distance, 0.0)
    pct = SPECIAL_ASPECT_HOUSES.get(aspecting_planet, {}).get(house_distance, pct)
    return 60.0 * pct / 100.0


def _is_benefic_aspect(aspecting_planet: str, planet_longitude: dict) -> bool:
    if aspecting_planet == "Moon":
        return ((planet_longitude["Moon"] - planet_longitude["Sun"]) % 360.0) < 180.0
    return aspecting_planet in NATURAL_BENEFICS


def _drik_bala(planet: str, planet_longitude: dict, sign_indices: dict) -> float:
    total = 0.0
    for other in CLASSICAL_GRAHAS:
        if other == planet:
            continue
        distance = _house_distance(sign_indices[other], sign_indices[planet])
        virupa = _aspect_virupa(other, distance)
        if virupa == 0.0:
            continue
        total += virupa if _is_benefic_aspect(other, planet_longitude) else -virupa
    return total


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def compute_shadbala(birth_dt_local, latitude: float, longitude: float, tz_offset: float) -> dict:
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

    vmdh_lords = _varsha_masa_dina_hora_bala(dt_utc, tz_offset, bracket)

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

        nathonnata = _nathonnata_bala(planet, dt_utc, bracket)
        paksha = _paksha_bala(planet, elongation)
        tribhaga = 0.0 if planet == "Jupiter" else _tribhaga_bala(planet, dt_utc, bracket)
        vmdh_bala = sum(15.0 for lord in vmdh_lords.values() if lord == planet)
        ayana = _ayana_bala(planet, dt_utc)
        kaala_total = nathonnata + paksha + tribhaga + vmdh_bala + ayana

        chesta = _chesta_bala(planet, ayana, paksha, planet_longitude["Sun"], lon)
        naisargika = 60.0 * NAISARGIKA_RANK[planet] / 7.0
        drik = _drik_bala(planet, planet_longitude, sign_indices)

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
        }

    _apply_yuddha_bala(results)
    return results


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


def _bhava_dig_bala(bhava_madhya: float, angle_by_house: dict) -> float:
    """Reconstructed from the documented special cases (e.g. a Nara-sign
    Ascendant gets 60, a Nara-sign 7th gets 0): each bhava's Dig Bala is its
    angular distance from the kendra where its own sign-group is weakest,
    divided by 3 -- the same mechanic as planetary Dig Bala."""
    weak_house = BHAVA_SIGN_GROUP_WEAK_HOUSE[_bhava_sign_group(bhava_madhya)]
    return _angular_sep(bhava_madhya, angle_by_house[weak_house]) / 3.0


def _bhava_drishti_bala(bhava_madhya: float, planet_longitude: dict, sign_indices: dict) -> float:
    bhava_sign = _sign_index(bhava_madhya)
    total = 0.0
    for other in CLASSICAL_GRAHAS:
        distance = _house_distance(sign_indices[other], bhava_sign)
        virupa = _aspect_virupa(other, distance)
        if virupa == 0.0:
            continue
        total += virupa if _is_benefic_aspect(other, planet_longitude) else -virupa
    return total


def compute_bhavabala(birth_dt_local, latitude: float, longitude: float, tz_offset: float,
                       shadbala_results: dict = None) -> list:
    from .chart import get_kundli

    if shadbala_results is None:
        shadbala_results = compute_shadbala(birth_dt_local, latitude, longitude, tz_offset)

    kundli = get_kundli(birth_dt_local, latitude, longitude, tz_offset)
    dt_utc = birth_dt_local - timedelta(hours=tz_offset)
    planet_longitude = {p["planet"]: p["longitude"] for p in kundli["planets"]}
    sign_indices = {pl: varga.d1_sign_index(lon) for pl, lon in planet_longitude.items() if pl in CLASSICAL_GRAHAS}

    asc_lon = ephem.sidereal_ascendant(dt_utc, latitude, longitude)
    mc_lon = ephem.sidereal_mc(dt_utc, longitude)
    madhyas = _sripati_bhava_madhyas(asc_lon, mc_lon)
    angle_by_house = {1: madhyas[0], 4: madhyas[3], 7: madhyas[6], 10: madhyas[9]}

    results = []
    for house_num in range(1, 13):
        madhya = madhyas[house_num - 1]
        sign_idx = _sign_index(madhya)
        lord = RASHI_LORDS[sign_idx]

        bhavadhipati = shadbala_results.get(lord, {}).get("total_virupa", 0.0)
        dig = _bhava_dig_bala(madhya, angle_by_house)
        drishti = _bhava_drishti_bala(madhya, planet_longitude, sign_indices)
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

    return results
