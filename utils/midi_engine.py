"""
MIDI generation and manipulation engine for Simple Balance Music.
Uses music21 for notation, pretty_midi for MIDI creation, Azure OpenAI for AI generation.
"""

import os
import tempfile

try:
    import pretty_midi
    HAS_PRETTY_MIDI = True
except ImportError:
    pretty_midi = None
    HAS_PRETTY_MIDI = False

try:
    from music21 import converter, midi as m21_midi, stream, note, chord, meter, key as m21_key, tempo
    HAS_MUSIC21 = True
except ImportError:
    HAS_MUSIC21 = False

try:
    import mido
    HAS_MIDO = True
except ImportError:
    mido = None
    HAS_MIDO = False

try:
    import streamlit as st
except ImportError:
    st = None

try:
    from openai import AzureOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# --- Note/Scale Utilities ---

NOTE_MAP = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}

SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
}

CHORD_NUMERALS = {
    "I": 0, "i": 0, "II": 1, "ii": 1, "III": 2, "iii": 2,
    "IV": 3, "iv": 3, "V": 4, "v": 4, "VI": 5, "vi": 5,
    "VII": 6, "vii": 6,
}


def _get_scale_notes(root, scale="minor", octave=4):
    """Get MIDI note numbers for a scale."""
    root_midi = NOTE_MAP.get(root, 0) + (octave * 12)
    intervals = SCALE_INTERVALS.get(scale, SCALE_INTERVALS["minor"])
    return [root_midi + i for i in intervals]


def _build_chord(root_midi, quality="minor"):
    """Build a chord from root MIDI note."""
    if quality == "major":
        return [root_midi, root_midi + 4, root_midi + 7]
    elif quality == "minor":
        return [root_midi, root_midi + 3, root_midi + 7]
    elif quality == "diminished":
        return [root_midi, root_midi + 3, root_midi + 6]
    elif quality == "sus2":
        return [root_midi, root_midi + 2, root_midi + 7]
    elif quality == "sus4":
        return [root_midi, root_midi + 5, root_midi + 7]
    elif quality == "7":
        return [root_midi, root_midi + 4, root_midi + 7, root_midi + 10]
    elif quality == "min7":
        return [root_midi, root_midi + 3, root_midi + 7, root_midi + 10]
    else:
        return [root_midi, root_midi + 3, root_midi + 7]


def generate_midi_from_text(prompt, model="gpt-4o", bpm=128, output_path=None):
    """Use Azure OpenAI to generate ABC notation, convert to MIDI via music21."""
    if not HAS_OPENAI or not HAS_MUSIC21:
        return _mock_midi_generation(prompt, "Missing openai or music21 dependency")
    endpoint = ""
    api_key = ""
    if st is not None:
        endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT", "")
        api_key = st.secrets.get("AZURE_OPENAI_KEY", "")
    if not endpoint or not api_key:
        return _mock_midi_generation(prompt, "Azure OpenAI not configured")
    try:
        client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version="2024-12-01-preview")
        system_prompt = (
            "You are a music composition AI. Generate ABC notation for the requested music. "
            "Output ONLY valid ABC notation, no explanations. Use appropriate time signature and key. "
            "Keep it between 8-32 bars. For electronic/dance music, emphasize rhythmic patterns. "
            "Include tempo marking (Q:) matching the requested BPM. "
            "Use standard ABC notation headers (X:, T:, M:, L:, K:, Q:)."
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate ABC notation at {bpm} BPM: {prompt}"},
            ],
            temperature=0.7,
        )
        abc_text = response.choices[0].message.content.strip()
        if "```" in abc_text:
            lines = abc_text.split("
")
            cleaned = [l for l in lines if not l.strip().startswith("```")]
            abc_text = "
".join(cleaned)
        score = converter.parse(abc_text, format="abc")
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), "sb_generated.mid")
        midi_file = m21_midi.translate.streamToMidiFile(score)
        midi_file.open(output_path, "wb")
        midi_file.write()
        midi_file.close()
        return {"midi_path": output_path, "abc_notation": abc_text, "status": "complete"}
    except Exception as e:
        return _mock_midi_generation(prompt, str(e))


def create_chord_progression(key_root="A", scale="minor", progression=None, bpm=128, bars_per_chord=2, velocity=80, octave=3, output_path=None):
    """Generate a MIDI chord progression."""
    if not HAS_PRETTY_MIDI:
        return _mock_midi_path("chord_progression")
    if progression is None:
        progression = ["i", "VI", "III", "VII"]
    pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    instrument = pretty_midi.Instrument(program=0, name="Chords")
    beats_per_bar = 4
    seconds_per_beat = 60.0 / bpm
    bar_duration = beats_per_bar * seconds_per_beat
    scale_notes = _get_scale_notes(key_root, scale, octave)
    current_time = 0.0
    for numeral in progression:
        degree = CHORD_NUMERALS.get(numeral.replace("7", "").replace("dim", ""), 0)
        if numeral[0].isupper():
            quality = "major"
        else:
            quality = "minor"
        if "dim" in numeral:
            quality = "diminished"
        if "7" in numeral and numeral[0].isupper():
            quality = "7"
        elif "7" in numeral:
            quality = "min7"
        root_note = scale_notes[degree % len(scale_notes)]
        chord_notes = _build_chord(root_note, quality)
        duration = bar_duration * bars_per_chord
        for midi_note in chord_notes:
            note = pretty_midi.Note(velocity=velocity, pitch=midi_note, start=current_time, end=current_time + duration)
            instrument.notes.append(note)
        current_time += duration
    pm.instruments.append(instrument)
    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), "sb_chords.mid")
    pm.write(output_path)
    return output_path


def create_bassline(key_root="A", pattern=None, bpm=128, octave=2, velocity=100, output_path=None):
    """Generate a MIDI bassline pattern."""
    if not HAS_PRETTY_MIDI:
        return _mock_midi_path("bassline")
    if pattern is None:
        pattern = [
            {"note": 0, "duration": 0.5, "rest": False},
            {"note": 0, "duration": 0.5, "rest": True},
            {"note": 0, "duration": 0.5, "rest": False},
            {"note": 0, "duration": 0.5, "rest": False},
            {"note": 0, "duration": 0.5, "rest": False},
            {"note": 0, "duration": 0.5, "rest": True},
            {"note": 2, "duration": 0.5, "rest": False},
            {"note": 0, "duration": 0.5, "rest": False},
        ]
    pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    instrument = pretty_midi.Instrument(program=38, name="Bass")
    seconds_per_beat = 60.0 / bpm
    root_midi = NOTE_MAP.get(key_root, 0) + (octave * 12)
    scale = SCALE_INTERVALS["minor"]
    current_time = 0.0
    for _ in range(8):
        for step in pattern:
            dur = step["duration"] * seconds_per_beat
            if not step.get("rest", False):
                degree = step["note"] % len(scale)
                midi_note = root_midi + scale[degree]
                note = pretty_midi.Note(velocity=velocity, pitch=midi_note, start=current_time, end=current_time + dur * 0.9)
                instrument.notes.append(note)
            current_time += dur
    pm.instruments.append(instrument)
    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), "sb_bass.mid")
    pm.write(output_path)
    return output_path


def _get_drum_patterns():
    """Return drum pattern definitions for different styles."""
    return {
        "progressive_house": {
            "kick": [0, 4, 8, 12],
            "clap": [4, 12],
            "closed_hat": [2, 6, 10, 14],
            "open_hat": [14],
        },
        "techno": {
            "kick": [0, 3, 4, 8, 11, 12],
            "clap": [4, 12],
            "closed_hat": [0, 2, 4, 6, 8, 10, 12, 14],
            "open_hat": [6, 14],
        },
        "deep_house": {
            "kick": [0, 4, 8, 12],
            "snare": [4, 13],
            "closed_hat": [2, 5, 6, 10, 13, 14],
            "open_hat": [6],
        },
        "breakbeat": {
            "kick": [0, 3, 6, 10],
            "snare": [4, 7, 12, 15],
            "closed_hat": list(range(16)),
            "open_hat": [2, 10],
        },
        "testpilot": {
            "kick": [0, 4, 8, 12],
            "clap": [4, 12],
            "closed_hat": [1, 3, 5, 7, 9, 11, 13, 15],
            "open_hat": [7, 15],
        },
    }


def create_drum_pattern(style="progressive_house", bpm=128, bars=4, velocity_kick=110, velocity_snare=90, velocity_hat=70, velocity_open_hat=60, output_path=None):
    """Generate a MIDI drum pattern."""
    if not HAS_PRETTY_MIDI:
        return _mock_midi_path("drums")
    pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    instrument = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")
    seconds_per_beat = 60.0 / bpm
    sixteenth = seconds_per_beat / 4.0
    KICK, SNARE, CLOSED_HAT, OPEN_HAT, CLAP = 36, 38, 42, 46, 39
    patterns = _get_drum_patterns()
    pat = patterns.get(style, patterns["progressive_house"])
    for bar in range(bars):
        bar_offset = bar * 16 * sixteenth
        for step in range(16):
            step_time = bar_offset + step * sixteenth
            for drum_type, hits in pat.items():
                if step in hits:
                    if drum_type == "kick":
                        pitch, vel = KICK, velocity_kick
                    elif drum_type == "snare":
                        pitch, vel = SNARE, velocity_snare
                    elif drum_type == "clap":
                        pitch, vel = CLAP, velocity_snare
                    elif drum_type == "closed_hat":
                        pitch, vel = CLOSED_HAT, velocity_hat
                    elif drum_type == "open_hat":
                        pitch, vel = OPEN_HAT, velocity_open_hat
                    else:
                        continue
                    note = pretty_midi.Note(velocity=vel, pitch=pitch, start=step_time, end=step_time + sixteenth * 0.8)
                    instrument.notes.append(note)
    pm.instruments.append(instrument)
    if output_path is None:
        output_path = os.path.join(tempfile.gettempdir(), f"sb_drums_{style}.mid")
    pm.write(output_path)
    return output_path


def midi_to_audio(midi_path, output_path=None, soundfont=None):
    """Convert MIDI to audio via FluidSynth if available."""
    if output_path is None:
        base = os.path.splitext(midi_path)[0]
        output_path = f"{base}.wav"
    if HAS_PRETTY_MIDI:
        try:
            pm = pretty_midi.PrettyMIDI(midi_path)
            audio = pm.fluidsynth(fs=44100, sf2_path=soundfont)
            import soundfile as sf_lib
            sf_lib.write(output_path, audio, 44100)
            return output_path
        except Exception:
            pass
    return f"MIDI-to-audio requires FluidSynth. MIDI saved to: {midi_path}"


# --- Mock/Fallback ---

def _mock_midi_generation(prompt, reason=""):
    """Return mock data when MIDI generation is unavailable."""
    return {"midi_path": None, "abc_notation": None, "status": "mock", "message": f"MIDI generation unavailable. {reason}".strip()}


def _mock_midi_path(name):
    """Return mock path when pretty_midi is not available."""
    return f"[MOCK] pretty_midi not installed. Cannot generate {name} MIDI."
