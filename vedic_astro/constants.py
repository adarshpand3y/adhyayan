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
# Descending (slowest-first) Chaldean order used for planetary-hour (Hora) lords.
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Tribhaga (day/night each split into 3): lord of the 1st/2nd/3rd part.
TRIBHAGA_DAY_LORDS = ["Mercury", "Sun", "Saturn"]
TRIBHAGA_NIGHT_LORDS = ["Moon", "Venus", "Mars"]

# Naisargika (natural/inherent) Bala rank, 1 (weakest) .. 7 (strongest); actual
# virupas = 60 * rank / 7.
NAISARGIKA_RANK = {"Saturn": 1, "Mars": 2, "Mercury": 3, "Jupiter": 4, "Venus": 5, "Moon": 6, "Sun": 7}

# Commonly-cited minimum required total Shadbala, in Rupas (1 Rupa = 60 virupas).
# Sourced from BPHS (cross-checked against saravali.github.io/astrology/bala_summary.html).
REQUIRED_BALA_RUPAS = {"Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
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

# Graded aspect (Drishti) strength, as a percentage of full (60 virupa) strength,
# by house-distance (1-12) counted from the aspecting planet. Houses not listed
# get 0%. Every planet gets 100% on the 7th; Mars/Jupiter/Saturn get upgraded
# to 100% on their special houses (see SPECIAL_ASPECT_HOUSES).
DRISHTI_BASE_PERCENT = {3: 25.0, 4: 75.0, 5: 50.0, 7: 100.0, 8: 75.0, 9: 50.0, 10: 25.0}
SPECIAL_ASPECT_HOUSES = {
    "Mars": {4: 100.0, 8: 100.0},
    "Jupiter": {5: 100.0, 9: 100.0},
    "Saturn": {3: 100.0, 10: 100.0},
}
