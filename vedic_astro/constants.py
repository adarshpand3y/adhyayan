"""Static lookup tables for Vedic (sidereal) astrology calculations."""

RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Ruling planet (dasha lord) of each of the 27 nakshatras, in order.
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
]

# Vimshottari dasha total years per planet, in the fixed dasha sequence.
DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}
VIMSHOTTARI_TOTAL_YEARS = sum(DASHA_YEARS.values())  # 120

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Amavasya",
]
PAKSHA_NAMES = ["Shukla", "Krishna"]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva",
    "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana",
    "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
    "Brahma", "Indra", "Vaidhriti",
]

# The 11 karana names. Bava..Vishti (index 0-6) repeat 8 times to cover
# tithis 2 through 57 (half-tithis); the 4 "fixed" karanas only occur once
# each, at the end of the lunar month (last 4 half-tithis, 57-60).
KARANA_MOVABLE = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]
KARANA_FIXED = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Choghadiya name -> nature (Shubh = auspicious, Ashubh = inauspicious, Neutral)
CHOGHADIYA_NATURE = {
    "Amrit": "Shubh", "Shubh": "Shubh", "Labh": "Shubh",
    "Chal": "Neutral",
    "Rog": "Ashubh", "Kaal": "Ashubh", "Udveg": "Ashubh",
}

# Day sequence of the 8 choghadiya slots, keyed by weekday, starting at sunrise.
# Standard fixed lookup table used by all panchang calculators.
CHOGHADIYA_DAY_SEQUENCE = {
    "Sunday": ["Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],
    "Monday": ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit"],
    "Tuesday": ["Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
    "Wednesday": ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh"],
    "Thursday": ["Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh"],
    "Friday": ["Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal"],
    "Saturday": ["Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal"],
}

# Night sequence always starts from the slot that follows the day's last slot.
CHOGHADIYA_NIGHT_SEQUENCE = {
    "Sunday": ["Shubh", "Amrit", "Chal", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],
    "Monday": ["Chal", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Chal"],
    "Tuesday": ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Chal", "Rog", "Kaal"],
    "Wednesday": ["Udveg", "Shubh", "Amrit", "Chal", "Rog", "Kaal", "Labh", "Udveg"],
    "Thursday": ["Amrit", "Chal", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],
    "Friday": ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Chal", "Rog"],
    "Saturday": ["Labh", "Udveg", "Shubh", "Amrit", "Chal", "Rog", "Kaal", "Labh"],
}

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Combustion (Asta) orbs in degrees of separation from the Sun (BPHS values).
# Sun, Rahu and Ketu are not subject to combustion.
COMBUSTION_ORBS = {"Moon": 12.0, "Mars": 17.0, "Mercury": 14.0, "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0}
# Tighter orbs that apply when the planet is retrograde.
COMBUSTION_ORBS_RETROGRADE = {"Mercury": 12.0, "Venus": 8.0}

# ---------------------------------------------------------------------------
# Shadbala / Bhavabala tables (classical, BPHS-based). Restricted to the 7
# classical grahas -- Rahu/Ketu have no shadbala in classical texts.
# ---------------------------------------------------------------------------

CLASSICAL_GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

RASHI_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
               "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

# Own (Swakshetra) signs, by rashi index (0=Mesha).
OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10],
}

# Moolatrikona: (rashi_index, degree_start, degree_end), degrees within the sign.
MOOLATRIKONA = {
    "Sun": (4, 0, 20), "Moon": (1, 4, 30), "Mars": (0, 0, 12),
    "Mercury": (5, 16, 20), "Jupiter": (8, 0, 10), "Venus": (6, 0, 15),
    "Saturn": (10, 0, 20),
}

# Exaltation point, absolute sidereal longitude in degrees (0-360).
EXALTATION_LONGITUDE = {
    "Sun": 10.0, "Moon": 33.0, "Mars": 298.0, "Mercury": 165.0,
    "Jupiter": 95.0, "Venus": 357.0, "Saturn": 200.0,
}

# Natural (Naisargika) friendship -- deliberately asymmetric, per BPHS.
NATURAL_FRIENDS = {
    "Sun": ["Moon", "Mars", "Jupiter"],
    "Moon": ["Sun", "Mercury"],
    "Mars": ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus": ["Mercury", "Saturn"],
    "Saturn": ["Mercury", "Venus"],
}
NATURAL_ENEMIES = {
    "Sun": ["Venus", "Saturn"],
    "Moon": [],
    "Mars": ["Mercury"],
    "Mercury": ["Moon"],
    "Jupiter": ["Mercury", "Venus"],
    "Venus": ["Sun", "Moon"],
    "Saturn": ["Sun", "Moon", "Mars"],
}

RELATIONSHIP_POINTS = {
    "moolatrikona": 45.0, "own": 30.0, "adhimitra": 22.5,
    "mitra": 15.0, "sama": 7.5, "shatru": 3.75, "adhishatru": 1.875,
}

GENDER = {
    "Sun": "male", "Moon": "female", "Mars": "male", "Mercury": "neuter",
    "Jupiter": "male", "Venus": "female", "Saturn": "neuter",
}

# House (from ascendant) in which each planet is at Dig Bala's full (60) strength.
DIG_BALA_FULL_HOUSE = {"Sun": 10, "Mars": 10, "Jupiter": 1, "Mercury": 1, "Moon": 4, "Venus": 4, "Saturn": 7}

# Classical mean daily motions (degrees/day) used to normalise Chesta Bala.
MEAN_DAILY_MOTION = {
    "Sun": 0.9856, "Moon": 13.176, "Mars": 0.524, "Mercury": 1.383,
    "Jupiter": 0.0831, "Venus": 1.602, "Saturn": 0.0334,
}

WEEKDAY_LORDS = {
    "Sunday": "Sun", "Monday": "Moon", "Tuesday": "Mars", "Wednesday": "Mercury",
    "Thursday": "Jupiter", "Friday": "Venus", "Saturday": "Saturn",
}
# Vara (weekday) lords indexed 0=Sunday .. 6=Saturday, the order the classical
# "count the remainder from the Sun" rules use.
VARA_LORDS_FROM_SUNDAY = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Abda (year) / Masa (month) / Vara (weekday) / Hora (planetary hour) Bala: the
# four lords are NOT worth the same -- BPHS grades them 15/30/45/60 virupas.
ABDA_MASA_VARA_HORA_VIRUPAS = {"varsha": 15.0, "masa": 30.0, "dina": 45.0, "hora": 60.0}

# Parama Kranti: the classical maximum declination, 24 degrees. Ayana Bala uses
# it both to derive the kranti from the sayana longitude and as the divisor, so
# that a planet on the celestial equator scores 30 and one at maximum northern
# declination 60. Using one constant for both roles is what makes the scale come
# out right -- the two must agree.
AYANA_PARAMA_KRANTI = 24.0

# Julian Day of the Kali Yuga epoch (17/18 Feb 3102 BCE), the zero point the
# classical Ahargana (elapsed-day count) is measured from. The Abda and Masa
# lords are located by stepping back through the schematic 360-day year and
# 30-day month it counts off.
KALI_EPOCH_JD = 588465.5
AHARGANA_YEAR_DAYS = 360
AHARGANA_MONTH_DAYS = 30

# Per-component minimum strengths in virupas (Sthana, Dig, Kaala, Chesta,
# Ayana), from vijayalur.com/2011/06/15/shadbala-an-overview. These sit
# alongside REQUIRED_BALA_RUPAS, which is the threshold on the *total*.
# NOTE the Chesta figures exceed the 60-virupa maximum a Chesta Bala can reach,
# so that column looks like an error in the source; it is recorded as published
# but is not used to judge sufficiency anywhere.
COMPONENT_MINIMUM_VIRUPAS = {
    "Sun": {"sthana": 165, "dig": 35, "kaala": 50, "chesta": 112, "ayana": 30},
    "Mercury": {"sthana": 165, "dig": 35, "kaala": 50, "chesta": 112, "ayana": 30},
    "Jupiter": {"sthana": 165, "dig": 35, "kaala": 50, "chesta": 112, "ayana": 30},
    "Moon": {"sthana": 133, "dig": 50, "kaala": 30, "chesta": 100, "ayana": 40},
    "Venus": {"sthana": 133, "dig": 50, "kaala": 30, "chesta": 100, "ayana": 40},
    "Mars": {"sthana": 96, "dig": 30, "kaala": 40, "chesta": 67, "ayana": 20},
    "Saturn": {"sthana": 96, "dig": 30, "kaala": 40, "chesta": 67, "ayana": 20},
}
# Descending (slowest-first) Chaldean order used for planetary-hour (Hora) lords.
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Tribhaga (day/night each split into 3): lord of the 1st/2nd/3rd part.
TRIBHAGA_DAY_LORDS = ["Mercury", "Sun", "Saturn"]
TRIBHAGA_NIGHT_LORDS = ["Moon", "Venus", "Mars"]

# Naisargika (natural/inherent) Bala rank, 1 (weakest) .. 7 (strongest); actual
# virupas = 60 * rank / 7.
NAISARGIKA_RANK = {"Saturn": 1, "Mars": 2, "Mercury": 3, "Jupiter": 4, "Venus": 5, "Moon": 6, "Sun": 7}

# Minimum required total Shadbala, in Rupas (1 Rupa = 60 virupas): 300, 360,
# 300, 420, 390, 330 and 300 virupas. A planet is judged not by clearing this
# outright but by its Ratio (attained / required), which is what the classical
# Relative Rank orders the grahas on -- so a weak-looking Sun can still outrank
# a numerically stronger Mercury.
REQUIRED_BALA_RUPAS = {"Sun": 5.0, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
                        "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0}

# Bhava Dig Bala: sign-group -> the house (1=Asc,4=IC,7=Desc,10=MC) each group is
# *weakest* at (0 virupas there, 60 virupas at the opposite kendra). Sagittarius
# and Capricorn are split by degree between two groups (classical convention).
BHAVA_SIGN_GROUP_WEAK_HOUSE = {"nara": 7, "jalachara": 10, "chatuspada": 4, "keeta": 1}

# Yuddha Bala (planetary war): only the 5 non-luminous "Tara Graha" participate.
YUDDHA_ELIGIBLE_PLANETS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
YUDDHA_ORB_DEGREES = 1.0
# Classical apparent angular diameters, in arcseconds (per dineshcheramastro.com/2022/12/10/yuddha-bala).
YUDDHA_DIAMETER_ARCSEC = {"Mars": 9.4, "Mercury": 6.6, "Jupiter": 190.4, "Venus": 16.6, "Saturn": 158.0}

NATURAL_BENEFICS = ["Jupiter", "Venus", "Mercury"]
NATURAL_MALEFICS = ["Sun", "Mars", "Saturn"]

# Sphuta Drishti (BPHS ch. 26): aspect strength in virupas as a *continuous*
# function of the ecliptic distance from the aspecting body to the aspected
# point, given as (upper_bound_degrees, slope, intercept) so that
#   drishti = slope * distance + intercept   for distance < upper_bound.
# It peaks at 60 on the 7th (180 deg) and passes through the classical graded
# values -- 15 at the 3rd (60), 45 at the 4th (90), 30 at the 5th (120),
# 45 at the 8th (210), 30 at the 9th (240), 15 at the 10th (270).
# Distances below 30 and at/above 300 give nothing.
# Special-aspect additions (Raman): on top of the value above, Mars adds 15 on
# the 4th and 8th, Jupiter 30 on the 5th and 9th, Saturn 45 on the 3rd and
# 10th, keyed by the same from-aspecting-body distance in degrees.
SPECIAL_ASPECT_BONUS = {
    "Mars": (((90.0, 120.0), 15.0), ((210.0, 240.0), 15.0)),
    "Jupiter": (((120.0, 150.0), 30.0), ((240.0, 270.0), 30.0)),
    "Saturn": (((60.0, 90.0), 45.0), ((270.0, 300.0), 45.0)),
}

# In Bhava Drishti Bala every graha's drishti is quartered except these two,
# whose drishti on a bhava counts in full.
FULL_BHAVA_DRISHTI_GRAHAS = ("Jupiter", "Mercury")

SPHUTA_DRISHTI_SEGMENTS = [
    (30.0, 0.0, 0.0),        # 0-30    : 0
    (60.0, 0.5, -15.0),      # 30-60   : 0  -> 15
    (90.0, 1.0, -45.0),      # 60-90   : 15 -> 45
    (120.0, -0.5, 90.0),     # 90-120  : 45 -> 30
    (150.0, -1.0, 150.0),    # 120-150 : 30 -> 0
    (180.0, 2.0, -300.0),    # 150-180 : 0  -> 60
    (300.0, -0.5, 150.0),    # 180-300 : 60 -> 0
    (360.0, 0.0, 0.0),       # 300-360 : 0
]
