# Simple Balance Music v2.0 — Test Suite

**Product:** Simple Balance Music AI Production Suite
**Version:** 2.0 Production Edition
**Date:** February 24, 2026
**Tester:** Peter Wilson / Sinton.ia
**Lifecycle Step:** 4 of 5 (Build > Vision > Demo > **TEST** > Sign Off)

---

## Summary

| Category | Tests | Passed | Failed |
|----------|-------|--------|--------|
| DJ Command | 5 | 0 | 0 |
| Discovery | 4 | 0 | 0 |
| AI Mastering | 4 | 0 | 0 |
| Stem Separation | 3 | 0 | 0 |
| AI Generation | 3 | 0 | 0 |
| Events Radar | 2 | 0 | 0 |
| Set Builder | 4 | 0 | 0 |
| Mix Archive | 3 | 0 | 0 |
| Producer Tools | 4 | 0 | 0 |
| Dashboard | 2 | 0 | 0 |
| **TOTAL** | **34** | **0** | **0** |

---

## DJ Command (Tab 1)

| # | Category | Test Name | Input | Expected Output | Status | Notes |
|---|----------|-----------|-------|-----------------|--------|-------|
| 1 | DJ Command | AI chat responds to vibe request | Type "Give me 3 tracks for a deep melodic opening set at 120 BPM" | AI returns 3 track suggestions with artist, BPM, key, energy level (2-3 for opening), and mix notes in the TRACK SUGGESTION format | UNTESTED | |
| 2 | DJ Command | Energy alert fires on violation | Type "I want to open with a 6/6 energy banger then drop to ambient" | AI returns an ENERGY ALERT warning against opening above 3 and dropping more than -1 per track. Suggests a bridge or corrected flow | UNTESTED | |
| 3 | DJ Command | Beatport search returns results | In Quick Tools sidebar, enter "Colyn" in search box, set BPM range 118-135, click Search Beatport | Results display with track title, artist, BPM, key, energy bar, label, and genre for each result | UNTESTED | |
| 4 | DJ Command | Harmonic Key Checker validates compatible keys | Select current key "Am" and next key "C", click Check Compatibility | Shows "Compatible!" with Camelot codes 8A and 8B (relative major/minor match) | UNTESTED | |
| 5 | DJ Command | Harmonic Key Checker warns on risky mix | Select current key "Am" and next key "F#m", click Check Compatibility | Shows "Risky mix" warning with suggestion to use a bridge track | UNTESTED | |

---

## Discovery (Tab 2)

| # | Category | Test Name | Input | Expected Output | Status | Notes |
|---|----------|-----------|-------|-----------------|--------|-------|
| 6 | Discovery | Quick Mood button triggers AI recommendation | Click the "Need to release" mood button in the sidebar | AI chat receives "Find something dark, cathartic, building" and responds with track recommendations matching that mood (070 Shake, dark builds, cathartic artists) | UNTESTED | |
| 7 | Discovery | Last.fm trending loads genre results | Select "melodic techno" from Genre Tag dropdown, click Load Trending | Up to 10 tracks display with track name, artist, and play count. If Last.fm API not configured, shows graceful fallback | UNTESTED | |
| 8 | Discovery | Artist lookup returns stats and bio | Type "Glowal" in Artist Lookup, click Lookup | Artist name, listener count, play count, genre tags, and bio snippet display. If no API key, shows "No data found" info message | UNTESTED | |
| 9 | Discovery | Decompress mode runs nightly sequence | Type "Decompress mode" in the chat input | AI responds with the 5-track nightly decompress sequence: 070 Shake (release), Sampha (land), Phantasma track (mom), My Blood (brothers), Mike Posner (close) | UNTESTED | |

---

## AI Mastering (Tab 3)

| # | Category | Test Name | Input | Expected Output | Status | Notes |
|---|----------|-----------|-------|-----------------|--------|-------|
| 10 | AI Mastering | Upload and analyze audio file | Upload a .wav file via the file uploader | Audio player renders with playback. File size displays. If Pedalboard/librosa installed: BPM, Key, Loudness (dB), and Peak (dB) metrics display | UNTESTED | |
| 11 | AI Mastering | Master track with Club preset | Upload .wav, select "Club / PA System" preset, set Extra Gain to +2 dB, click Master Track | Mastering spinner runs. "Mastering complete!" message. Before vs After loudness comparison displays. Download button appears for mastered file | UNTESTED | |
| 12 | AI Mastering | Apply single reverb effect | Upload .wav, scroll to Apply Single Effect, select "reverb", set Room Size 0.7 and Wet 0.5, click Apply Effect | Processed audio player appears with reverb applied. Download button appears for the processed file | UNTESTED | |
| 13 | AI Mastering | Mastering presets display reference info | Scroll to Mastering Reference in right column, expand "mau5trap Dark" preset | Shows Target LUFS, Compression ratio and threshold, Limiter threshold, and description text | UNTESTED | |

---

## Stem Separation (Tab 4)

| # | Category | Test Name | Input | Expected Output | Status | Notes |
|---|----------|-----------|-------|-----------------|--------|-------|
| 14 | Stem Separation | Upload file and select 4-stem mode | Upload .mp3 file, select "4 stems (vocals/drums/bass/other)" radio | File loads with audio player and size display. If librosa available: BPM, Key, Duration metrics shown. 4-stem radio selected | UNTESTED | |
| 15 | Stem Separation | Separate stems with Replicate connected | Upload .mp3, select 4 stems, click Separate Stems (with REPLICATE_API_TOKEN configured) | Spinner shows "Separating stems via Demucs on Replicate..." Result shows 4 expandable sections (Vocals, Drums, Bass, Other) each with audio player and download link | UNTESTED | |
| 16 | Stem Separation | Demo mode fallback without API | Upload .mp3, click Separate Stems (no REPLICATE_API_TOKEN) | Warning: "Replicate API not configured." Demo mode shows 4 expanders (Vocals, Drums, Bass, Other) with placeholder content for each stem | UNTESTED | |

---

## AI Generation (Tab 5)

| # | Category | Test Name | Input | Expected Output | Status | Notes |
|---|----------|-----------|-------|-----------------|--------|-------|
| 17 | AI Generation | MusicGen text-to-music generation | Select AI Audio Generation mode. Enter prompt "Dark progressive house, 128 BPM, Am, rolling bass, atmospheric pads". Set duration 15s, creativity 1.0, CFG 3. Click Generate | If Replicate connected: spinner, "Generation complete!", audio player with generated music, download link, detected BPM/Key/Loudness metrics. If not connected: API warning | UNTESTED | |
| 18 | AI Generation | MIDI chord progression generator | Select MIDI Generation mode. Set Root "A", Scale "minor", select mau5trap Classic progression, BPM 128. Click Generate Chords | "Chord progression MIDI generated!" message. Download Chord MIDI button appears with .mid file | UNTESTED | |
| 19 | AI Generation | mau5trap template full stack generation | Select mau5trap Templates mode. Expand "Progressive House" template. Verify BPM, Key, Sidechain, Drums metrics display. Click Generate Full Stack | Spinner runs. "Generated progressive_house MIDI stack!" Three download buttons appear: Chords MIDI, Drums MIDI, Bass MIDI | UNTESTED | |

---

## Events Radar (Tab 6)

| # | Category | Test Name | Input | Expected Output | Status | Notes |
|---|----------|-----------|-------|-----------------|--------|-------|
| 20 | Events Radar | Search events by city with mau5trap filter | Select city "Miami", set Days Ahead to 60, check "mau5trap artists only", click Search Events | Results filtered to only show events featuring mau5trap roster artists (deadmau5, REZZ, No Mana, etc.). Each event shows date, name, artists, venue, and [mau5trap] tag | UNTESTED | |
| 21 | Events Radar | 2026 festival calendar displays correctly | Navigate to Events Radar tab without searching | "Major 2026 Festivals" section displays with 15 festivals. Each expander shows genre, location, and website link. Ultra (Mar 27-29), EDC (May 15-17), Tomorrowland (Jul 17-19) all present | UNTESTED | |

---

## Set Builder (Tab 7)

| # | Category | Test Name | Input | Expected Output | Status | Notes |
|---|----------|-----------|-------|-----------------|--------|-------|
| 22 | Set Builder | Add track and verify display | Enter Track "Oxygen Levels Low", Artist "Colyn", BPM 126, Key "Am", Energy 5, Notes "Melodic peak". Click Add to Set | Track appears in Current Set list showing: position number, bold title with artist, 126 BPM, Am with Camelot code, energy progress bar at 5/10 | UNTESTED | |
| 23 | Set Builder | Energy flow violation detection | Load "Opening Set (60min)" preset. Add a track with Energy 1 after the Energy 5 track (position 5) | Harmonic Compatibility section shows warning: "Energy drop -4 (max -1)" for the inserted track. Additional BPM and key warnings if applicable | UNTESTED | |
| 24 | Set Builder | Load preset and visualize energy chart | Click "Load: Opening Set (60min)" preset button | 6 tracks load into Current Set. Energy Flow chart renders (Plotly line chart, gold color) showing arc from 2 to 5 back to 3. BPM Transitions bar chart renders in purple | UNTESTED | |
| 25 | Set Builder | AI Suggestions analyzes full set | Load a preset, click AI Suggestions button | Spinner shows "Analyzing set..." AI returns analysis of energy flow, BPM transitions, harmonic compatibility, and specific reordering or bridge track suggestions | UNTESTED | |

---

## Mix Archive (Tab 8)

| # | Category | Test Name | Input | Expected Output | Status | Notes |
|---|----------|-----------|-------|-----------------|--------|-------|
| 26 | Mix Archive | Filter mixes by mood and energy | Select "Dark" mood filter, set Energy Range to 4-6 | Shows 2 mixes: "Prince of Darkness" (Dark, energy 5) and "Final Headgear" (Dark, energy 4). Counter shows "2/16". Stats section visible | UNTESTED | |
| 27 | Mix Archive | Search mixes by keyword | Type "daddy" in Search field | Filters to "So Daddy" mix. Expanding shows full metadata: tags (melodic, emotional), energy 3, mood Emotional, BPM range 118-124 | UNTESTED | |
| 28 | Mix Archive | Archive AI chat finds mix by description | Type "What's the most chill mix for a rainy afternoon?" in the chat | AI responds referencing "Rainy afternoons" (Chill, energy 2, 110-118 BPM) and possibly "Little Behind" (Chill, energy 2). Contextual response about Jimmy's headphone DJ sessions | UNTESTED | |

---

## Producer Tools (Tab 9)

| # | Category | Test Name | Input | Expected Output | Status | Notes |
|---|----------|-----------|-------|-----------------|--------|-------|
| 29 | Producer Tools | Reference track analysis with visualizations | Navigate to Reference Analyzer sub-tab. Upload .wav file, click Analyze | BPM, Key, Loudness, Peak, Duration, Brightness metrics display. Camelot code and compatible keys shown. Waveform chart (gold) and Frequency Spectrum chart (purple, log scale) render | UNTESTED | |
| 30 | Producer Tools | Scale/Key helper shows notes and Camelot | Navigate to Scale/Key Helper sub-tab. Select Root "A", Scale "minor" | Notes display: A - B - C - D - E - F - G. Camelot shows Am = 8A. Compatible keys listed. mau5trap chord progressions display below | UNTESTED | |
| 31 | Producer Tools | Drum grid displays 16-step pattern | Navigate to Drum Grid sub-tab. Select style "progressive_house" | 16-step grid renders with X and . markers for kick, snare, hihat, etc. BPM and Bars inputs visible. Generate MIDI button present | UNTESTED | |
| 32 | Producer Tools | Production AI chat responds to sound design question | Navigate to Production AI sub-tab. Type "How do I get that deadmau5 pluck sound from Strobe?" | AI responds with practical sound design advice referencing mau5trap production style: oscillator setup, filter settings, envelope, effects chain. Speaks in DJ-to-producer language | UNTESTED | |

---

## Dashboard (Tab 10)

| # | Category | Test Name | Input | Expected Output | Status | Notes |
|---|----------|-----------|-------|-----------------|--------|-------|
| 33 | Dashboard | Session metrics display correctly | Navigate to Dashboard tab | Four metrics display: Queries (count from session), Tokens Used (in+out total), Set Tracks (count from Set Builder), Mixes Archived (18). All render with gold values | UNTESTED | |
| 34 | Dashboard | mau5trap submission checklist tracks progress | Check 3 of 5 checklist items: "Track mixed to -6dB headroom", "Mastered to streaming specs", "Best 20-second clip identified" | Progress bar shows 3/5 complete. Remaining items unchecked. Submit info shows demos@mau5trap.com and LabelRadar link. "Ready to submit" message does NOT appear (incomplete) | UNTESTED | |

---

## Test Execution Notes

- **API Dependencies:** Tests 3, 7, 8, 11, 12, 15, 17 require live API keys (Azure OpenAI, Replicate, Last.fm, Dolby.io). Run with and without keys to verify both live and demo mode paths.
- **Audio Dependencies:** Tests 10, 11, 12, 14, 29 require librosa + pedalboard + soundfile installed. Verify graceful fallback when missing.
- **MIDI Dependencies:** Tests 18, 19, 31 require pretty_midi + music21 + mido. Verify fallback messaging.
- **Browser:** Test on Chrome (primary) and Edge. Verify dark theme renders correctly in both.
- **Mobile:** Verify layout does not break on tablet viewport. Sidebar should collapse cleanly.

---

**Status Legend:**
- **UNTESTED** — Not yet executed
- **PASS** — Works as described
- **FAIL** — Does not match expected output (document what happened in Notes)

---

*Simple Balance Music v2.0 | J.A.W. | Built with Sinton.ia*
