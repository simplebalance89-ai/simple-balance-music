# Simple Balance Music - Product Design

**Document Version:** 1.0
**Date:** February 24, 2026
**Author:** Peter Wilson / Sinton.ia
**Status:** Active Development

---

## What It Is

Simple Balance Music is an AI-powered music production, DJing, and discovery platform built for electronic music creators. It is a full-stack web application deployed on Streamlit Cloud that combines real AI services (Azure OpenAI, Replicate, Spotify Pedalboard) with deep domain knowledge of electronic music production workflows.

The platform is named after Peter and Jimmy Wilson's DJ project **J.A.W.** (Jimmy And Wilson). Music is how the brothers communicate. This is not a toy or a demo. It is a working production suite built on real APIs, with real audio processing, real MIDI generation, and real AI-driven DJ intelligence.

**Core identity:** Simple Balance is the intersection of DJ culture, music production, and AI tooling. Peter was a DJ and promoter for half his life. He ran clubs, sold tickets, managed guest lists, and built floors. This platform encodes that knowledge into software.

**Live URL:** Deployed on Streamlit Cloud (simplebalance89-ai/simple-balance-music)
**Repo:** `simplebalance89-ai/simple-balance-music` on GitHub
**Local Path:** `C:\Claude\Work\simple-balance-music\`

---

## What Was Built (v2.0)

### Architecture Overview

The application is a single Streamlit app (`app.py`) with 10 tab modules, 7 utility modules, and a custom dark theme (navy/gold, matching the Simple Balance brand). Every tab is a standalone module in `tabs/` and every backend service is abstracted in `utils/`.

**App Shell (`app.py`):**
- Custom CSS with dark gradient background (#0a0a1a base), gold accents (#FFC000), purple code highlights (#a78bfa)
- Session state tracking: query count, token usage (in/out), session start timestamp
- Live API status bar at the top showing green/red dots for Azure OpenAI, Replicate, Dolby.io
- Footer with session stats and J.A.W. branding
- All tabs render via imported `render()` functions from tab modules

---

### Tab 1: DJ Command (`tabs/tab_jaw.py`)

**Purpose:** AI-powered DJ advisor and energy flow guardian. The brain of the DJ operation.

**Features:**
- **Chat Interface:** Full conversational AI via Azure OpenAI with a deeply engineered system prompt
- **Beatport Search Panel:** Search tracks by query with BPM range slider (80-160), returns title, artist, BPM, key, energy rating, label, genre
- **Harmonic Key Checker:** Select two keys from dropdown, checks Camelot wheel compatibility (same key, relative major/minor, adjacent keys), warns on risky mixes
- **Energy Scale Reference:** Visual ASCII energy scale 1-6, with three set templates (Standard 2hr, Journey, Chill)

**System Prompt Engineering (JAW_SYSTEM_PROMPT):**
This is the most detailed prompt in the application. It encodes:
- **Energy Flow Rules:** Max energy jump +2 per track (hard stop), max drop -1 per track (warn unless intentional), peak duration 3-5 tracks max (flag after 5), opening energy 2-3 max, closer energy 4-5 target
- **BPM Rules:** Max BPM jump +/-8 (warn), +/-15 allowed with harmonic key match, genre shift requires 2-track bridge
- **Repetition Rules:** Same artist min 5 tracks apart, same track once per set, same key max 3 consecutive
- **Energy Scale (1-6):** Ambient, Chill, Warm, Build, Peak, Full Send
- **Set Templates:** Standard 2-Hour, Journey (Emotional Arc), Chill Session
- **Mood Profiles:** Chill (1-3, 80-110 BPM), Deep (3-4, 118-124), Driving (4-5, 125-132), Euphoric (5-6, 128-138), Dark (4-6, 130-145), Emotional (3-5, 115-130)
- **Track Suggestion Format:** Structured output with track, artist, BPM, key, energy bar, mood tag, reasoning, mix note
- **Energy Alert Format:** Structured warnings for rule violations
- **Key Artists:** Afterlife label (Colyn, Tale of Us), Upercent, Township Rebellion, Glowal, Brunello, Lane 8, Tim Engelhardt, Philip Bader
- **Prohibitions:** Never crash 5-6 to 1-2 without warning, never repeat artist within 5 tracks, never open above 3, never stack 6+ peaks without suggesting a valley, never ignore genre shift

**API Dependencies:** Azure OpenAI (chat), Beatport API v4 (search, falls back to mock data)

---

### Tab 2: Discovery (`tabs/tab_discovery.py`)

**Purpose:** Music discovery and breaking artist scouting. Mood-based, not genre-based.

**Features:**
- **Chat Interface:** Conversational AI for mood-based music discovery
- **Trending Panel:** Select genre tag (electronic, melodic techno, deep house, progressive house, indie, hip-hop, alternative, soul), loads top tracks from Last.fm with play counts
- **Artist Lookup:** Search any artist, returns listeners, play count, tags, and bio excerpt
- **Quick Moods:** One-click buttons for "Need to release", "Need to land", "Missing mom", "Brotherhood", "Working/focus", "Decompress" -- each auto-sends a curated prompt to the AI

**System Prompt Engineering (DISCOVERY_SYSTEM_PROMPT):**
Deeply personal. Encodes Peter's musical arc and relationships:
- **Peter's Arc:** 5:3666 (Hotel Diablo darkness) to sun to me (found the light). Demons to dawn at 46.
- **Core Artists & Why:** 13 artists with reasons (MGK = same darkness-to-light journey, Blue October = wrote the Wilson brothers' story, Glowal = the Sinton.ia origin artist, etc.)
- **Key Relationships:** Jimmy = "My Blood" (Twenty One Pilots), Gladys = "sun to me" (MGK), Mom = Phantasma playlist (Fleetwood Mac, Meat Loaf, Stevie Nicks), Gian Lucca = "The Best Part of Life" (SAINt JHN)
- **Mood Matching Table:** 7 moods with directions and example artists
- **Nightly Decompress Sequence:** 5-track ritual (070 Shake > Sampha > Phantasma track > My Blood/For My Brother > Mike Posner)
- **Breaking Artist Criteria:** Under 50K monthly listeners, 200%+ growth in 3 months, unique sound, authentic

**API Dependencies:** Azure OpenAI (chat), Last.fm API (trending, artist lookup, falls back to curated mock data featuring Peter's actual favorite artists)

---

### Tab 3: AI Mastering (`tabs/tab_mastering.py`)

**Purpose:** Real audio mastering using Spotify's Pedalboard library. Upload a track, apply mastering chain, download the result.

**Features:**
- **File Upload:** Accepts mp3, wav, flac, aiff, m4a
- **Audio Analysis:** BPM detection, key detection, loudness (RMS dB), peak dB via librosa
- **5 Mastering Presets:**
  - Club / PA System: Punchy, loud, clear
  - Streaming (-14 LUFS): Spotify/Apple optimized
  - Demo Master: Balanced for label submission
  - mau5trap Dark: Heavy lows, rolled highs
  - Vinyl: Controlled bass, warm compression
- **Fine-Tune Controls:** Extra gain slider (-6 to +6 dB), export format (WAV/FLAC)
- **Before/After Comparison:** Shows loudness metrics before and after mastering
- **Individual Effects Panel:** 8 effects with per-effect parameters:
  - Compressor (threshold, ratio)
  - Reverb (room size, wet)
  - Delay (time, feedback)
  - Chorus
  - High-pass filter (cutoff Hz)
  - Low-pass filter (cutoff Hz)
  - Limiter
  - Gain (dB)
- **Mastering Reference Panel:** Displays all mau5trap mastering presets with target LUFS, compression settings, limiter settings
- **EQ Profile Reference:** 5 profiles (Dark Atmospheric, Bright Lead, Sub Bass, Vocal Presence, Flat Reference)
- **Dolby.io Status:** Optional cloud mastering integration (currently not configured -- enterprise signup required)

**Audio Processing Chain (from `utils/audio_engine.py`):**
The mastering chain is: High-pass filter > Low shelf EQ > High shelf EQ > Compressor > Makeup gain > Brickwall limiter. All implemented via Spotify Pedalboard (real DSP, not simulation).

**API Dependencies:** Pedalboard (local DSP), librosa (analysis), Dolby.io (optional cloud mastering, not configured)

---

### Tab 4: Stem Separation (`tabs/tab_stems.py`)

**Purpose:** Separate any track into vocals, drums, bass, and other using Meta's Demucs model.

**Features:**
- **File Upload:** Accepts mp3, wav, flac, aiff
- **Audio Analysis:** BPM, key, duration before separation
- **Stem Options:** 2 stems (vocals/instrumental) or 4 stems (vocals/drums/bass/other)
- **URL-Based Separation:** Provide a direct URL to an audio file for separation
- **Per-Stem Output:** Each stem gets its own expandable section with audio player and download link
- **Use Case Guides:** Remix prep, mashup creation, acapella extraction, practice/analysis
- **How It Works:** 4-step explanation of the Demucs pipeline

**Technical:** Demucs v4 (Meta) runs on Replicate GPU cloud. Audio must be URL-accessible for processing. Local upload requires intermediate cloud storage (S3/GCS) in production.

**API Dependencies:** Replicate (Demucs model `cjwbw/demucs:latest`), librosa (optional pre-analysis)

---

### Tab 5: AI Generation (`tabs/tab_generation.py`)

**Purpose:** Generate music from text descriptions (MusicGen) and create MIDI patterns programmatically.

**Three Modes:**

**Mode 1: AI Audio Generation (MusicGen)**
- Text-to-music via Meta's MusicGen on Replicate
- 3 model tiers: Large (best quality, ~30s max), Medium (faster), Small (fastest)
- Controls: Duration (5-30 sec), creativity/temperature (0.5-1.5), CFG prompt adherence (1-10)
- 5 built-in prompt presets: mau5trap Progressive, TESTPILOT Techno, Melodic Breakdown, Deep House Groove, Ambient Intro
- Post-generation analysis: detected BPM, key, loudness

**Mode 2: MIDI Generation**
- **AI MIDI (Text-to-MIDI):** Describe music in text, Azure OpenAI generates ABC notation, music21 converts to MIDI file. Configurable BPM and model.
- **Chord Progression Generator:** Select root note (12 options), scale (minor, major, dorian, phrygian), chord progression (from mau5trap presets or custom). Generates downloadable MIDI.
- **Drum Pattern Generator:** 5 styles (progressive_house, techno, deep_house, breakbeat, testpilot), configurable BPM and bar count. Generates downloadable MIDI.
- **Bassline Generator:** Select root note, BPM. Generates sidechain-style bassline with rests. Downloadable MIDI.
- All MIDI is DAW-compatible (Ableton, FL Studio, Logic).

**Mode 3: mau5trap Templates**
- One-click genre templates with all parameters pre-configured
- 3 templates: Progressive House (128 BPM, Am), TESTPILOT Techno (132 BPM, Dm), Melodic Deep (122 BPM, Em)
- Each template generates a full MIDI stack: chords + drums + bass as separate downloadable MIDI files

**API Dependencies:** Replicate (MusicGen), Azure OpenAI (ABC notation generation), pretty_midi (MIDI creation), music21 (notation parsing)

---

### Tab 6: Events Radar (`tabs/tab_festivals.py`)

**Purpose:** Track upcoming shows, festivals, and events. Filter by city and artist.

**Features:**
- **Event Search:** Select city (Miami, LA, NY, Chicago, Las Vegas, Ibiza, Berlin, Amsterdam), days ahead (7-180), optional mau5trap-only filter
- **Artist Tracker:** Add/remove tracked artists. Default tracked: deadmau5, REZZ, No Mana, Colyn, Tale of Us, Anyma, Lane 8, Adam Beyer, Township Rebellion
- **Artist Event Lookup:** Search shows for any artist via Bandsintown
- **mau5trap Roster Display:** 20 artists (deadmau5, REZZ, No Mana, BlackGummy, Attlas, Notaker, Rinzen, Morgin Madison, Lamorn, Bensley, i_o, Tommy Trash, Feed Me, Grabbitz, Matt Lange, PEEKABOO, Gallya, Speaker Honey, Sian, HNTR)
- **2026 Festival Calendar:** 15 curated major festivals with dates, cities, genres, and website links:
  - Ultra Miami (Mar 27-29), Coachella (Apr 10-19), EDC Las Vegas (May 15-17), Movement Detroit (May 23-25), Sonar Barcelona (Jun 18-20), Tomorrowland (Jul 17-26), ADE Amsterdam (Oct 14-18), III Points Miami, Awakenings Amsterdam, Time Warp Mannheim, Drumcode Festival Amsterdam, Creamfields UK, Burning Man Nevada, HARD Summer LA, Afterlife Voyage Ibiza
- **Event Advisor Chat:** AI-powered event recommendations
- **Event Tagging:** Events with tracked artists get [TRACKED] tag, mau5trap roster events get [mau5trap] tag

**API Dependencies:** EDMTrain API (event search, falls back to curated mock events), Bandsintown API (artist events, requires key), Azure OpenAI (event advisor chat)

---

### Tab 7: Set Builder (`tabs/tab_setbuilder.py`)

**Purpose:** Track-by-track DJ set planner with energy flow visualization and harmonic compatibility checking.

**Features:**
- **Track Entry Form:** Track name, artist, BPM (60-200), key (25 key options), energy (1-10 scale), transition notes
- **Current Set Display:** Numbered tracklist with BPM, key (with Camelot code), energy progress bar, remove button per track
- **Energy Flow Chart (Plotly):** Gold line chart showing energy curve across the set, track labels on hover
- **BPM Transition Chart (Plotly):** Purple bar chart showing BPM per track position
- **Harmonic Compatibility Analysis:** Automatic checks for:
  - Energy jumps greater than +2 (warning)
  - Energy drops greater than -1 (warning)
  - BPM jumps greater than 8 (warning)
  - Key clashes (non-Camelot-compatible transitions)
  - Opening energy too high (above 3)
- **Set Duration Calculator:** Estimates total set duration based on track count (5.5 min avg per track)
- **3 Preset Sets:**
  - Opening Set (60min): 6 tracks, energy 2-5-3
  - Peak Time (90min): 8 tracks, energy 4-8-4
  - After Hours (120min): 8 tracks, energy 2-6-1
- **AI Suggestions:** Send full tracklist to AI for reordering and improvement suggestions
- **Export:** Download setlist as markdown file
- **Key Reference Panel:** Camelot wheel explanation

**API Dependencies:** Azure OpenAI (AI suggestions), plotly (charts), audio_engine (Camelot functions)

---

### Tab 8: Mix Archive (`tabs/tab_archive.py`)

**Purpose:** Catalog, search, filter, and annotate the J.A.W. mix collection.

**16 Archived Mixes:**

| Title | Mood | Energy | BPM Range | Tags |
|-------|------|--------|-----------|------|
| AUG 25 Stream | Driving | 4 | 120-128 | house, stream |
| Back Pain | Deep | 3 | 118-124 | deep, melodic |
| Crazy Storm | Euphoric | 5 | 124-132 | progressive, peak |
| Final Headgear | Dark | 4 | 122-130 | techno, dark |
| Here with you guys | Emotional | 3 | 118-126 | melodic, emotional |
| Let me think | Deep | 3 | 116-124 | deep, minimal |
| Letting it Go | Emotional | 4 | 120-128 | melodic, progressive |
| Little Behind | Chill | 2 | 112-120 | chill, ambient |
| Mommy Night out | Driving | 4 | 122-130 | house, driving |
| No More pacifier | Deep | 3 | 118-126 | deep, house |
| Prince of Darkness | Dark | 5 | 126-134 | dark, techno |
| Rainy afternoons | Chill | 2 | 110-118 | chill, ambient, downtempo |
| REAL AMERICAN | Euphoric | 5 | 126-136 | progressive, euphoric |
| So Daddy | Emotional | 3 | 118-124 | melodic, emotional |
| Thanks for having me | Emotional | 3 | 116-124 | melodic, emotional |
| Werid Crowd | Driving | 4 | 122-130 | house, driving |

**Context:** Jimmy (VJ Wilson) DJs through headphones because Liam (3) and Logan (2) are sleeping. Each mix title tells a story of what was happening in his life when he recorded it.

**Features:**
- **Filters:** Mood multi-select (6 moods), energy range slider (1-6), text search (title or tags)
- **Stats Panel:** Mood distribution breakdown, average energy across all mixes
- **Mix Details:** Expandable cards with full metadata, audio playback (if local file exists), per-mix notes/comments stored in session state
- **Audio Analyzer:** Upload any mix for BPM, key, loudness, duration analysis
- **Archive AI Chat:** Ask questions about the collection, get mix recommendations

**Mix File Locations (multiple backup copies):**
- `C:\Users\GCTII\Desktop\mixes\` (16 mixes)
- `C:\Users\GCTII\Proton Drive\dkgianelli\My files\Simple_Balance\Jimmy_Mixes\`
- `C:\Users\GCTII\Downloads\Jimmy_Temp\`
- `C:\Users\GCTII\.claude\Personal\Music\Jimmy_Mixes\`

**API Dependencies:** Azure OpenAI (archive chat), librosa (audio analysis)

---

### Tab 9: Producer Tools (`tabs/tab_producer.py`)

**Purpose:** Production reference analysis, music theory tools, drum grid visualization, and AI production advisor.

**4 Sub-Tabs:**

**Sub-Tab 1: Reference Analyzer**
- Upload reference track (mp3/wav/flac)
- Full analysis: BPM, key, loudness (dB), peak (dB), duration, brightness (Hz), Camelot code, compatible keys
- Waveform visualization (Plotly, gold line chart)
- Frequency spectrum visualization (Plotly, purple line chart, logarithmic frequency axis)
- AI reference analysis by track name (describe a track, get production insights)

**Sub-Tab 2: Scale/Key Helper**
- Select root note (12 options) and scale (major, minor, dorian, phrygian, mixolydian, harmonic_minor, melodic_minor)
- Displays all notes in the scale
- Camelot wheel lookup with compatible key list
- Common mau5trap progressions reference:
  - mau5trap Classic: i - VI - III - VII
  - Strobe Style: i - iv - VI - V
  - Dark Drive: i - iv - v - i
  - Euphoric Lift: i - III - VII - VI
  - TESTPILOT Minimal: i - i - iv - i

**Sub-Tab 3: Drum Grid**
- Visual 16-step drum grid display (X for hit, . for rest)
- 5 pattern styles: progressive_house, techno, deep_house, breakbeat, testpilot
- Configurable BPM and bar count
- Generate downloadable MIDI from any displayed pattern

**Sub-Tab 4: Production AI**
- Full chat interface with production-focused system prompt
- Covers chord progressions, sound design, mixing, arrangement, production workflow
- Speaks in mau5trap/deadmau5/TESTPILOT context

**API Dependencies:** Azure OpenAI (production AI, reference analysis), librosa/Pedalboard (audio analysis), pretty_midi (MIDI generation), plotly (visualizations), mau5trap_presets (progression reference)

---

### Tab 10: Dashboard (`tabs/tab_dashboard.py`)

**Purpose:** Session overview, API status monitoring, and mau5trap submission checklist.

**Features:**
- **Session Metrics:** Total queries, tokens used, set tracks count, mixes archived
- **mau5trap Submission Checklist:** 5 checkboxes with progress bar:
  1. Track mixed to -6dB headroom
  2. Mastered to streaming specs (-14 LUFS)
  3. Best 20-second clip identified
  4. Track info filled (title, BPM, key, genre)
  5. Submitted via demos@mau5trap.com or LabelRadar
- **API Status Panel:** Green/red status for all 6 APIs (Azure OpenAI, Replicate, Dolby.io, Last.fm, EDMTrain, Bandsintown)
- **Activity Feed:** Recent platform activity log
- **Quick Links:** Tab directory for navigation

**API Dependencies:** Streamlit secrets (status checks)

---

### Utility Modules

**`utils/ai_client.py` - Azure OpenAI Wrapper**
- AzureOpenAI client with configurable endpoint, key, model (default gpt-4o)
- API version: 2024-12-01-preview
- Token tracking: prompt_tokens and completion_tokens accumulated in session state
- Default temperature: 0.3

**`utils/apis.py` - External API Integrations**
- EDMTrain: Event search by city/state with mock fallback (5 curated events)
- Bandsintown: Artist event lookup (requires API key, no fallback)
- Last.fm: Trending tracks by tag, artist info lookup with mock fallback (8 curated tracks from Peter's favorites)
- MusicBrainz: Recording/artist/release search (no API key required, just user agent)
- Beatport v4: Track search by query/genre/BPM with mock fallback (6 curated tracks)

**`utils/audio_engine.py` - Pedalboard DSP Engine**
- Audio loading/saving via Pedalboard AudioFile or soundfile
- Full mastering chain: HP filter > Low shelf > High shelf > Compressor > Gain > Limiter
- Individual effects: sidechain compression, EQ (parametric), reverb, compression, limiter
- Audio analysis via librosa: BPM detection (beat_track), key detection (chroma_cqt with Krumhansl-Schmuckler profiles), loudness (RMS to LUFS approximation), peak dB, duration, sample rate
- Waveform and frequency spectrum data extraction for visualization
- Camelot wheel functions: key_to_camelot(), get_compatible_camelot(), are_keys_compatible()
- Full mock fallback when dependencies are missing

**`utils/replicate_client.py` - Replicate API Client**
- MusicGen generation: text-to-audio with model selection (large/medium/small), duration, temperature, top_k, top_p, CFG, output format (wav), peak normalization
- Demucs stem separation: 2 or 4 stem modes, returns per-stem URLs
- Async prediction polling: configurable poll interval and timeout (default 5min)
- Full mock fallback for offline development

**`utils/dolby_client.py` - Dolby.io Media API Client**
- Upload URL generation for Dolby.io storage
- File upload to Dolby.io
- Cloud mastering with profile selection and loudness control
- Audio enhancement (noise reduction, dynamics)
- Media analysis (loudness, noise, clipping detection)
- Download URL retrieval
- Job polling with configurable timeout
- Full mock fallback (not currently configured -- enterprise signup required)

**`utils/midi_engine.py` - MIDI Generation Engine**
- Note/scale utilities: 12 notes, 7 scale types (major, minor, dorian, phrygian, mixolydian, harmonic_minor, melodic_minor)
- Chord building: major, minor, diminished, sus2, sus4, dominant 7th, minor 7th
- AI MIDI generation: Text prompt > Azure OpenAI > ABC notation > music21 parsing > MIDI file
- Chord progression generator: Configurable root, scale, numeral progression, BPM, bars per chord, velocity, octave
- Bassline generator: Sidechain-style pattern with rests, configurable root/BPM/octave
- Drum pattern generator: 5 styles with 16-step grid patterns, configurable BPM/bars/velocity per drum type
- MIDI-to-audio conversion via FluidSynth (if available)
- General MIDI drum mapping: kick=36, snare=38, closed_hat=42, open_hat=46, clap=39

**`utils/mau5trap_presets.py` - Production Presets Library**
- 5 BPM presets (progressive_house, testpilot, deep_house, melodic_techno, electro_house)
- 4 key preset groups (mau5trap common, deadmau5 favorites, all minor, relative majors)
- 3 mastering presets with full EQ/compression/limiter chains (mau5trap club, streaming, demo)
- 4 sidechain presets (pump, subtle, off, testpilot slam)
- 5 EQ profiles (dark atmospheric, bright lead, sub bass, vocal presence, flat reference)
- 5 chord progressions (mau5trap classic, strobe, dark drive, euphoric lift, testpilot minimal)
- 3 genre templates with complete production settings (progressive_house, testpilot_techno, melodic_deep)

---

## Current State

**Deployed:** Yes, on Streamlit Cloud
**Python Version:** Pinned to 3.10 for Streamlit Cloud compatibility
**Branch:** main (7 commits)

### API Status (as of Feb 24, 2026)

| API | Status | Notes |
|-----|--------|-------|
| Azure OpenAI | Configured | Key from casa-companion .env, model: gpt-4o |
| Replicate | Configured | Token active, MusicGen + Demucs ready |
| Dolby.io | NOT configured | Enterprise signup only, skipped |
| Last.fm | NOT configured | Falls back to curated mock data |
| EDMTrain | NOT configured | Falls back to curated mock events |
| Bandsintown | NOT configured | No fallback, returns empty |
| Beatport v4 | NOT configured | Falls back to curated mock results |
| MusicBrainz | Ready | No key required, just user agent header |

### What Works Right Now
- All 10 tabs render and are functional
- AI chat works in DJ Command, Discovery, Events Radar, Mix Archive, Producer Tools (5 chat interfaces)
- Audio mastering chain works locally with Pedalboard (if dependencies installed)
- MIDI generation works (chord progressions, drum patterns, basslines, AI text-to-MIDI)
- Energy flow visualization works in Set Builder (Plotly charts)
- Mix archive is fully cataloged and searchable
- mau5trap submission checklist is functional
- Custom dark theme renders correctly

### What Needs Work
- Audio file upload to cloud storage for Replicate stem separation (currently requires pre-uploaded URL)
- Last.fm, EDMTrain, Bandsintown API keys need configuration for live data
- Dolby.io integration is blocked by enterprise signup
- No user authentication or persistence between sessions
- No database (everything is session state or hardcoded)
- No file storage for generated/mastered audio (ephemeral only)

---

## Version History

| Version | Commit | Date | What Changed |
|---------|--------|------|--------------|
| v1.0 | `75347c3` | Feb 2026 | Initial commit: 10 tab modules, basic structure |
| v1.5 | `3470764` | Feb 2026 | Streamlit Cloud config: dark theme + deploy settings |
| v2.0 | `89f3718` | Feb 2026 | Rebuild core infrastructure as production-grade toolkit |
| v2.0 | `590e6b4` | Feb 2026 | Rewrite all 10 tabs with real API integrations |
| v2.0.1 | `710830d` | Feb 2026 | Fix syntax errors: broken string literals, invalid tag expressions |
| v2.0.2 | `5f0bd45` | Feb 2026 | Fix emoji rendering: st.success/st.warning instead of markdown emoji |
| v2.0.3 | `1817428` | Feb 2026 | Pin Python 3.10 for Streamlit Cloud compatibility |

---

## Phase Rollout Plan (DETAILED)

### v2.0 - Current Production Suite (COMPLETE)

**What it is:** The full music AI production suite as built today. 10 tabs, real APIs, real audio processing.

**Target User:** Peter and Jimmy Wilson (internal use, portfolio piece, proof of concept)

**Value:** Demonstrates that one person can build a professional-grade music production platform with AI. This is the foundation everything else builds on.

---

### v2.5 - API Completion + Polish

**Timeline:** 1-2 weeks
**Effort:** Low (configuration + minor UI work)

**Deliverables:**

1. **Last.fm API Integration**
   - Sign up at last.fm/api, get API key
   - Configure LASTFM_API_KEY in Streamlit secrets
   - Discovery tab trending will pull real data instead of mocks
   - Artist lookup will return real listener counts, bio, tags
   - Estimated time: 30 minutes

2. **EDMTrain API Integration**
   - Sign up at edmtrain.com/api, get client key
   - Configure EDMTRAIN_API_KEY in Streamlit secrets
   - Events Radar will pull real upcoming events by city
   - Estimated time: 30 minutes

3. **Bandsintown API Integration**
   - Register app at artists.bandsintown.com, get app ID
   - Configure BANDSINTOWN_APP_ID in Streamlit secrets
   - Artist event lookup will return real upcoming shows
   - Estimated time: 30 minutes

4. **Cloud Audio Storage (S3 or Supabase)**
   - Add temporary file upload to cloud storage (S3, GCS, or Supabase Storage)
   - Enables direct file upload for stem separation (currently requires URL)
   - Enables persistent storage for mastered/generated audio files
   - Estimated time: 4-6 hours

5. **UI Polish**
   - Loading states and progress indicators for long-running operations
   - Error handling improvements (user-friendly messages)
   - Mobile responsiveness improvements
   - Favicon and Open Graph meta tags
   - Estimated time: 3-4 hours

6. **Spotify API Integration (Optional)**
   - Spotify Web API for track metadata, audio features (danceability, energy, valence)
   - Would enhance Discovery tab with real-time track characteristics
   - OAuth flow complexity makes this a stretch goal
   - Estimated time: 8-10 hours

**Total v2.5 Estimate:** 1-2 weeks part-time

---

### v3.0 - DemoReady (Label Submission Tool)

**Timeline:** 2-3 weeks
**Effort:** Medium
**Revenue Potential:** Strongest play from existing platform. 2-3 week build on what already exists.

**What it is:** An AI-powered tool that helps independent producers prepare and submit demos to record labels. It takes the existing mastering, analysis, and mau5trap submission checklist and turns it into a guided workflow product.

**Why it wins:**
- No tool like this exists. Producers submit demos blind.
- Labels get thousands of submissions. Most are poorly prepared.
- DemoReady bridges the gap: it ensures every submission meets label standards before it's sent.
- Peter knows the DJ/promoter side. He knows what labels look for because he was on the other end of the table.

**Feature Set:**

1. **Label Database**
   - Curated database of electronic music labels with submission requirements
   - Start with 20-30 labels: mau5trap, Afterlife, Drumcode, Anjunadeep, This Never Happened, Moon Harbour, Steyoyoke, Diynamic, Kompakt, Innervisions, etc.
   - Per-label data: submission email, LabelRadar link, preferred format (WAV/MP3), loudness target, genre focus, response time, acceptance rate estimate
   - Filterable by genre, submission method, and acceptance difficulty

2. **Track Prep Wizard**
   - Step-by-step guided workflow:
     - Step 1: Upload your track
     - Step 2: AI analyzes BPM, key, loudness, peak, dynamics
     - Step 3: AI compares against target label's requirements
     - Step 4: Auto-apply mastering preset for label's specs (or manual adjust)
     - Step 5: Generate 20-second highlight clip (AI selects the strongest section)
     - Step 6: Generate submission email template with track metadata
   - Per-label customization (e.g., mau5trap wants -6dB headroom, Afterlife wants -14 LUFS streaming master)

3. **Submission Tracker**
   - Track which demos were sent to which labels
   - Status tracking: Drafted, Submitted, Follow-Up Sent, Responded, Accepted, Rejected
   - Date tracking with follow-up reminders (industry standard: follow up after 4-6 weeks)
   - Notes per submission

4. **AI Demo Critique**
   - Upload a track, AI provides production feedback
   - Compares to reference tracks from the target label's catalog
   - Identifies strengths and areas for improvement
   - "Would this fit on [label]?" analysis

5. **Email Template Generator**
   - AI generates label-appropriate submission emails
   - Includes track metadata, artist bio snippet, streaming links
   - Personalized per label (references recent releases, label style)

**Technical Requirements:**
- Database: Supabase or SQLite for label database and submission tracking
- Authentication: Streamlit login or Supabase Auth (needed for persistent user data)
- Email: Optional SMTP integration for sending directly, or copy-to-clipboard
- Existing foundation: Mastering engine, audio analysis, AI chat, mau5trap presets all already built

**Pricing:** Free tier (3 submissions/month) + Pro tier ($9/month unlimited)

---

### v3.5 - SetFlow AI (DJ Set Planner)

**Timeline:** 3-4 weeks (builds on existing Set Builder tab)
**Effort:** Medium-High

**What it is:** An intelligent DJ set planning tool that takes the existing Set Builder and turns it into a full set management platform with music library integration, auto-ordering, and live set tracking.

**Why it wins:**
- Rekordbox and Traktor are DJ software, not set planners. They don't think about energy flow.
- SetFlow AI is the thinking layer that sits on top of your music library and plans the set for you.
- Peter's energy flow rules (encoded in the J.A.W. system prompt) are genuinely valuable DJ knowledge.

**Feature Set:**

1. **Music Library Integration**
   - Import track library from CSV, Rekordbox XML, or manual entry
   - Per-track metadata: title, artist, BPM, key, energy, mood, tags, duration
   - Bulk audio analysis: upload folder, auto-detect BPM/key for all tracks

2. **AI Auto-Ordering**
   - Given a track selection, AI orders them for optimal energy flow
   - Respects all energy rules (max +2 jump, max -1 drop, no repeat artist within 5)
   - Respects harmonic compatibility (Camelot wheel)
   - Generates transition notes per track pair
   - Multiple ordering modes: Standard 2hr, Journey, After Hours, Custom

3. **Set Templates + Sharing**
   - Save sets as reusable templates
   - Export as PDF, markdown, or Rekordbox-compatible playlist
   - Share sets via link (public URL)

4. **Live Set Mode**
   - Real-time set tracker during a live DJ performance
   - Mark current track, advance through set
   - AI suggests next track from remaining pool based on current energy/BPM/key
   - Timer per track, total set duration countdown

5. **Crate Builder**
   - AI suggests tracks to add to your set based on gaps in energy/mood coverage
   - "You need a bridge track between track 5 and 6. Here are suggestions."
   - Integration with Beatport/Spotify for discovery

**Technical Requirements:**
- Database: User library persistence (Supabase)
- File parsing: Rekordbox XML parser, CSV import
- Batch audio analysis: Queue system for analyzing multiple files
- Real-time features: WebSocket or polling for live set mode

**Pricing:** Free tier (1 saved set) + Pro tier ($14/month unlimited sets)

---

### v4.0 - Club/Promoter Tools

**Timeline:** 4-6 weeks
**Effort:** High

**What it is:** The promoter side of the platform. Ticket selling, guest list management, event promotion, venue analytics. This is where Peter's real-world experience as a club promoter becomes the product.

**Why it wins:**
- Peter ran clubs and promoted events for years. He knows the pain points: guest list management is always a mess, ticket reconciliation is manual, and promoter tools are either overbuilt enterprise software or spreadsheets.
- No tool combines DJ set planning with event promotion. SetFlow AI + Club Tools = the full DJ/promoter stack.

**Feature Set:**

1. **Event Creator**
   - Create events with venue, date, lineup, ticket tiers, capacity
   - Event landing page generation (shareable URL)
   - Flyer/social media asset generation with AI

2. **Guest List Management**
   - Digital guest list with tiers: VIP, Guest, Plus One, Comp
   - QR code check-in at the door
   - Real-time capacity tracking
   - Guest list sharing with co-promoters
   - Export to CSV/PDF

3. **Ticket System (Basic)**
   - Stripe integration for ticket sales
   - Tiered pricing (Early Bird, General, VIP, Table)
   - Promo codes and discount management
   - Sales dashboard with real-time revenue tracking
   - QR code tickets with scan validation

4. **Promoter Analytics**
   - Revenue per event, per tier
   - Guest list conversion rate (invites vs. shows)
   - Repeat attendee tracking
   - Best-selling time windows (early vs. late buyers)

5. **DJ Booking Manager**
   - Track DJ bookings, fees, riders
   - Contract template generation
   - Payment tracking (deposit, balance, post-event)

**Technical Requirements:**
- Payment processing: Stripe Connect
- QR code generation and scanning
- Database: Full relational DB (Supabase or managed PostgreSQL)
- Authentication: Required (multi-user, roles: promoter, door staff, DJ)
- Hosting: Likely needs migration from Streamlit to Next.js or Flask for the ticketing features

**Pricing:** Free tier (1 event/month, 50 guest list) + Promoter tier ($29/month) + Venue tier ($79/month)

---

### v5.0 - Simple Balance Pro SaaS

**Timeline:** 8-12 weeks (from v4.0 completion)
**Effort:** Very High

**What it is:** The full SaaS product. Simple Balance Pro wraps everything above into a subscription platform with user accounts, persistent data, team features, and a polished UI.

**Two Tiers:**

**Hobbyist ($19/month)**
- All DemoReady features (unlimited submissions)
- SetFlow AI (5 saved sets)
- Mix Archive (personal mix library, 10 mixes)
- AI Mastering (10 masters/month)
- Stem Separation (5 separations/month)
- AI Generation (10 generations/month)
- Producer Tools (full access)
- Music Discovery (full access)
- Events Radar (full access)

**Pro ($49/month)**
- Everything in Hobbyist
- Unlimited sets, mixes, masters, separations, generations
- Club/Promoter Tools (full access)
- Guest List Management (unlimited events)
- Ticket System (5% platform fee on sales)
- DJ Booking Manager
- Priority AI processing (faster queue)
- Custom mastering presets (save your own)
- Team accounts (invite collaborators)
- API access (integrate with your own tools)
- White-label event pages

**Annual Pricing:**
- Hobbyist: $190/year ($15.83/month, save $38)
- Pro: $490/year ($40.83/month, save $98)

**Technical Requirements:**
- Full migration from Streamlit to production web framework (Next.js frontend + FastAPI backend recommended)
- Authentication: Supabase Auth or Auth0
- Database: Supabase (PostgreSQL)
- File storage: S3 or Supabase Storage
- Payment: Stripe Billing for subscriptions + Stripe Connect for ticket sales
- CDN: CloudFront or Vercel Edge for audio file delivery
- Queue system: Redis + Celery for async audio processing
- Monitoring: Sentry + analytics

---

## Revenue Model

### Revenue Streams

| Stream | Source | Timeline |
|--------|--------|----------|
| DemoReady Subscriptions | $9/mo per user | v3.0 (Month 2-3) |
| SetFlow AI Subscriptions | $14/mo per user | v3.5 (Month 4-5) |
| Simple Balance Pro | $19-49/mo per user | v5.0 (Month 8-12) |
| Ticket Platform Fees | 5% per ticket sold | v4.0 (Month 6-8) |
| AI Processing Credits | Pay-per-use for heavy users | v5.0 |

### Cost Structure

| Cost | Monthly Estimate | Notes |
|------|-----------------|-------|
| Azure OpenAI | $20-50 | GPT-4o usage across chat interfaces |
| Replicate | $10-30 | MusicGen + Demucs per-generation |
| Supabase | $25 | Pro plan for DB + Auth + Storage |
| Streamlit Cloud | $0 | Free tier until migration |
| Vercel/Railway (post-migration) | $20 | Hosting |
| Stripe | 2.9% + $0.30 per transaction | Payment processing |
| Domain + SSL | $15/year | simplebalancemusic.com |
| **Total Overhead** | **~$100-150/month** | Before any revenue |

### Break-Even Analysis
- At $9/mo DemoReady: ~15 paying users covers costs
- At $19/mo Hobbyist: ~8 paying users covers costs
- At $49/mo Pro: ~3 paying users covers costs
- Target: 50 paying users within 6 months of launch = $950-2,450/month revenue

---

## Tech Stack

### Current Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | Streamlit | >=1.31.0 |
| **Backend** | Python | 3.10 (pinned) |
| **AI/LLM** | Azure OpenAI (GPT-4o) | API v2024-12-01-preview |
| **Music Generation** | Replicate (MusicGen Large/Medium/Small) | Meta MusicGen |
| **Stem Separation** | Replicate (Demucs v4) | Meta Demucs |
| **Audio DSP** | Spotify Pedalboard | >=0.9.0 |
| **Audio Analysis** | librosa | >=0.10.1 |
| **Audio I/O** | soundfile | >=0.12.1 |
| **MIDI** | pretty_midi + mido + music21 | Various |
| **Visualization** | Plotly | >=5.18.0 |
| **Data** | Pandas + NumPy | >=2.1.0 / >=1.26.0 |
| **Audio Manipulation** | pydub + mutagen | >=0.25.1 / >=1.47.0 |
| **HTTP** | requests | >=2.31.0 |
| **Config** | python-dotenv | >=1.0.0 |
| **Hosting** | Streamlit Cloud | Free tier |
| **Source Control** | GitHub | simplebalance89-ai org |

### Future Stack Additions (v3.0+)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Database** | Supabase (PostgreSQL) | User data, label DB, submission tracking |
| **Auth** | Supabase Auth | User accounts, sessions |
| **Storage** | Supabase Storage or S3 | Audio files, MIDI files |
| **Payments** | Stripe Billing + Connect | Subscriptions + ticket sales |
| **Frontend (v5.0)** | Next.js | Production UI migration |
| **Backend (v5.0)** | FastAPI | API layer |
| **Queue** | Redis + Celery | Async audio processing |
| **CDN** | CloudFront | Audio file delivery |
| **Monitoring** | Sentry | Error tracking |

---

## Key Files & Paths

### Repository Structure

```
C:\Claude\Work\simple-balance-music\
|-- app.py                          # Main Streamlit application (169 lines)
|-- requirements.txt                # Python dependencies (16 packages)
|-- .gitignore                      # Excludes secrets, audio files, venvs
|-- .streamlit/
|   |-- config.toml                 # Dark theme + server settings
|   |-- secrets.toml.example        # Template for API keys
|-- tabs/
|   |-- __init__.py
|   |-- tab_jaw.py                  # Tab 1: DJ Command (203 lines)
|   |-- tab_discovery.py            # Tab 2: Music Discovery (157 lines)
|   |-- tab_mastering.py            # Tab 3: AI Mastering (178 lines)
|   |-- tab_stems.py                # Tab 4: Stem Separation (147 lines)
|   |-- tab_generation.py           # Tab 5: AI Generation (291 lines)
|   |-- tab_festivals.py            # Tab 6: Events Radar (186 lines)
|   |-- tab_setbuilder.py           # Tab 7: Set Builder (247 lines)
|   |-- tab_archive.py              # Tab 8: Mix Archive (141 lines)
|   |-- tab_producer.py             # Tab 9: Producer Tools (245 lines)
|   |-- tab_dashboard.py            # Tab 10: Dashboard (100 lines)
|-- utils/
|   |-- __init__.py
|   |-- ai_client.py                # Azure OpenAI wrapper (41 lines)
|   |-- apis.py                     # External API integrations (209 lines)
|   |-- audio_engine.py             # Pedalboard DSP + librosa analysis (250 lines)
|   |-- replicate_client.py         # Replicate API (MusicGen + Demucs) (232 lines)
|   |-- dolby_client.py             # Dolby.io Media API (194 lines)
|   |-- midi_engine.py              # MIDI generation engine (315 lines)
|   |-- mau5trap_presets.py         # Production presets library (115 lines)
```

### Related Paths

| Path | What |
|------|------|
| `C:\Claude\Work\simple-balance-music\` | Main repo (local) |
| `C:\Users\GCTII\.claude\projects\C--Users-GCTII\memory\simple-balance-music.md` | State tracker |
| `C:\Users\GCTII\.claude\projects\C--Users-GCTII\memory\next-companies-research.md` | Company research |
| `C:\Users\GCTII\Desktop\mixes\` | Jimmy's mixes (primary copy) |
| `C:\Users\GCTII\Proton Drive\...\Jimmy_Mixes\` | Jimmy's mixes (cloud backup) |
| `C:\Claude\Work\next_companies_research.html` | Full research report (HTML) |

### API Keys Location
All API keys stored in Streamlit Cloud Settings > Secrets (TOML format). Local development uses `.streamlit/secrets.toml` (gitignored).

---

## Competitor Landscape

### Direct Competitors (Music AI Platforms)

| Competitor | What They Do | Price | Gap We Fill |
|-----------|-------------|-------|-------------|
| **Landr** | AI mastering, distribution, samples | $4-26/mo | No DJ tools, no set planning, no label submission workflow |
| **eMastered** | AI mastering only | $9-29/mo | Single feature. No production tools, no DJ integration |
| **iZotope Ozone** | Professional mastering plugin | $249 one-time | Desktop plugin only. No AI chat, no DJ features, no cloud |
| **BandLab** | Free DAW + social | Free | Social-focused, not production-grade. No DJ tools |
| **Splice** | Samples + plugins + rent-to-own | $8-30/mo | Sample marketplace, not a production platform. No AI |

### Adjacent Competitors (DJ Tools)

| Competitor | What They Do | Price | Gap We Fill |
|-----------|-------------|-------|-------------|
| **Rekordbox** | DJ software + library management | Free-$15/mo | Performance software, not a set planner. No AI energy flow |
| **Traktor** | DJ software | $99 one-time | Same as Rekordbox. No AI, no set intelligence |
| **Mixed In Key** | Key detection + energy analysis | $58 one-time | Key detection only. No set building, no AI advisor |
| **DJ.Studio** | AI-powered DJ mix creator | $4-12/mo | Creates auto-mixes. Not a set planner or production tool |
| **Setlist.fm** | Crowd-sourced setlist database | Free | Tracking past sets, not planning future ones |

### Adjacent Competitors (Promoter/Event Tools)

| Competitor | What They Do | Price | Gap We Fill |
|-----------|-------------|-------|-------------|
| **Eventbrite** | Ticketing platform | 3.7% + $1.79/ticket | Generic. Not built for club/DJ events specifically |
| **Dice** | Music-focused ticketing | Commission-based | Great for fans, limited for promoters. No DJ integration |
| **Resident Advisor** | Event listings + ticketing | Commission-based | Listing platform, not a promoter management tool |
| **Prism** | Nightlife guest list management | Custom pricing | Guest list only. No set planning, no production tools |

### Competitive Moat

**Nobody combines all three:** production + DJ set planning + event promotion in one platform.

The closest comparison is if you merged Landr (mastering) + Mixed In Key (harmonic analysis) + Rekordbox (library management) + Eventbrite (ticketing) + an AI advisor trained on 20+ years of DJ/promoter experience. That product does not exist. Simple Balance is building it.

**Peter's edge:** He is not a developer building a music tool. He is a DJ and promoter who learned to build software. The system prompts (especially J.A.W. DJ Command) encode real floor experience that no competitor has. The energy flow rules, the mood profiles, the transition logic -- that came from running floors, not from reading documentation.

---

*Simple Balance Music. Built by a DJ. Powered by AI. For the floor.*
