"""
mau5trap production presets for Simple Balance Music.
Curated settings for progressive house, techno, and label-ready masters.
"""

# --- BPM Presets ---
BPM_PRESETS = {
    "progressive_house": {"min": 126, "max": 128, "default": 128, "label": "Progressive House"},
    "testpilot": {"min": 130, "max": 135, "default": 132, "label": "Techno / TESTPILOT"},
    "deep_house": {"min": 120, "max": 124, "default": 122, "label": "Deep House"},
    "melodic_techno": {"min": 122, "max": 128, "default": 125, "label": "Melodic Techno"},
    "electro_house": {"min": 126, "max": 130, "default": 128, "label": "Electro House"},
}

# --- Key Presets ---
KEY_PRESETS = {
    "mau5trap_common": {
        "keys": ["Am", "Dm", "Em", "Cm"],
        "label": "Common mau5trap Keys",
        "description": "Minor keys dominate the mau5trap catalog. Dark, moody, driving.",
    },
    "deadmau5_favorites": {
        "keys": ["Am", "F#m", "Dm", "Gm"],
        "label": "deadmau5 Signature Keys",
        "description": "Keys frequently used across deadmau5 releases.",
    },
    "melodic_range": {
        "keys": ["Am", "Bm", "Cm", "Dm", "Em", "Fm", "Gm"],
        "label": "All Minor Keys",
        "description": "Full range of natural minor keys for melodic work.",
    },
    "relative_majors": {
        "keys": ["C", "D", "Eb", "F", "G", "Ab", "Bb"],
        "label": "Relative Majors",
        "description": "Major counterparts for brighter passages and breakdowns.",
    },
}

# --- Mastering Presets ---
MASTERING_PRESETS = {
    "mau5trap": {
        "label": "mau5trap Club Master",
        "target_lufs": -6,
        "eq": {"high_pass": 30, "low_shelf_freq": 80, "low_shelf_gain": 1.5, "high_shelf_freq": 12000, "high_shelf_gain": 1.0},
        "compression": {"threshold": -16, "ratio": 3.0, "attack_ms": 10, "release_ms": 80},
        "makeup_gain_db": 2.0,
        "limiter": {"threshold": -0.5, "release_ms": 80},
        "description": "Club-optimized. Punchy lows, clear highs, loud and clean.",
    },
    "streaming": {
        "label": "Streaming Master (-14 LUFS)",
        "target_lufs": -14,
        "eq": {"high_pass": 25, "low_shelf_freq": 100, "low_shelf_gain": 0.5, "high_shelf_freq": 14000, "high_shelf_gain": 0.5},
        "compression": {"threshold": -20, "ratio": 2.5, "attack_ms": 15, "release_ms": 120},
        "makeup_gain_db": 1.0,
        "limiter": {"threshold": -1.0, "release_ms": 100},
        "description": "Optimized for Spotify/Apple Music normalization at -14 LUFS.",
    },
    "demo": {
        "label": "Demo Master (-10 LUFS)",
        "target_lufs": -10,
        "eq": {"high_pass": 28, "low_shelf_freq": 90, "low_shelf_gain": 1.0, "high_shelf_freq": 13000, "high_shelf_gain": 0.8},
        "compression": {"threshold": -18, "ratio": 2.8, "attack_ms": 12, "release_ms": 100},
        "makeup_gain_db": 1.5,
        "limiter": {"threshold": -0.8, "release_ms": 90},
        "description": "Balanced demo master. Loud enough to impress, clean enough to judge.",
    },
}

# --- Sidechain Presets ---
SIDECHAIN_PRESETS = {
    "pump": {"label": "Heavy Pump", "threshold": -30, "ratio": 8.0, "attack_ms": 1.0, "release_ms": 150, "description": "Classic mau5trap sidechain pump. Heavy ducking on kick hits."},
    "subtle": {"label": "Subtle Groove", "threshold": -20, "ratio": 3.0, "attack_ms": 5.0, "release_ms": 80, "description": "Light sidechain for groove without obvious pumping."},
    "off": {"label": "No Sidechain", "threshold": 0, "ratio": 1.0, "attack_ms": 10, "release_ms": 50, "description": "Bypass. No sidechain compression applied."},
    "testpilot": {"label": "TESTPILOT Slam", "threshold": -35, "ratio": 10.0, "attack_ms": 0.5, "release_ms": 200, "description": "Aggressive techno sidechain. Deep, crushing pump."},
}

# --- EQ Profiles ---
EQ_PROFILES = {
    "dark_atmospheric": {"label": "Dark Atmospheric", "high_pass": 35, "low_shelf_freq": 100, "low_shelf_gain": 2.0, "high_shelf_freq": 8000, "high_shelf_gain": -2.0, "description": "Rolled-off highs, boosted lows. Moody, atmospheric feel."},
    "bright_lead": {"label": "Bright Lead", "high_pass": 80, "low_shelf_freq": 200, "low_shelf_gain": -3.0, "high_shelf_freq": 10000, "high_shelf_gain": 3.0, "description": "Cut lows, boost presence. For leads that cut through the mix."},
    "sub_bass": {"label": "Sub Bass", "high_pass": 20, "low_shelf_freq": 60, "low_shelf_gain": 4.0, "high_shelf_freq": 5000, "high_shelf_gain": -6.0, "description": "Maximum sub presence. Kill the highs, feel the weight."},
    "vocal_presence": {"label": "Vocal Presence", "high_pass": 100, "low_shelf_freq": 250, "low_shelf_gain": -2.0, "high_shelf_freq": 12000, "high_shelf_gain": 2.0, "description": "Clear vocal space. Reduce mud, add air."},
    "flat_reference": {"label": "Flat Reference", "high_pass": 20, "low_shelf_freq": 100, "low_shelf_gain": 0.0, "high_shelf_freq": 16000, "high_shelf_gain": 0.0, "description": "Flat response. For A/B reference comparison."},
}

# --- Chord Progressions ---
CHORD_PROGRESSIONS = {
    "mau5trap_classic": {"label": "mau5trap Classic", "progression": ["i", "VI", "III", "VII"], "description": "The quintessential progressive house progression."},
    "strobe": {"label": "Strobe Style", "progression": ["i", "iv", "VI", "V"], "description": "Emotional, building progression inspired by Strobe."},
    "dark_drive": {"label": "Dark Drive", "progression": ["i", "iv", "v", "i"], "description": "All minor. Dark, relentless, driving."},
    "euphoric_lift": {"label": "Euphoric Lift", "progression": ["i", "III", "VII", "VI"], "description": "Lifting progression for main room breakdowns."},
    "testpilot_minimal": {"label": "TESTPILOT Minimal", "progression": ["i", "i", "iv", "i"], "description": "Minimal movement. Hypnotic. Let the rhythm do the work."},
}

# --- Genre Templates ---
GENRE_TEMPLATES = {
    "progressive_house": {"bpm": 128, "key": "Am", "mastering": "mau5trap", "sidechain": "pump", "eq": "dark_atmospheric", "progression": "mau5trap_classic", "drum_style": "progressive_house", "description": "Full progressive house production template."},
    "testpilot_techno": {"bpm": 132, "key": "Dm", "mastering": "mau5trap", "sidechain": "testpilot", "eq": "dark_atmospheric", "progression": "testpilot_minimal", "drum_style": "testpilot", "description": "TESTPILOT-style dark techno template."},
    "melodic_deep": {"bpm": 122, "key": "Em", "mastering": "streaming", "sidechain": "subtle", "eq": "vocal_presence", "progression": "strobe", "drum_style": "deep_house", "description": "Deep, melodic production. Emotional and atmospheric."},
}


def get_preset_summary():
    """Return a summary of all available presets for UI display."""
    return {
        "bpm_presets": {k: v["label"] for k, v in BPM_PRESETS.items()},
        "key_presets": {k: v["label"] for k, v in KEY_PRESETS.items()},
        "mastering_presets": {k: v["label"] for k, v in MASTERING_PRESETS.items()},
        "sidechain_presets": {k: v["label"] for k, v in SIDECHAIN_PRESETS.items()},
        "eq_profiles": {k: v["label"] for k, v in EQ_PROFILES.items()},
        "chord_progressions": {k: v["label"] for k, v in CHORD_PROGRESSIONS.items()},
        "genre_templates": {k: v["description"] for k, v in GENRE_TEMPLATES.items()},
    }
