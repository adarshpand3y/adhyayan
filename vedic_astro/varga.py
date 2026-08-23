"""
Divisional chart (varga) sign calculations, used only to score Saptavargaja
Bala (part of Shadbala's Sthana Bala). Each function takes an absolute
sidereal longitude (0-360) and returns the *dispositor* (ruling planet) of
that varga sign -- not the sign itself -- since that's all Saptavargaja Bala
needs, and it keeps D30 (which classically assigns a lord directly rather
than a rashi) consistent with the others.

Standard Parashari division rules (D2 Hora, D3 Drekkana, D7 Saptamsa,
D9 Navamsa, D12 Dwadasamsa equal-division; D30 Trimsamsa unequal).
"""
from .constants import RASHI_LORDS

_D9_START_OFFSET = {0: 0, 1: 8, 2: 4}  # movable/fixed/dual (rashi_index % 3)


def _rashi_and_degree(longitude: float):
    rashi_index = int(longitude // 30)
    degree = longitude - rashi_index * 30
    return rashi_index, degree


def d1_sign_index(longitude: float) -> int:
    return _rashi_and_degree(longitude)[0]


def d9_sign_index(longitude: float) -> int:
    rashi_index, degree = _rashi_and_degree(longitude)
    part = int(degree // (30.0 / 9))
    start = (rashi_index + _D9_START_OFFSET[rashi_index % 3]) % 12
    return (start + part) % 12


def d1_dispositor(longitude: float) -> str:
    rashi_index, _ = _rashi_and_degree(longitude)
    return RASHI_LORDS[rashi_index]


def d2_dispositor(longitude: float) -> str:
    rashi_index, degree = _rashi_and_degree(longitude)
    is_odd_sign = rashi_index % 2 == 0
    first_half = degree < 15.0
    sun_hora = first_half if is_odd_sign else not first_half
    return "Sun" if sun_hora else "Moon"


def d3_dispositor(longitude: float) -> str:
    rashi_index, degree = _rashi_and_degree(longitude)
    decan = int(degree // 10)
    sign_index = (rashi_index + decan * 4) % 12
    return RASHI_LORDS[sign_index]


def d7_dispositor(longitude: float) -> str:
    rashi_index, degree = _rashi_and_degree(longitude)
    part = int(degree // (30.0 / 7))
    is_odd_sign = rashi_index % 2 == 0
    start = rashi_index if is_odd_sign else (rashi_index + 6) % 12
    sign_index = (start + part) % 12
    return RASHI_LORDS[sign_index]


def d9_dispositor(longitude: float) -> str:
    return RASHI_LORDS[d9_sign_index(longitude)]


def d12_dispositor(longitude: float) -> str:
    rashi_index, degree = _rashi_and_degree(longitude)
    part = int(degree // 2.5)
    sign_index = (rashi_index + part) % 12
    return RASHI_LORDS[sign_index]


# Trimsamsa (D30) unequal divisions -- each division is assigned a lord
# directly rather than a rashi (classical simplification kept here too).
_D30_ODD = [("Mars", 0, 5), ("Saturn", 5, 10), ("Jupiter", 10, 18), ("Mercury", 18, 25), ("Venus", 25, 30)]
_D30_EVEN = [("Venus", 0, 5), ("Mercury", 5, 12), ("Jupiter", 12, 20), ("Saturn", 20, 25), ("Mars", 25, 30)]


def d30_dispositor(longitude: float) -> str:
    rashi_index, degree = _rashi_and_degree(longitude)
    table = _D30_ODD if rashi_index % 2 == 0 else _D30_EVEN
    for lord, start, end in table:
        if start <= degree < end:
            return lord
    return table[-1][0]


# The 7 vargas used for Saptavargaja Bala, in order.
SAPTAVARGA_DISPOSITORS = [
    d1_dispositor, d2_dispositor, d3_dispositor, d7_dispositor,
    d9_dispositor, d12_dispositor, d30_dispositor,
]
